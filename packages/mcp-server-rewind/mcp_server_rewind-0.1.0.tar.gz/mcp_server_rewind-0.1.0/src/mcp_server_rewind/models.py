"""Data models for the Rewind MCP server."""

from datetime import datetime, time
from typing import Optional, List
from pydantic import BaseModel, Field


class TimeRange(BaseModel):
    """Represents a time range for filtering transcripts."""
    start_time: Optional[time] = None
    end_time: Optional[time] = None


class TranscriptQuery(BaseModel):
    """Input parameters for searching transcripts."""
    date: str = Field(..., description="Date in ISO format (YYYY-MM-DD)")
    start_time: Optional[str] = Field(None, description="Start time in HH:MM format")
    end_time: Optional[str] = Field(None, description="End time in HH:MM format")
    query: Optional[str] = Field(None, description="Optional text to search within transcripts")


class ListTranscriptDatesRequest(BaseModel):
    """Input parameters for listing available transcript dates."""
    year: Optional[int] = Field(None, description="Filter by year")
    month: Optional[int] = Field(None, description="Filter by month (1-12)")


class TranscriptSummaryRequest(BaseModel):
    """Input parameters for getting transcript summary."""
    date: str = Field(..., description="Date in ISO format (YYYY-MM-DD)")


class TranscriptSegment(BaseModel):
    """Represents a segment of transcript content."""
    timestamp: datetime
    content: str
    file_path: str
    video_file: Optional[str] = None
    duration_seconds: Optional[int] = None


class TranscriptResult(BaseModel):
    """Result of a transcript search."""
    date: str
    segments: List[TranscriptSegment]
    total_segments: int
    query_used: Optional[str] = None


class TranscriptDate(BaseModel):
    """Represents a date with available transcripts."""
    date: str
    transcript_count: int
    total_duration_seconds: Optional[int] = None


class TranscriptSummary(BaseModel):
    """Summary of transcript activity for a date."""
    date: str
    total_segments: int
    total_duration_seconds: Optional[int] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    file_count: int