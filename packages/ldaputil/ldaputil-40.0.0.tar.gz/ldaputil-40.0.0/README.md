# ldaputil

A simple test Python package that prints "Hello World" during installation.

## Description

This is a minimal test package created to demonstrate Python packaging. The package doesn't provide any real functionality - it's designed to print a greeting message when installed and imported.

## Installation

```bash
pip install ldaputil
```

## Usage

```python
import ldaputil

# The package will print "Hello World" message when imported

# You can also use the hello_world function
ldaputil.hello_world()

# Or use the greet function from main module
from ldaputil.main import greet
greet("Python Developer")
```

## Features

- Prints greeting message during installation/import
- Simple hello_world() function
- Greet function with customizable name
- Minimal dependencies

## Development

This package was created as a learning exercise for Python packaging.

## License

MIT License 