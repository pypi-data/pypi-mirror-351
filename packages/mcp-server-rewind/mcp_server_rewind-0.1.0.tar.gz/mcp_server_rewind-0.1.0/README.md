# MCP Server for Rewind AI Transcripts

A Model Context Protocol (MCP) server that provides tools to query and search through Rewind AI screen recording transcripts.

## Features

- 🔍 **Search transcripts** by date and time range
- 📅 **List available dates** with transcript data
- 📊 **Get summaries** of transcript activity for any date
- 🔎 **Full-text search** within transcript content
- ⏰ **Time-based filtering** to focus on specific periods

## Installation

### Using uv (recommended)

```bash
# Clone the repository
git clone https://github.com/yourusername/mcp-server-rewind.git
cd mcp-server-rewind

# Install with uv
uv pip install -e .
```

### Using pip

```bash
# Clone the repository
git clone https://github.com/yourusername/mcp-server-rewind.git
cd mcp-server-rewind

# Install with pip
pip install -e .
```

## Configuration

### Claude Desktop Integration

Add the following to your Claude Desktop configuration file:

**MacOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
**Windows**: `%APPDATA%\Claude\claude_desktop_config.json`

```json
{
  "mcpServers": {
    "rewind": {
      "command": "uv",
      "args": [
        "--directory",
        "/path/to/mcp-server-rewind",
        "run",
        "mcp-server-rewind"
      ],
      "env": {
        "REWIND_BASE_PATH": "/Users/yourusername/Library/Application Support/com.memoryvault.MemoryVault/chunks",
        "REWIND_TIMEZONE": "Europe/Berlin"
      }
    }
  }
}
```

### Environment Variables

- `REWIND_BASE_PATH`: Base path to Rewind chunks directory (default: `~/Library/Application Support/com.memoryvault.MemoryVault/chunks`)
- `REWIND_TIMEZONE`: Timezone for timestamp interpretation (optional, e.g., "Europe/Berlin")

## Usage

Once configured, the following tools are available in Claude:

### 1. Search Transcripts

Search for screen recording transcripts by date with optional time range and text query.

```
search_transcripts:
  date: "2025-05-31"
  start_time: "09:30"  # Optional: HH:MM format
  end_time: "10:30"    # Optional: HH:MM format
  query: "neuraflow"   # Optional: text to search for
```

### 2. List Transcript Dates

List all dates that have transcript data, optionally filtered by year and/or month.

```
list_transcript_dates:
  year: 2025  # Optional
  month: 5    # Optional (1-12)
```

### 3. Get Transcript Summary

Get a summary of transcript activity for a specific date.

```
get_transcript_summary:
  date: "2025-05-31"
```

## Example Queries

**Find all screen activity for a specific time period:**
```
"Show me what I was working on between 9:30 and 10:30 on May 31st"
```

**Search for specific content:**
```
"Find all mentions of 'neuraflow' in my screen recordings from May 31st"
```

**Get an overview of recording activity:**
```
"What dates do I have screen recordings for in May 2025?"
```

**Summarize a day's activity:**
```
"Give me a summary of my screen recording activity on May 29th"
```

## How It Works

The server reads transcript files from Rewind's local storage, which are organized by date in the following structure:
```
chunks/
├── 202505/          # YYYYMM
│   ├── 29/          # DD
│   │   ├── video_file_transcript_20250529_093756_to_20250529_094410.txt
│   │   └── ...
│   └── 31/
│       └── ...
└── ...
```

Each transcript file contains the OCR'd text from the corresponding video segment, allowing you to search through your screen content as if it were a document.

## Development

### Running Tests

```bash
uv run pytest
```

### Code Quality

```bash
# Type checking
uv run pyright

# Linting
uv run ruff check .

# Formatting
uv run ruff format .
```

## License

MIT License - see LICENSE file for details.

## Privacy Note

This tool only accesses local Rewind transcript files on your machine. No data is sent to external services. All processing happens locally on your computer.