# Challenge MCP

[![PyPI version](https://badge.fury.io/py/challenge-mcp.svg)](https://badge.fury.io/py/challenge-mcp)
[![Python Support](https://img.shields.io/pypi/pyversions/challenge-mcp.svg)](https://pypi.org/project/challenge-mcp/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A Model Context Protocol (MCP) server for challenge management with authentication. This package provides a FastMCP server that enables AI assistants to interact with challenge management systems through a standardized protocol.

## Features

- 🚀 **FastMCP Server**: Built on the Model Context Protocol for seamless AI integration
- 🔐 **Authentication**: Secure token-based authentication system
- 🏆 **Challenge Management**: Complete API for managing challenges, participants, and teams
- 📊 **Real-time Data**: Server-Sent Events (SSE) support for live updates
- 🔧 **Easy Configuration**: Environment-based configuration with sensible defaults

## Installation

### From PyPI (Recommended)

```bash
pip install challenge-mcp
```

### From Source

```bash
git clone https://github.com/your-username/challenge-mcp.git
cd challenge-mcp
pip install -e .
```

### Development Installation

```bash
git clone https://github.com/your-username/challenge-mcp.git
cd challenge-mcp
pip install -e ".[dev]"
```

## Quick Start

### 1. Environment Setup

Create a `.env` file in your project directory:

```env
API_BASE_URL=https://your-api-server.com
# Add other environment variables as needed
```

### 2. Start the Server

```python
from challenge_mcp import mcp

# Configure if needed
mcp.host = "0.0.0.0"
mcp.port = 8050

# Start the server
mcp.run()
```

### 3. Health Check

Once the server is running, you can check its health:

```bash
curl http://localhost:8050/v1/mcp/health
```

## API Endpoints

The server provides several MCP tools for challenge management:

### Challenge Management
- `get_active_challenge_list` - Fetch active challenges with filtering and pagination
- `get_active_challenge_by_id` - Get specific challenge details
- `get_challenge_pool_list` - Browse available challenge templates
- `get_challenge_pool_by_id` - Get challenge template details

### Participant Management
- `get_active_challenge_participants` - List challenge participants
- `get_active_challenge_participant_workouts` - Get participant workout data

### Team Management
- `get_active_challenge_teams` - List challenge teams

### Statistics
- `get_active_challenge_stats` - Get challenge statistics and analytics

## Configuration

### Environment Variables

| Variable | Description | Required | Default |
|----------|-------------|----------|---------|
| `API_BASE_URL` | Base URL for the backend API | Yes | - |

### Server Configuration

```python
from challenge_mcp import mcp

# Configure server settings
mcp.host = "127.0.0.1"
mcp.port = 8080
mcp.timeout_keep_alive = 30
mcp.timeout_graceful_shutdown = 10
```

## Authentication

The server uses token-based authentication. Tokens should be provided in the request context when calling MCP tools. The authentication is handled automatically by the `AuthFastMCP` class.

## Development

### Setting up Development Environment

```bash
# Clone the repository
git clone https://github.com/your-username/challenge-mcp.git
cd challenge-mcp

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install development dependencies
pip install -e ".[dev]"
```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=challenge_mcp

# Run specific test file
pytest tests/test_server.py
```

### Code Formatting

```bash
# Format code with black
black challenge_mcp/

# Sort imports with isort
isort challenge_mcp/

# Type checking with mypy
mypy challenge_mcp/
```

## Docker Support

You can also run the server using Docker:

```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY . .
RUN pip install .

EXPOSE 8050
CMD ["python", "-c", "from challenge_mcp import mcp; mcp.run()"]
```

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

- 📖 [Documentation](https://challenge-mcp.readthedocs.io)
- 🐛 [Bug Reports](https://github.com/your-username/challenge-mcp/issues)
- 💬 [Discussions](https://github.com/your-username/challenge-mcp/discussions)

## Changelog

See [CHANGELOG.md](CHANGELOG.md) for a list of changes and version history.

---

Made with ❤️ by the Challenge MCP Team 