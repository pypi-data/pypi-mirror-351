# `escape-path` - Cross-Platform Path Escaping for Python

A lightweight Python utility to safely escape paths for command-line usage. It automatically adapts to NT or POSIX, ensuring paths are correctly escaped.

## Installation

```bash
pip install escape-path
```

## Quick Start

### Basic Usage

On NT:

```python
from escape_path import escape_path

path = r"C:\Program Files\My App\file.txt"
escaped = escape_path(path)
print(escaped)
# "C:\Program Files\My App\file.txt"
```


On POSIX:

```python
from escape_path import escape_path

path = '/home/user/My Documents/file.txt'
escaped = escape_path(path)
print(escaped)
# '/home/user/My Documents/file.txt'
```

### Platform-Specific Escaping

```python
from escape_path import escape_nt_path, escape_posix_path

nt_path = escape_nt_path(r"C:\My Files\data.csv")   # "C:\My Files\data.csv"
posix_path = escape_posix_path("/tmp/my file.log")  # '/tmp/my file.log'
```

## Contributing

Contributions are welcome! Please open an issue or submit a pull request for any improvements.

## License

MIT License. See [LICENSE](LICENSE) for more information.