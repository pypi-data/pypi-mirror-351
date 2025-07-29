# Hello Package

A simple Python package that provides functions to greet users with nicely formatted names.

## Features

- Capitalizes the first letter of each part of a name.
- Prints a personalized greeting message.

## Installation

You can install the package using pip. Run the following command:

```bash
pip install hello_package
```

## Usage

Here’s a quick example of how to use the `hello_package`:

```python
from hello_package.hello import nice_name, say_hello

# Get a nicely formatted name
formatted_name = nice_name("   john doe   ")
print(formatted_name)  # Output: "John Doe"

# Print a greeting
say_hello(formatted_name)  # Output: "Hello *John Doe*"
```
