# typecli

## Overview

`typecli` is a Python library that provides a type-annotated interface for creating command-line argument parsers. It builds on top of `argparse` but offers a more intuitive and type-safe way to define command-line arguments using Python class syntax and type hints.

## Key Features

- Type-annotated argument definitions
- Automatic conversion of input values to specified types
- Support for positional and optional arguments
- Built-in support for common types including:
  - Primitive types (`bool`, `int`, `str`, etc.)
  - Optional types (`Optional[T]`)
  - Union types (`Union[T1, T2]`)
  - Lists (`list[T]`)
  - Enums (`enum.Enum`, `enum.IntEnum`, `enum.Flag`)
  - File I/O (`TextIO`)
- Default values and help text support
- Direct instantiation of argument classes

## Basic Usage

### Defining Arguments

Create a class that inherits from `typecli.Parser` and define your arguments as class variables with type annotations:

```python
from typing import Optional
import typecli

class Args(typecli.Parser):
    files: list[str] = typecli.arg(positional=True)
    name: Optional[str]
    verbose: bool = typecli.arg(help="Enable verbose output")
    count: int = typecli.arg(short="c", default=1)
```

### Parsing Arguments

Use the `parse()` class method to parse command-line arguments:

```python
args = Args.parse(["--verbose", "-c", "5", "file1.txt", "file2.txt"])
```

### Accessing Values

Access the parsed values as attributes of the args object:

```python
print(args.files)    # ["file1.txt", "file2.txt"]
print(args.name)     # None
print(args.verbose)  # True
print(args.count)    # 5
```

## Argument Types

### Boolean Flags

Boolean fields automatically become flags that don't require a value:

```python
class Args(typecli.Parser):
    flag: bool

args = Args.parse(["--flag"])  # args.flag == True
```

### Optional Arguments

Use `Optional[T]` to indicate an argument that can be omitted:

```python
class Args(typecli.Parser):
    name: Optional[str]

args = Args.parse([])  # args.name == None
```

### List Arguments

Use `list[T]` to accept multiple values:

```python
class Args(typecli.Parser):
    numbers: list[int]

args = Args.parse(["--numbers", "1", "2", "3"])  # args.numbers == [1, 2, 3]
```

### Positional Arguments

Use `positional=True` to make an argument positional:

```python
class Args(typecli.Parser):
    filename: str = typecli.arg(positional=True)

args = Args.parse(["file.txt"])  # args.filename == "file.txt"
```

### Enum Arguments

`typecli` supports both standard Enums and IntEnums:

```python
from enum import Enum, IntEnum, auto

class Color(Enum):
    RED = auto()
    GREEN = auto()
    BLUE = auto()

class Size(IntEnum):
    SMALL = 1
    MEDIUM = 2
    LARGE = 3

class Args(typecli.Parser):
    color: Color
    size: Size

args = Args.parse(["--color", "RED", "--size", "2"])
# args.color == Color.RED
# args.size == Size.MEDIUM
```

### Flag Arguments (Bitmask)

For bitmask-style flags, use `enum.Flag`:

```python
from enum import Flag, auto

class Permissions(Flag):
    READ = auto()
    WRITE = auto()
    EXECUTE = auto()

class Args(typecli.Parser):
    perms: Permissions

args = Args.parse(["--perms", "READ", "WRITE"])
# args.perms == Permissions.READ | Permissions.WRITE
```

### File I/O Arguments

Use `TextIO` type for file arguments:

```python
from typing import TextIO
import sys

class Args(typecli.Parser):
    input: TextIO = typecli.arg(positional=True)
    output: TextIO = typecli.arg(default=sys.stdout, short="o")

args = Args.parse(["-"])  # args.input == sys.stdin
```

## Advanced Features

### Union Types

Support for multiple possible types:

```python
from typing import Union

class Args(typecli.Parser):
    value: Union[int, str]

args1 = Args.parse(["--value", "42"])    # args1.value == 42
args2 = Args.parse(["--value", "text"]) # args2.value == "text"
```

### Customizing Argument Behavior

The `typecli.arg()` function accepts several parameters:

```python
class Args(typecli.Parser):
    name: str = typecli.arg(
        short="n",               # Custom short flag (-n)
        default="default",       # Default value
        help="The name to use",  # Help text
        positional=True          # Make positional
    )
```

### Required Arguments

By default, arguments without defaults are required. To customize error handling:

```python
@typecli.cli(exit_on_error=False)
class Args(typecli.Parser):
    required: str

try:
    Args.parse([])  # Will raise argparse.ArgumentError
except argparse.ArgumentError:
    # Handle error
    pass
```

### Direct Instantiation

You can also create argument objects directly:

```python
args = Args(required="value", optional=None)
```

## Best Practices

1. **Use descriptive names**: Choose clear names for your arguments that indicate their purpose.
2. **Provide help text**: Always include help text for your arguments to make the `--help` output useful.
3. **Set sensible defaults**: Where appropriate, provide default values for optional arguments.
4. **Use type hints consistently**: The library relies on type hints for proper argument parsing.
5. **Group related arguments**: Consider using nested classes or separate parsers for complex command structures.

## Limitations

- The library relies on Python's type hints, which means it requires Python 3.7+ for full functionality.
- Some advanced argparse features may not be directly accessible through this interface.
- Union types are tried in order, which can sometimes lead to unexpected type conversions.
