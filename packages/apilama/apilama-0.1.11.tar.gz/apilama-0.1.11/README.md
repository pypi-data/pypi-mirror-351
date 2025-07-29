# APILama

## PyLama Ecosystem Navigation

| Project | Description | Links |
|---------|-------------|-------|
| **APILama** | API service for code generation | [GitHub](https://github.com/py-lama/apilama) · [Docs](https://py-lama.github.io/apilama/) |
| **GetLLM** | LLM model management and code generation | [GitHub](https://github.com/py-lama/getllm) · [PyPI](https://pypi.org/project/getllm/) · [Docs](https://py-lama.github.io/getllm/) |
| **DevLama** | Python code generation with Ollama | [GitHub](https://github.com/py-lama/devlama) · [Docs](https://py-lama.github.io/devlama/) |
| **LogLama** | Centralized logging and environment management | [GitHub](https://github.com/py-lama/loglama) · [PyPI](https://pypi.org/project/loglama/) · [Docs](https://py-lama.github.io/loglama/) |
| **BEXY** | Sandbox for executing generated code | [GitHub](https://github.com/py-lama/bexy) · [Docs](https://py-lama.github.io/bexy/) |
| **JSLama** | JavaScript code generation | [GitHub](https://github.com/py-lama/jslama) · [NPM](https://www.npmjs.com/package/jslama) · [Docs](https://py-lama.github.io/jslama/) |
| **JSBox** | JavaScript sandbox for executing code | [GitHub](https://github.com/py-lama/jsbox) · [NPM](https://www.npmjs.com/package/jsbox) · [Docs](https://py-lama.github.io/jsbox/) |
| **SheLLama** | Shell command generation | [GitHub](https://github.com/py-lama/shellama) · [PyPI](https://pypi.org/project/shellama/) · [Docs](https://py-lama.github.io/shellama/) |
| **WebLama** | Web application generation | [GitHub](https://github.com/py-lama/weblama) · [Docs](https://py-lama.github.io/weblama/) |

## Author

**Tom Sapletta** — DevOps Engineer & Systems Architect

- 💻 15+ years in DevOps, Software Development, and Systems Architecture
- 🏢 Founder & CEO at Telemonit (Portigen - edge computing power solutions)
- 🌍 Based in Germany | Open to remote collaboration
- 📚 Passionate about edge computing, hypermodularization, and automated SDLC

[![GitHub](https://img.shields.io/badge/GitHub-181717?logo=github&logoColor=white)](https://github.com/tom-sapletta-com)
[![LinkedIn](https://img.shields.io/badge/LinkedIn-0077B5?logo=linkedin&logoColor=white)](https://linkedin.com/in/tom-sapletta-com)
[![ORCID](https://img.shields.io/badge/ORCID-A6CE39?logo=orcid&logoColor=white)](https://orcid.org/0009-0000-6327-2810)
[![Portfolio](https://img.shields.io/badge/Portfolio-000000?style=flat&logo=about.me&logoColor=white)](https://www.digitname.com/)

## Support This Project

If you find this project useful, please consider supporting it:

- [GitHub Sponsors](https://github.com/sponsors/tom-sapletta-com)
- [Open Collective](https://opencollective.com/tom-sapletta-com)
- [PayPal](https://www.paypal.me/softreck/10.00)
- [Donate via Softreck](https://donate.softreck.dev)

---

APILama is the API gateway for the PyLama ecosystem. It serves as the central communication layer between the frontend WebLama interface and the various backend services (PyLama, BEXY, PyLLM, SheLLama). APILama integrates with LogLama as the primary service for centralized logging, environment management, and service orchestration.

## Features

- **Unified API Gateway**: Single entry point for all PyLama ecosystem services
- **Service Routing**: Intelligent routing of requests to appropriate backend services (BEXY, PyLLM, SheLLama, PyLama)
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
- `BEXY_API_URL`: URL of the BEXY API (default: http://localhost:8000)
- `GETLLM_API_URL`: URL of the PyLLM API (default: http://localhost:8001)
- `SHELLAMA_API_URL`: URL of the SheLLama API (default: http://localhost:8002)
- `DEVLAMA_API_URL`: URL of the PyLama API (default: http://localhost:8003)

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

### BEXY Endpoints
```
GET /api/bexy/health     # Check BEXY health
POST /api/bexy/execute   # Execute Python code
```

### PyLLM Endpoints
```
GET /api/getllm/health     # Check PyLLM health
POST /api/getllm/generate  # Generate code or text
```

### PyLama Endpoints
```
GET /api/devlama/health    # Check PyLama health
GET /api/devlama/models    # List available models
POST /api/devlama/execute  # Execute a model
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
