# tinymsg

A lightweight serialization library for Python using MessagePack with type-safe Pydantic models. This Python instance of the tinymsg serialization library is directly compatible with [tinymsg-cpp](https://github.com/alangshur/tinymsg-cpp) and tinymsg-rs (coming soon).

## Features

- **Type-safe**: Built on Pydantic for automatic validation and type checking
- **Fast**: Uses MessagePack for efficient binary serialization
- **Simple**: Minimal boilerplate - just inherit from `Message`
- **Nested support**: Handles nested objects, lists, and dicts automatically

## Installation

```bash
uv add tinymsg       # using uv
pip install tinymsg  # using pip
```

## Quick Start

```python
from tinymsg import Message

class Person(Message):
    name: str
    age: int
    email: str

class Team(Message):
    name: str
    members: list[Person]
    active: bool = True

# Create objects
alice = Person(name="Alice", age=30, email="alice@example.com")
bob = Person(name="Bob", age=25, email="bob@example.com")
team = Team(
    name="Engineering", 
    members=[alice, bob]
)

# Serialize to bytes
data = team.pack()

# Deserialize from bytes
restored_team = Team.unpack(data)

print(restored_team.members[0].name)  # "Alice"
```

## Development

### Recommended Workflow (using uv)

[uv](https://github.com/astral-sh/uv) is a fast Python package manager and virtualenv manager. Install it first:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

#### Setup Development Environment

```bash
# Create virtual environment and install all dependencies (including dev dependencies)
uv sync --extra dev

# Alternative: Create venv manually then install
uv venv
source .venv/bin/activate
uv pip install -e ".[dev]"
```

#### Development Commands

```bash
# Run tests
uv run pytest

# Run tests with coverage report
uv run pytest --cov=tinymsg --cov-report=html

# Run specific test
uv run pytest tests/test_tinymsg.py::TestBasicSerialization::test_simple_message_roundtrip

# Check code with ruff (linting)
uv run ruff check .

# Auto-fix linting issues
uv run ruff check --fix .

# Format code with ruff
uv run ruff format .
```

#### Other Useful Commands

```bash
# Add a new dependency
uv add requests

# Add a new dev dependency
uv add --dev mypy

# Update dependencies
uv sync

# Show installed packages
uv pip list
```

### Traditional Workflow (using pip)

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate

# Install dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Lint and format code
ruff check .
ruff format .
```
