"""MCP server implementation for Rewind AI transcripts."""

import json
import logging
import os
from typing import Any, Dict, List, Sequence

from mcp.server import Server
from mcp.server.session import ServerSession
from mcp.server.stdio import stdio_server
from mcp.types import (
    ClientCapabilities,
    TextContent,
    Tool,
)

from .models import (
    TranscriptQuery,
    ListTranscriptDatesRequest,
    TranscriptSummaryRequest,
)
from .transcript_reader import TranscriptReader

logger = logging.getLogger(__name__)


async def serve() -> None:
    """Main entry point for the MCP server."""
    # Get configuration from environment
    base_path = os.getenv(
        "REWIND_BASE_PATH",
        str(os.path.expanduser("~/Library/Application Support/com.memoryvault.MemoryVault/chunks"))
    )
    timezone = os.getenv("REWIND_TIMEZONE")
    
    # Initialize transcript reader
    reader = TranscriptReader(base_path, timezone)
    
    # Initialize MCP server
    server = Server("mcp-server-rewind")
    
    @server.list_tools()
    async def list_tools() -> List[Tool]:
        """List available tools."""
        return [
            Tool(
                name="search_transcripts",
                description="Search screen recording transcripts by date and optional time range",
                inputSchema=TranscriptQuery.model_json_schema(),
            ),
            Tool(
                name="list_transcript_dates",
                description="List available dates with transcript data",
                inputSchema=ListTranscriptDatesRequest.model_json_schema(),
            ),
            Tool(
                name="get_transcript_summary",
                description="Get a summary of transcript activity for a date",
                inputSchema=TranscriptSummaryRequest.model_json_schema(),
            ),
        ]
    
    @server.call_tool()
    async def call_tool(name: str, arguments: Dict[str, Any]) -> List[TextContent]:
        """Handle tool calls."""
        try:
            if name == "search_transcripts":
                # Validate arguments
                query = TranscriptQuery(**arguments)
                
                # Search transcripts
                result = reader.search_transcripts(
                    target_date=query.date,
                    start_time=query.start_time,
                    end_time=query.end_time,
                    query=query.query
                )
                
                # Format result
                output = f"Found {result.total_segments} transcript segments for {result.date}"
                if query.start_time or query.end_time:
                    output += f" (time range: {query.start_time or 'start'} to {query.end_time or 'end'})"
                if query.query:
                    output += f" matching '{query.query}'"
                output += "\n\n"
                
                for i, segment in enumerate(result.segments, 1):
                    output += f"--- Segment {i} ---\n"
                    output += f"Time: {segment.timestamp.strftime('%H:%M:%S')}"
                    if segment.duration_seconds:
                        output += f" (duration: {segment.duration_seconds}s)"
                    output += f"\nFile: {segment.video_file}\n"
                    output += f"Content:\n{segment.content}\n\n"
                
                return [TextContent(type="text", text=output)]
            
            elif name == "list_transcript_dates":
                # Validate arguments
                request = ListTranscriptDatesRequest(**arguments)
                
                # List available dates
                dates = reader.list_available_dates(
                    year=request.year,
                    month=request.month
                )
                
                if not dates:
                    output = "No transcript data found"
                    if request.year:
                        output += f" for year {request.year}"
                    if request.month:
                        output += f" month {request.month}"
                else:
                    output = f"Found transcript data for {len(dates)} dates:\n\n"
                    
                    for date_info in dates:
                        output += f"📅 {date_info.date}: "
                        output += f"{date_info.transcript_count} segments"
                        if date_info.total_duration_seconds:
                            hours = date_info.total_duration_seconds // 3600
                            minutes = (date_info.total_duration_seconds % 3600) // 60
                            output += f" ({hours}h {minutes}m total)"
                        output += "\n"
                
                return [TextContent(type="text", text=output)]
            
            elif name == "get_transcript_summary":
                # Validate arguments
                request = TranscriptSummaryRequest(**arguments)
                
                # Get summary
                summary = reader.get_transcript_summary(request.date)
                
                output = f"📊 Transcript Summary for {summary.date}\n"
                output += "=" * 40 + "\n\n"
                
                if summary.total_segments == 0:
                    output += "No transcripts found for this date."
                else:
                    output += f"Total segments: {summary.total_segments}\n"
                    
                    if summary.total_duration_seconds:
                        hours = summary.total_duration_seconds // 3600
                        minutes = (summary.total_duration_seconds % 3600) // 60
                        seconds = summary.total_duration_seconds % 60
                        output += f"Total duration: {hours}h {minutes}m {seconds}s\n"
                    
                    if summary.start_time and summary.end_time:
                        output += f"Recording period: {summary.start_time.strftime('%H:%M:%S')} - {summary.end_time.strftime('%H:%M:%S')}\n"
                        
                        # Calculate active hours
                        active_duration = (summary.end_time - summary.start_time).total_seconds()
                        active_hours = active_duration / 3600
                        output += f"Active hours: {active_hours:.1f}h\n"
                        
                        # Calculate coverage percentage
                        if active_duration > 0:
                            coverage = (summary.total_duration_seconds / active_duration) * 100
                            output += f"Coverage: {coverage:.1f}%\n"
                
                return [TextContent(type="text", text=output)]
            
            else:
                raise ValueError(f"Unknown tool: {name}")
        
        except Exception as e:
            logger.error(f"Error executing {name}: {str(e)}")
            return [TextContent(type="text", text=f"Error: {str(e)}")]
    
    # Run the server
    options = server.create_initialization_options()
    async with stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream, options, raise_exceptions=True)