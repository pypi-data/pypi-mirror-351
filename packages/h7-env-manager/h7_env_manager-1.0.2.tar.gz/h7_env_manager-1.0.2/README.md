# h7-env-manager

Core utility classes for environment variable management in Python projects.

## Installation

```bash
pip install h7-env-manager
```

## Features

- Centralized environment variable management
- Support for required and optional environment variables
- Automatic loading of .env files

## Usage

```python
from h7_env_manager import EnvManager

# Get required environment variable (raises ValueError if not found)
api_key = EnvManager.get_required_env_var("API_KEY")

# Get optional environment variable with default value
debug_mode = EnvManager.get_optional_env_var("DEBUG_MODE", "false")

```

## Requirements

- Python 3.7+
- python-dotenv
- h7-file-finder

## License

MIT License - Copyright (c) 2025 Roger Mori
