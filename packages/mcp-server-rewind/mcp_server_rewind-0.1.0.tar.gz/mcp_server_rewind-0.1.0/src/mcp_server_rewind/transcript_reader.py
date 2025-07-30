"""Core logic for reading and parsing Rewind transcript files."""

import os
import re
import logging
from datetime import datetime, time, date, timedelta
from pathlib import Path
from typing import List, Optional, Tuple
from zoneinfo import ZoneInfo

from .models import TranscriptSegment, TranscriptResult, TranscriptDate, TranscriptSummary

logger = logging.getLogger(__name__)


class TranscriptReader:
    """Handles reading and parsing of Rewind transcript files."""
    
    def __init__(self, base_path: str, timezone: Optional[str] = None):
        self.base_path = Path(base_path)
        self.timezone = ZoneInfo(timezone) if timezone else None
        
        # Pattern to extract timestamp from transcript filename
        # Example: d0tb6ijo6bd05l1den2g_transcript_20250531_093756_to_20250531_094410.txt
        self.transcript_pattern = re.compile(
            r'_transcript_(\d{8})_(\d{6})_to_(\d{8})_(\d{6})\.txt$'
        )
    
    def _parse_timestamp_from_filename(self, filename: str) -> Optional[Tuple[datetime, datetime]]:
        """Extract start and end timestamps from transcript filename."""
        match = self.transcript_pattern.search(filename)
        if not match:
            return None
        
        start_date, start_time, end_date, end_time = match.groups()
        
        try:
            # Parse start timestamp
            start_dt = datetime.strptime(f"{start_date}_{start_time}", "%Y%m%d_%H%M%S")
            # Parse end timestamp
            end_dt = datetime.strptime(f"{end_date}_{end_time}", "%Y%m%d_%H%M%S")
            
            # Apply timezone if specified
            if self.timezone:
                start_dt = start_dt.replace(tzinfo=self.timezone)
                end_dt = end_dt.replace(tzinfo=self.timezone)
            
            return start_dt, end_dt
        except ValueError as e:
            logger.warning(f"Failed to parse timestamp from {filename}: {e}")
            return None
    
    def _get_transcript_files_for_date(self, target_date: date) -> List[Path]:
        """Get all transcript files for a specific date."""
        # Construct path: base_path/YYYYMM/DD/
        year_month = target_date.strftime("%Y%m")
        day = target_date.strftime("%d")
        
        date_path = self.base_path / year_month / day
        
        if not date_path.exists():
            logger.info(f"No transcripts found for date {target_date} at {date_path}")
            return []
        
        # Find all transcript files
        transcript_files = list(date_path.glob("*_transcript_*.txt"))
        
        # Sort by filename (which includes timestamp)
        transcript_files.sort()
        
        return transcript_files
    
    def _read_transcript_content(self, file_path: Path) -> str:
        """Read the content of a transcript file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            logger.error(f"Failed to read transcript file {file_path}: {e}")
            return ""
    
    def _filter_by_time_range(
        self, 
        segments: List[TranscriptSegment], 
        start_time: Optional[time], 
        end_time: Optional[time]
    ) -> List[TranscriptSegment]:
        """Filter segments by time range."""
        if not start_time and not end_time:
            return segments
        
        filtered = []
        for segment in segments:
            segment_time = segment.timestamp.time()
            
            if start_time and segment_time < start_time:
                continue
            if end_time and segment_time > end_time:
                continue
            
            filtered.append(segment)
        
        return filtered
    
    def _filter_by_query(
        self, 
        segments: List[TranscriptSegment], 
        query: str
    ) -> List[TranscriptSegment]:
        """Filter segments by search query."""
        if not query:
            return segments
        
        query_lower = query.lower()
        return [
            segment for segment in segments 
            if query_lower in segment.content.lower()
        ]
    
    def search_transcripts(
        self,
        target_date: str,
        start_time: Optional[str] = None,
        end_time: Optional[str] = None,
        query: Optional[str] = None
    ) -> TranscriptResult:
        """Search transcripts for a specific date and optional time range."""
        # Parse date
        try:
            search_date = datetime.strptime(target_date, "%Y-%m-%d").date()
        except ValueError:
            raise ValueError(f"Invalid date format: {target_date}. Use YYYY-MM-DD")
        
        # Parse time range if provided
        start_time_obj = None
        end_time_obj = None
        
        if start_time:
            try:
                start_time_obj = datetime.strptime(start_time, "%H:%M").time()
            except ValueError:
                raise ValueError(f"Invalid start time format: {start_time}. Use HH:MM")
        
        if end_time:
            try:
                end_time_obj = datetime.strptime(end_time, "%H:%M").time()
            except ValueError:
                raise ValueError(f"Invalid end time format: {end_time}. Use HH:MM")
        
        # Get transcript files
        transcript_files = self._get_transcript_files_for_date(search_date)
        
        # Parse all segments
        all_segments = []
        for file_path in transcript_files:
            timestamps = self._parse_timestamp_from_filename(file_path.name)
            if not timestamps:
                continue
            
            start_dt, end_dt = timestamps
            content = self._read_transcript_content(file_path)
            
            if content:
                # Calculate duration
                duration = int((end_dt - start_dt).total_seconds())
                
                # Extract video filename (remove _transcript_*.txt suffix)
                video_file = file_path.name.split('_transcript_')[0]
                
                segment = TranscriptSegment(
                    timestamp=start_dt,
                    content=content,
                    file_path=str(file_path),
                    video_file=video_file,
                    duration_seconds=duration
                )
                all_segments.append(segment)
        
        # Apply filters
        filtered_segments = self._filter_by_time_range(all_segments, start_time_obj, end_time_obj)
        filtered_segments = self._filter_by_query(filtered_segments, query)
        
        return TranscriptResult(
            date=target_date,
            segments=filtered_segments,
            total_segments=len(filtered_segments),
            query_used=query
        )
    
    def list_available_dates(
        self,
        year: Optional[int] = None,
        month: Optional[int] = None
    ) -> List[TranscriptDate]:
        """List all dates that have transcript data."""
        available_dates = []
        
        # If year is specified, only look in those directories
        if year and month:
            year_month_dirs = [self.base_path / f"{year}{month:02d}"]
        elif year:
            year_month_dirs = [
                d for d in self.base_path.iterdir() 
                if d.is_dir() and d.name.startswith(str(year))
            ]
        else:
            year_month_dirs = [
                d for d in self.base_path.iterdir() 
                if d.is_dir() and d.name.isdigit() and len(d.name) == 6
            ]
        
        for year_month_dir in sorted(year_month_dirs):
            if not year_month_dir.exists():
                continue
            
            # Extract year and month from directory name
            ym = year_month_dir.name
            dir_year = int(ym[:4])
            dir_month = int(ym[4:6])
            
            # Check each day directory
            for day_dir in sorted(year_month_dir.iterdir()):
                if not day_dir.is_dir() or not day_dir.name.isdigit():
                    continue
                
                day = int(day_dir.name)
                
                # Count transcript files
                transcript_files = list(day_dir.glob("*_transcript_*.txt"))
                if transcript_files:
                    # Calculate total duration
                    total_duration = 0
                    for file_path in transcript_files:
                        timestamps = self._parse_timestamp_from_filename(file_path.name)
                        if timestamps:
                            start_dt, end_dt = timestamps
                            duration = int((end_dt - start_dt).total_seconds())
                            total_duration += duration
                    
                    date_str = f"{dir_year:04d}-{dir_month:02d}-{day:02d}"
                    available_dates.append(TranscriptDate(
                        date=date_str,
                        transcript_count=len(transcript_files),
                        total_duration_seconds=total_duration
                    ))
        
        return available_dates
    
    def get_transcript_summary(self, target_date: str) -> TranscriptSummary:
        """Get a summary of transcript activity for a specific date."""
        # Parse date
        try:
            search_date = datetime.strptime(target_date, "%Y-%m-%d").date()
        except ValueError:
            raise ValueError(f"Invalid date format: {target_date}. Use YYYY-MM-DD")
        
        # Get transcript files
        transcript_files = self._get_transcript_files_for_date(search_date)
        
        if not transcript_files:
            return TranscriptSummary(
                date=target_date,
                total_segments=0,
                total_duration_seconds=0,
                start_time=None,
                end_time=None,
                file_count=0
            )
        
        # Calculate summary statistics
        total_duration = 0
        earliest_start = None
        latest_end = None
        
        for file_path in transcript_files:
            timestamps = self._parse_timestamp_from_filename(file_path.name)
            if timestamps:
                start_dt, end_dt = timestamps
                duration = int((end_dt - start_dt).total_seconds())
                total_duration += duration
                
                if earliest_start is None or start_dt < earliest_start:
                    earliest_start = start_dt
                if latest_end is None or end_dt > latest_end:
                    latest_end = end_dt
        
        return TranscriptSummary(
            date=target_date,
            total_segments=len(transcript_files),
            total_duration_seconds=total_duration,
            start_time=earliest_start,
            end_time=latest_end,
            file_count=len(transcript_files)
        )