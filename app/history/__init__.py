import os
import readline
import atexit

class HistoryManager:
    """Simple history manager for shell commands using readline"""
    
    def __init__(self):
        """
        Initialize history manager
        """
        self._setup_readline()
        self.load_history()
        
        # Register automatic save on exit
        atexit.register(self.save_history)
    
    def _setup_readline(self):
        """Configure readline for history support"""
        # Disable Python's automatic history to avoid conflicts
        try:
            readline.set_auto_history(False)
        except AttributeError:
            # set_auto_history not available in older Python versions
            pass
        
        # Enable history
        readline.set_history_length(50)  # Keep last 50 commands
        
        # Set up basic key bindings for arrow keys
        readline.parse_and_bind("\\e[A: previous-history")  # Up arrow
        readline.parse_and_bind("\\e[B: next-history")      # Down arrow
    
    def load_history(self):
        """Load command history from file if it exists"""
        try:
            readline.clear_history()
            readline.read_history_file()

        except (FileNotFoundError, PermissionError) as e:
            print(f"Note: Could not load history file: {e}")
    
    def save_history(self):
        """Save command history to file"""
        try:
            readline.write_history_file()
        except (PermissionError, OSError) as e:
            print(f"Warning: Could not save history: {e}")
    
    def add_command(self, command: str):
        """Add a command to history"""
        # Only add non-empty commands
        if command and command.strip():
            cmd = command.strip()
            
            # Avoid duplicate consecutive commands
            history_len = readline.get_current_history_length()
            if history_len == 0 or readline.get_history_item(history_len) != cmd:
                readline.add_history(cmd)
    
    def get_input(self, prompt="$ "):
        """Get user input with history support"""
        return input(prompt)
    
    def get_history_length(self):
        """Get current number of commands in history"""
        return readline.get_current_history_length()
    
    def clear_history(self):
        """Clear all command history"""
        readline.clear_history()

    def get_history(self, count=None) -> list:
        """Get command history"""
        history_length = readline.get_current_history_length()
        
        if history_length == 0:
            return []
        
        # Determine how many commands to return
        if count is None:
            start_idx = 1
        else:
            start_idx = max(1, history_length - count + 1)
        
        history_list = []
        for i in range(start_idx, history_length + 1):
            command = readline.get_history_item(i)
            if command:
                history_list.append((i, command))
        
        return history_list
    
    def print_history(self, count=None):
        """Print command history to stdout"""
        history_list = self.get_history(count)
        
        if not history_list:
            print("No commands in history")
            return
        
        for index, command in history_list:
            print(f"{index:4d}  {command}")