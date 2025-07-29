# SheLLama

## PyLama Ecosystem Navigation

| Project | Description | Links |
|---------|-------------|-------|
| **SheLLama** | Shell command generation | [GitHub](https://github.com/py-lama/shellama) · [PyPI](https://pypi.org/project/shellama/) · [Docs](https://py-lama.github.io/shellama/) |
| **GetLLM** | LLM model management and code generation | [GitHub](https://github.com/py-lama/getllm) · [PyPI](https://pypi.org/project/getllm/) · [Docs](https://py-lama.github.io/getllm/) |
| **DevLama** | Python code generation with Ollama | [GitHub](https://github.com/py-lama/devlama) · [Docs](https://py-lama.github.io/devlama/) |
| **LogLama** | Centralized logging and environment management | [GitHub](https://github.com/py-lama/loglama) · [PyPI](https://pypi.org/project/loglama/) · [Docs](https://py-lama.github.io/loglama/) |
| **APILama** | API service for code generation | [GitHub](https://github.com/py-lama/apilama) · [Docs](https://py-lama.github.io/apilama/) |
| **BEXY** | Sandbox for executing generated code | [GitHub](https://github.com/py-lama/bexy) · [Docs](https://py-lama.github.io/bexy/) |
| **JSLama** | JavaScript code generation | [GitHub](https://github.com/py-lama/jslama) · [NPM](https://www.npmjs.com/package/jslama) · [Docs](https://py-lama.github.io/jslama/) |
| **JSBox** | JavaScript sandbox for executing code | [GitHub](https://github.com/py-lama/jsbox) · [NPM](https://www.npmjs.com/package/jsbox) · [Docs](https://py-lama.github.io/jsbox/) |
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

SheLLama is a dedicated REST API service for shell and filesystem operations in the PyLama ecosystem. It provides a unified interface for file management, directory operations, shell command execution, and Git integration, available both as a Python library and a standalone REST API service that communicates with the APILama gateway. SheLLama integrates with LogLama as the primary service for centralized logging, environment management, and service orchestration.

## Features

- **RESTful API**: Complete REST API for all shell and filesystem operations
- **File Operations**: Read, write, list, and search files with proper error handling
- **Directory Management**: Create, delete, and list directories with detailed information
- **Shell Command Execution**: Execute shell commands with output capture and error handling
- **Git Integration**: Initialize repositories, commit changes, view status and logs
- **Secure File Handling**: Proper permissions and security checks for all operations
- **Cross-Origin Support**: CORS headers for integration with web applications
- **LogLama Integration**: Integrates with LogLama for centralized logging, environment management, and service orchestration
- **Structured Logging**: All operations are logged with component context for better filtering and analysis
- **Advanced Error Handling**: Standardized error responses with categorization and severity levels
- **Debug Window Integration**: Real-time debugging information with filtering capabilities
- **Dependency Management**: Support for pip, Poetry, and Pipenv for flexible dependency management

## Installation

```bash
# Create a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install the package
pip install -e .
```

## Usage

### As a Python Library

```python
# File operations
from shellama import file_ops

# List files in a directory
files = file_ops.list_files('/path/to/directory')

# Read a file
content = file_ops.read_file('/path/to/file.md')

# Write to a file
file_ops.write_file('/path/to/file.md', 'New content')

# Directory operations
from shellama import dir_ops

# Create a directory
dir_ops.create_directory('/path/to/new/directory')

# Shell commands
from shellama import shell

# Execute a shell command
result = shell.execute_command('ls -la')

# Git operations
from shellama import git_ops

# Get git status
status = git_ops.get_status('/path/to/repo')
```

### As a REST API Service

SheLLama is designed to run as a standalone REST API service that communicates with the APILama gateway:

```bash
# Start the SheLLama API server
python -m shellama.app --port 8002 --host 127.0.0.1
```

Using environment variables:

```bash
export PORT=8002
export HOST=127.0.0.1
export DEBUG=False
python -m shellama.app
```

Or using the Makefile:

```bash
make run PORT=8002 HOST=127.0.0.1
```

### Environment Variables

SheLLama uses the following environment variables for configuration:

- `PORT`: The port to run the server on (default: 8002)
- `HOST`: The host to bind to (default: 127.0.0.1)
- `DEBUG`: Enable debug mode (default: False)
- `LOG_LEVEL`: Logging level (default: INFO)
- `LOG_FILE`: Log file path (default: shellama.log)
- `SECRET_KEY`: Secret key for secure operations

You can set these variables in a `.env` file or pass them directly when starting the server.

#### API Endpoints

**File Operations:**
- `GET /files?directory=/path/to/dir` - List files in a directory
- `GET /file?filename=/path/to/file.md` - Get file content
- `POST /file` - Save file content (JSON body: `{"filename": "path", "content": "data"}`)
- `DELETE /file?filename=/path/to/file.md` - Delete a file

**Directory Operations:**
- `GET /directory?path=/path/to/dir` - Get directory information
- `POST /directory` - Create a directory (JSON body: `{"path": "/path/to/dir"}`)
- `DELETE /directory?path=/path/to/dir` - Delete a directory

**Shell Operations:**
- `POST /shell` - Execute a shell command (JSON body: `{"command": "ls -la", "cwd": "/path/to/dir"}`)

**Git Operations:**
- `GET /git/status?path=/path/to/repo` - Get git repository status
- `POST /git/init` - Initialize a git repository (JSON body: `{"path": "/path/to/dir"}`)
- `POST /git/commit` - Commit changes (JSON body: `{"path": "/path/to/repo", "message": "commit message"}`)
- `GET /git/log?path=/path/to/repo` - Get git commit history

**Debug Operations:**
- `GET /api/debug/status` - Get debug window status
- `GET /api/debug/entries` - Get debug entries with optional filtering
- `POST /api/debug/clear` - Clear all debug entries
- `POST /api/debug/enable` - Enable the debug window
- `POST /api/debug/disable` - Disable the debug window
- `GET /api/debug/categories` - Get all available debug categories
- `GET /api/debug/levels` - Get all available debug levels
- `POST /api/debug/add` - Add a debug entry

## Development

### Setting Up the Development Environment

SheLLama supports multiple dependency management tools for flexibility. Choose the approach that works best for your workflow.

### Managing Services

The Makefile provides several targets to help manage services and Docker containers:

```bash
# Start the SheLLama service
make run PORT=8002 HOST=0.0.0.0

# Start the Ansible testing environment
make ansible-test-env-up

# Stop all services, Docker containers, and free up ports
make stop
```

The `stop` target will:
- Stop all running Python processes for SheLLama and APILama on standard ports (8002, 8080, 9002, 9080, 19002, 19080)
- Stop and remove all Docker containers related to the PyLama ecosystem
- Stop the Ansible testing environment
- Check for any processes still using the relevant ports

#### Using pip and venv (Standard)

```bash
# Create a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install development dependencies
pip install -e ".[dev]"
```

#### Using Poetry

```bash
# Install dependencies with Poetry
poetry install

# Activate the Poetry virtual environment
poetry shell

# Run a command without activating the environment
poetry run python -m shellama.app
```

#### Using Pipenv

```bash
# Install dependencies with Pipenv
pipenv install --dev

# Activate the Pipenv virtual environment
pipenv shell

# Run a command without activating the environment
pipenv run python -m shellama.app
```

### Running Tests

```bash
# Run all tests
python -m pytest

# Run specific test file
python -m pytest tests/test_file_ops.py

# Run with coverage report
python -m pytest --cov=shellama tests/
```

### Error Handling and Debugging

SheLLama includes a comprehensive error handling system that provides standardized error responses across the application. This system categorizes errors by type and severity, making it easier to identify and resolve issues.

#### Error Categories

- **Validation Errors**: Issues with input validation
- **Permission Errors**: Access denied or insufficient permissions
- **File System Errors**: Problems with file or directory operations
- **Git Errors**: Issues with Git operations
- **Shell Errors**: Problems executing shell commands
- **Configuration Errors**: Issues with application configuration
- **External Service Errors**: Problems with external services

#### Debug Window

The debug window provides real-time debugging information that can be accessed through the API. It captures detailed information about application operations, errors, and performance metrics.

Features include:

- **Filtering**: Filter debug entries by level, category, or source
- **Real-time Capture**: Capture debugging information as it happens
- **API Access**: Access debug information through REST API endpoints
- **Configurable**: Enable or disable debugging at runtime

```python
# Using the debug window in code
from shellama.debug_window import add_debug_entry, DebugLevel, DebugCategory

# Add a debug entry
add_debug_entry(
    message="Processing file operation",
    level=DebugLevel.INFO,
    category=DebugCategory.FILE_OPERATIONS,
    details={"filename": "example.txt", "operation": "read"}
)
```

### Ansible Integration Tests

SheLLama includes a comprehensive suite of Ansible tests that verify the functionality of all API endpoints. These tests ensure that the service works correctly and can be integrated with other systems.

#### Ansible Testing Environment

A Docker-based Ansible testing environment is available for testing SheLLama and its integration with other PyLama components. This environment includes:

- **Ansible Controller**: Container with Ansible and testing tools installed
- **Service Targets**: Containers for each PyLama component
- **Mock Services**: Containers that simulate services for testing integration

To use the Ansible testing environment:

```bash
# Build the testing environment
make ansible-test-env-build

# Start the testing environment
make ansible-test-env-up

# Run tests in the environment
make ansible-test-env-run

# Open a shell in the controller container
make ansible-test-env-shell

# Stop the testing environment
make ansible-test-env-down
```

See the `test_markdown/devops_tools/ANSIBLE_TESTING.md` file for more detailed information about the Ansible testing environment.

#### Docker Testing Environment

A Docker testing environment is available for testing SheLLama without requiring the actual services to be running:

```bash
# Build and run all tests
./run_docker_tests.sh --build --run-tests

# Start in interactive mode
./run_docker_tests.sh --interactive

# Run only Git operations tests
./run_docker_tests.sh --test-git

# Stop containers when done
./run_docker_tests.sh --stop
```

See the `DOCKER_TESTING.md` file for more detailed information about the Docker testing environment.

#### Test Markdown Directory

A comprehensive test markdown directory is included in the project to support testing of all SheLLama functionality:

```
/test_markdown/
├── file_operations/       # For testing file handling functions
├── git_operations/        # For testing Git functionality
├── shell_commands/        # For testing shell command execution
└── devops_tools/          # For testing DevOps tools integration
```

This directory contains example files for testing various aspects of SheLLama, including file operations, Git functionality, shell command execution, and DevOps tools integration. See the `test_markdown/README.md` file for more information.

```bash
# Run all Ansible tests (requires APILama and SheLLama to be running)
make ansible-test

# Run tests in development mode (skips service health check)
make ansible-test-dev

# Validate test syntax without running tests
make ansible-test-dry-run

# Run specific test categories
make ansible-test-git    # Run only Git operations tests
make ansible-test-file   # Run only file operations tests
make ansible-test-dir    # Run only directory operations tests
make ansible-test-shell  # Run only shell operations tests
make ansible-test-error  # Run only error handling tests

# Direct targets that bypass the virtual environment (for systems with permission issues)
make ansible-test-direct         # Run all tests directly
make ansible-test-git-direct    # Run only Git operations tests directly
make ansible-test-file-direct   # Run only file operations tests directly
make ansible-test-dir-direct    # Run only directory operations tests directly
make ansible-test-shell-direct  # Run only shell operations tests directly
make ansible-test-error-direct  # Run only error handling tests directly

# Syntax validation targets (no services or virtual environment needed)
make ansible-test-all-syntax    # Validate syntax for all test playbooks
make ansible-test-git-syntax    # Validate Git operations tests syntax
make ansible-test-file-syntax   # Validate File operations tests syntax
make ansible-test-dir-syntax    # Validate Directory operations tests syntax
make ansible-test-shell-syntax  # Validate Shell operations tests syntax
make ansible-test-error-syntax  # Validate Error handling tests syntax

# Mock test targets (no services or virtual environment needed)
make ansible-test-git-mock     # Run Git operations tests with mocked responses

# Test markdown verification
make verify-test-markdown     # Verify test markdown directory structure

# Run with additional options
make ansible-test ANSIBLE_OPTS="--verbose --no-cleanup"

# Or run the test script directly with options
./run_ansible_tests.sh

# Run with verbose output
./run_ansible_tests.sh --verbose

# Run without cleaning up test directories
./run_ansible_tests.sh --no-cleanup

# Run without generating HTML report
./run_ansible_tests.sh --no-report

# Skip the health check (for development/testing)
./run_ansible_tests.sh --skip-health-check

# Show help
./run_ansible_tests.sh --help
```

#### Test Reports

The Ansible tests generate a comprehensive HTML report that provides detailed information about the test results. The report includes:

- Test summary with overall status
- Detailed results for each test category (file operations, directory operations, shell operations, git operations)
- Assertions verification
- Timestamps and environment information

Test reports are saved in the `ansible_tests/logs/` directory with a timestamp in the filename.

The Ansible tests cover:
- File operations (create, read, update, delete)
- Directory operations (create, list, delete)
- Shell command execution
- Git operations (comprehensive):
  - Repository initialization
  - Status checking
  - Adding and committing files
  - Branch creation and checkout
  - Merging branches
  - Viewing commit history
- Error handling (edge cases):
  - Non-existent directories and files
  - Invalid Git repositories and branches
  - Invalid shell commands
  - Proper error response validation
- Health check endpoints

#### Testing through APILama Gateway

The Ansible tests are designed to test SheLLama through the APILama gateway, which is the recommended way to access SheLLama in production. The APILama gateway adds the `/api/shellama` prefix to all SheLLama endpoints.

To run the tests, both the APILama gateway and SheLLama service must be running:

```bash
# In one terminal, start the APILama gateway
cd ../apilama
make run

# In another terminal, start the SheLLama service
cd ../shellama
make run

# Then run the tests
make ansible-test
```

Test results are logged to `ansible_tests/logs/` for debugging and auditing purposes.

### Code Quality

```bash
# Format code with Black
black shellama tests

# Lint code with Flake8
flake8 shellama tests

# Type checking with MyPy
mypy shellama
```

### Docker Development

```bash
# Build the Docker image
docker build -t shellama .

# Run the container
docker run -p 8002:8002 shellama
```

## License

MIT
