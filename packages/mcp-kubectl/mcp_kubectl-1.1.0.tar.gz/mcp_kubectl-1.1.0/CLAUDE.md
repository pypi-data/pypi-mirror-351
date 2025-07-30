# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Model Context Protocol (MCP) server for Kubernetes that enables AI assistants to interact with Kubernetes clusters through natural language. The project bridges AI assistants (Claude, Cursor, WindSurf) and Kubernetes operations via the standardized MCP protocol.

## Development Commands

### Package Management (uv native)
- **Install project**: `uv sync` (installs all dependencies from pyproject.toml)
- **Add dependencies**: `uv add <package>` (adds to pyproject.toml and syncs)
- **Add dev dependencies**: `uv add --group dev <package>`
- **Run commands**: `uv run <command>` (runs in project environment)
- **Development install**: `uv pip install -e .` (after `uv sync`)

### Testing
```bash
# Run all tests
uv run pytest

# Run only smoke tests (fast, no cluster needed)
uv run pytest tests/test_smoke.py

# Run only integration tests (requires cluster)
uv run pytest tests/test_integration.py

# Run with verbose output
uv run pytest -v
```

### Code Quality
```bash
# Lint code
uv run ruff check .

# Format code
uv run black .

# Type checking
uv run mypy kubectl_mcp_tool/

# Run all quality checks
uv run ruff check . && uv run black --check . && uv run mypy kubectl_mcp_tool/
```

### Running the Server
```bash
# Start MCP server (stdio transport)
uv run mcp-kubectl serve

# Start with SSE transport
uv run mcp-kubectl serve --transport sse

# Start in Cursor compatibility mode
uv run mcp-kubectl serve --cursor

# Or run via uvx (recommended for testing)
uvx --from mcp-kubectl mcp-kubectl serve
```

### Building and Publishing
```bash
# Simple make commands (recommended)
make publish-test    # Publish to Test PyPI
make publish-prod    # Publish to Production PyPI
make build          # Build package
make test           # Run tests
make help           # Show all commands

# Manual commands  
uv build
uv run pytest
export UV_PUBLISH_TOKEN=pypi-YOUR_TOKEN_HERE
uv publish --publish-url https://test.pypi.org/legacy/  # Test
uv publish                                              # Production
```

See [PUBLISHING.md](PUBLISHING.md) for setup instructions.

## Architecture

### Core Components
- **`kubectl_mcp_tool/mcp_server.py`**: Main MCP server using FastMCP framework with 16 clean tools
- **`kubectl_mcp_tool/cli.py`**: Simple CLI entry point for serving the MCP server
- **`kubectl_mcp_tool/core/kubernetes_ops.py`**: Direct Kubernetes API operations

### Directory Structure
- **`kubectl_mcp_tool/`**: Clean, minimal codebase
  - `__init__.py`: Package initialization
  - `mcp_server.py`: Main MCP server implementation
  - `cli.py`: CLI interface
  - `core/kubernetes_ops.py`: Core Kubernetes operations

### Transport Methods
- **stdio**: Standard input/output (primary for Claude)
- **SSE**: Server-Sent Events for web interfaces
- **HTTP**: REST API endpoints

## Key Technologies

- **MCP Framework**: `mcp>=1.5.0` for Model Context Protocol
- **Kubernetes Client**: `kubernetes>=28.1.0` for K8s API operations
- **FastAPI/Uvicorn**: Web framework for HTTP transport
- **Rich**: Terminal formatting
- **PyYAML**: Configuration parsing
- **Python**: Requires Python 3.10+ (updated from 3.9+ due to MCP dependency)

## Testing Strategy

Use the MCP inspector for testing all tools and functionality:
```bash
npx @modelcontextprotocol/inspector uv run mcp-kubectl serve
```

This provides a web interface to test all 16 MCP tools directly with your Kubernetes cluster.

## AI Assistant Integration

All AI assistants use the same clean MCP server:
- **Claude**: Uses stdio transport via `~/.config/claude/mcp.json`
- **Cursor**: Uses stdio transport via `~/.cursor/mcp.json`
- **WindSurf**: Uses stdio transport via `~/.config/windsurf/mcp.json`

All use the same configuration pattern with the unified server.

## Installation

### User Installation
```bash
# Install uv if not already installed (via Homebrew recommended for GUI apps)
brew install uv

# Install tool globally
uv tool install mcp-kubectl

# Or install from GitHub
uv tool install git+https://github.com/rohitg00/kubectl-mcp-server.git
```

### Development Setup
```bash
# Clone and set up development environment
git clone https://github.com/rohitg00/kubectl-mcp-server.git
cd kubectl-mcp-server
uv sync
uv pip install -e .
```

## Working Configuration

The following configuration works reliably with Claude Desktop and other AI assistants:

```json
{
  "mcpServers": {
    "kubernetes": {
      "command": "uvx",
      "args": ["--from", "mcp-kubectl", "mcp-kubectl", "serve"],
      "env": {
        "KUBECONFIG": "~/.kube/config"
      }
    }
  }
}
```

**Requirements:**
- uv installed via Homebrew: `brew install uv`
- Package installed: `uv tool install mcp-kubectl`

This approach uses `uvx` to run the tool, which handles dependency management automatically and works reliably with GUI applications.