import os
import shutil
import re
import logging
import sys

# Set up basic logging configuration
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def create_file(file_path: str, content: str) -> str:
    """Create a file with the given content."""
    try:
        # Create directory if needed
        dir_name = os.path.dirname(file_path)
        if dir_name:
            os.makedirs(dir_name, exist_ok=True)
        with open(file_path, 'w') as f:
            f.write(content)
        logging.info(f"Created file {file_path}")
        return f"File {file_path} created successfully."
    except Exception as e:
        logging.error(f"Error creating file {file_path}: {e}")
        return f"Failed to create file {file_path}: {e}"

def move_file(file_path: str, destination: str) -> str:
    """Move a file to a new destination."""
    try:
        dir_name = os.path.dirname(destination)
        if dir_name:
            os.makedirs(dir_name, exist_ok=True)
        shutil.move(file_path, destination)
        logging.info(f"Moved file {file_path} to {destination}")
        return f"File {file_path} moved to {destination} successfully."
    except Exception as e:
        logging.error(f"Error moving file {file_path} to {destination}: {e}")
        return f"Failed to move file {file_path} to {destination}: {e}"

def read_file(file_path: str) -> str:
    """Read the content of a file."""
    try:
        with open(file_path, 'r') as f:
            data = f.read()
        logging.info(f"Read file {file_path}")
        return data
    except Exception as e:
        logging.error(f"Error reading file {file_path}: {e}")
        return f"Failed to read file {file_path}: {e}"

def delete_file(file_path: str) -> str:
    """Delete the specified file."""
    try:
        os.remove(file_path)
        logging.info(f"Deleted file {file_path}")
        return f"File {file_path} deleted successfully."
    except Exception as e:
        logging.error(f"Error deleting file {file_path}: {e}")
        return f"Failed to delete file {file_path}: {e}"

def update_file(file_path: str, content: str) -> str:
    """Update an existing file with new content."""
    try:
        if not os.path.exists(file_path):
            return f"File {file_path} does not exist."
        with open(file_path, 'w') as f:
            f.write(content)
        logging.info(f"Updated file {file_path}")
        return f"File {file_path} updated successfully."
    except Exception as e:
        logging.error(f"Error updating file {file_path}: {e}")
        return f"Failed to update file {file_path}: {e}"

def copy_file(file_path: str, destination: str) -> str:
    """Copy a file to a new location."""
    try:
        if not os.path.exists(file_path):
            return f"Source file {file_path} does not exist."
        dest_dir = os.path.dirname(destination)
        if dest_dir:
            os.makedirs(dest_dir, exist_ok=True)
        shutil.copy(file_path, destination)
        logging.info(f"Copied file {file_path} to {destination}")
        return f"File {file_path} copied to {destination} successfully."
    except Exception as e:
        logging.error(f"Error copying file {file_path} to {destination}: {e}")
        return f"Failed to copy file {file_path} to {destination}: {e}"

def parse_command(user_input: str) -> tuple:
    """Parse user input into command components using regex patterns"""
    ui = user_input.strip()
    operation = file_path = destination = content = None
    
    # CREATE command
    match = re.match(r'create file\s+"?([^"]+)"?\s+with content\s+"?([^"]*)"?', ui, re.IGNORECASE)
    if not match:
        match = re.match(r'create\s+"?([^"]+)"?\s+with content\s+"?([^"]*)"?', ui, re.IGNORECASE)
    if match:
        operation = "create"
        file_path = match.group(1).strip()
        content = match.group(2).strip()
        return operation, file_path, destination, content

    # MOVE command
    match = re.match(r'move file\s+"?([^"]+)"?\s+to\s+"?([^"]+)"?', ui, re.IGNORECASE)
    if not match:
        match = re.match(r'move\s+"?([^"]+)"?\s+to\s+"?([^"]+)"?', ui, re.IGNORECASE)
    if match:
        operation = "move"
        file_path = match.group(1).strip()
        destination = match.group(2).strip()
        return operation, file_path, destination, content

    # READ command
    match = re.match(r'read file\s+"?([^"]+)"?', ui, re.IGNORECASE)
    if not match:
        match = re.match(r'read\s+"?([^"]+)"?', ui, re.IGNORECASE)
    if match:
        operation = "read"
        file_path = match.group(1).strip()
        return operation, file_path, destination, content

    # DELETE command
    match = re.match(r'delete file\s+"?([^"]+)"?', ui, re.IGNORECASE)
    if not match:
        match = re.match(r'delete\s+"?([^"]+)"?', ui, re.IGNORECASE)
    if match:
        operation = "delete"
        file_path = match.group(1).strip()
        return operation, file_path, destination, content

    # COPY command
    match = re.match(r'copy file\s+"?([^"]+)"?\s+to\s+"?([^"]+)"?', ui, re.IGNORECASE)
    if not match:
        match = re.match(r'copy\s+"?([^"]+)"?\s+to\s+"?([^"]+)"?', ui, re.IGNORECASE)
    if match:
        operation = "copy"
        file_path = match.group(1).strip()
        destination = match.group(2).strip()
        return operation, file_path, destination, content

    # UPDATE command
    match = re.match(r'update file\s+"?([^"]+)"?\s+with content\s+"?([^"]*)"?', ui, re.IGNORECASE)
    if not match:
        match = re.match(r'update\s+"?([^"]+)"?\s+with content\s+"?([^"]*)"?', ui, re.IGNORECASE)
    if match:
        operation = "update"
        file_path = match.group(1).strip()
        content = match.group(2).strip()
        return operation, file_path, destination, content

    return None, None, None, None

def execute_command(user_input: str) -> str:
    """Parse and execute the user's command"""
    operation, file_path, destination, content = parse_command(user_input)
    
    if not operation:
        return "Command not recognized. Available commands:\n" \
               "  create <path> with content <text>\n" \
               "  move <source> to <destination>\n" \
               "  read <path>\n" \
               "  delete <path>\n" \
               "  copy <source> to <destination>\n" \
               "  update <path> with content <text>"

    if operation == "create":
        if file_path and content is not None:
            return create_file(file_path, content)
        else:
            return "Invalid create command. Please specify file path and content."
    elif operation == "move":
        if file_path and destination:
            return move_file(file_path, destination)
        else:
            return "Invalid move command. Please specify source and destination."
    elif operation == "read":
        if file_path:
            return read_file(file_path)
        else:
            return "Invalid read command. Please specify file path."
    elif operation == "delete":
        if file_path:
            return delete_file(file_path)
        else:
            return "Invalid delete command. Please specify file path."
    elif operation == "copy":
        if file_path and destination:
            return copy_file(file_path, destination)
        else:
            return "Invalid copy command. Please specify source and destination."
    elif operation == "update":
        if file_path and content is not None:
            return update_file(file_path, content)
        else:
            return "Invalid update command. Please specify file path and new content."
    else:
        return "Unsupported operation."

def print_help():
    """Print available commands"""
    print("File Operations Agent - Available Commands:")
    print("  create <file_path> with content <text>")
    print("  move <source_path> to <destination_path>")
    print("  read <file_path>")
    print("  delete <file_path>")
    print("  copy <source_path> to <destination_path>")
    print("  update <file_path> with content <text>")
    print("  help - Show this help message")
    print("  exit - Quit the program")

def main():
    if len(sys.argv) > 1:
        # Non-interactive mode: execute single command
        user_input = " ".join(sys.argv[1:])
        result = execute_command(user_input)
        print(result)
    else:
        # Interactive mode
        print("File Operations Agent. Type 'help' for commands or 'exit' to quit.")
        while True:
            user_input = input("\n> ").strip()
            if not user_input:
                continue
                
            cmd = user_input.lower()
            if cmd in ["exit", "quit"]:
                print("Exiting.")
                break
                
            if cmd == "help":
                print_help()
                continue
                
            result = execute_command(user_input)
            print(result)

if __name__ == "__main__":
    main()