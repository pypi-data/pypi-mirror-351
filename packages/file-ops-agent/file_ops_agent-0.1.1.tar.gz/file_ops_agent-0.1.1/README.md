# File Operations Agent

A command-line tool for performing file operations.

## Installation
```bash
pip install file_ops_agent
```

## Usage
```bash
# Single command execution
agent create test.txt with content "Hello World!"

# Interactive mode
agent
> move file.txt to documents/file.txt
```

## Available Commands
- `create <path> with content <text>`
- `move <source> to <destination>`
- `read <path>`
- `delete <path>`
- `copy <source> to <destination>`
- `update <path> with content <text>`
- `help` - Show commands
- `exit` - Quit interactive mode