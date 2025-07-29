# APILama

APILama is the API gateway for the PyLama ecosystem. It serves as the central communication layer between the frontend WebLama interface and the various backend services (PyLama, PyBox, PyLLM, SheLLama). APILama integrates with LogLama as the primary service for centralized logging, environment management, and service orchestration.

## Features

- **Unified API Gateway**: Single entry point for all PyLama ecosystem services
- **Service Routing**: Intelligent routing of requests to appropriate backend services (PyBox, PyLLM, SheLLama, PyLama)
- **RESTful API Design**: Clean and consistent API endpoints for all operations
- **Cross-Origin Resource Sharing (CORS)**: Support for cross-origin requests from the WebLama frontend
- **Authentication and Authorization**: Secure access to API endpoints
- **Response Standardization**: Consistent response format across all services
- **Error Handling**: Comprehensive error handling and reporting
- **LogLama Integration**: Integrates with LogLama for centralized logging, environment management, and service orchestration
- **Structured Logging**: All API requests and responses are logged with component context for better debugging and monitoring

## Installation

```bash
# Create a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install the package in development mode
pip install -e .  # This is important! Always install in development mode before starting
```

> **IMPORTANT**: Always run `pip install -e .` before starting the project to ensure all dependencies are properly installed and the package is available in development mode.

## Usage

### Running the API Gateway

```bash
# Start the API server with default settings
python -m apilama.app --port 8080 --host 127.0.0.1

# Or with environment variables
export PORT=8080
export HOST=127.0.0.1
python -m apilama.app
```

### Using the Makefile

```bash
# Start the API server with default settings
make run

# Start with custom port
make run PORT=8090
```

### Environment Variables

APILama uses the following environment variables for configuration:

- `PORT`: The port to run the server on (default: 8080)
- `HOST`: The host to bind to (default: 127.0.0.1)
- `DEBUG`: Enable debug mode (default: False)
- `PYBOX_API_URL`: URL of the PyBox API (default: http://localhost:8000)
- `PYLLM_API_URL`: URL of the PyLLM API (default: http://localhost:8001)
- `SHELLAMA_API_URL`: URL of the SheLLama API (default: http://localhost:8002)
- `PYLAMA_API_URL`: URL of the PyLama API (default: http://localhost:8003)

You can set these variables in a `.env` file or pass them directly when starting the server.

## API Documentation

### Health Check
```
GET /api/health
```
Returns the health status of the APILama service.

### SheLLama Endpoints

#### File Operations
```
GET /api/shellama/files?directory=/path/to/dir   # List files in a directory
GET /api/shellama/file?filename=/path/to/file     # Get file content
POST /api/shellama/file                           # Create/update a file
DELETE /api/shellama/file?filename=/path/to/file  # Delete a file
```

#### Directory Operations
```
GET /api/shellama/directory?directory=/path/to/dir  # Get directory information
POST /api/shellama/directory                        # Create a directory
DELETE /api/shellama/directory?directory=/path      # Delete a directory
```

#### Shell Operations
```
POST /api/shellama/shell  # Execute a shell command
```

### PyBox Endpoints
```
GET /api/pybox/health     # Check PyBox health
POST /api/pybox/execute   # Execute Python code
```

### PyLLM Endpoints
```
GET /api/pyllm/health     # Check PyLLM health
POST /api/pyllm/generate  # Generate code or text
```

### PyLama Endpoints
```
GET /api/pylama/health    # Check PyLama health
GET /api/pylama/models    # List available models
POST /api/pylama/execute  # Execute a model
```

## Development

```bash
# Install development dependencies
pip install -e ".[dev]"

# Run tests
python -m pytest

# Format code
black apilama tests

# Lint code
flake8 apilama tests
```

## License

MIT
