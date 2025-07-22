import os
import shutil
from app.history import HistoryManager
from app.lexical.token import TokenType
from typing import List

class CommandResult:
    def __init__(self, exit_code=0, stdout="", stderr=""):
        self.exit_code = exit_code
        self.stdout = stdout
        self.stderr = stderr

    def __repr__(self):
        return f"CommandResult(exit_code={self.exit_code}, stdout='{self.stdout}', stderr='{self.stderr}')"

class BaseCommand:
    def execute(self, args: List[TokenType]) -> CommandResult:
        # Override in subclasses
        pass
        
    def get_help(self) -> str:
        # Return help text
        pass
        
    def validate_args(self, args: List[TokenType]) -> bool:
        # Check if arguments are valid
        pass


class PwdCommand(BaseCommand):
    def execute(self, args) -> CommandResult:
        try:
            cwd = os.getcwd() + "\n"
            return CommandResult(exit_code=0, stdout=cwd)
        except Exception as e:
            return CommandResult(exit_code=1, stderr=str(e))

class TypeCommand(BaseCommand):
    def execute(self, args) -> CommandResult:
        if not args:
            return CommandResult(exit_code=1, stderr="type: missing argument")
        
        builtin = args[0].value
        try:
            if CommandRegistry().is_builtin_command(builtin):
                return CommandResult(exit_code=0, stdout=f"{builtin} is a shell builtin\n")
            elif path := shutil.which(builtin):
                return CommandResult(exit_code=0, stdout=f"{builtin} is {path}\n")
            else:
                return CommandResult(exit_code=0, stdout=f"{builtin}: not found\n")
        except Exception as e:
            return CommandResult(exit_code=1, stderr=str(e))
    

class ChangeDirCommand(BaseCommand):
    def execute(self, args) -> CommandResult:
        if not args:
            return CommandResult(exit_code=1, stderr="cd: missing argument\n")
        
        dir = args[0].value

        if dir == "~":
            dir = os.environ.get("HOME")
        # change the cwd to dir
        try:
            os.chdir(dir)
        except FileNotFoundError:
            return CommandResult(exit_code=1, stderr=f"cd: {dir}: No such file or directory\n")
        
        return CommandResult(exit_code=0)

class ExitCommand(BaseCommand):
    def execute(self, args) -> CommandResult:
        # Exit the shell
        
        return CommandResult(exit_code=-1)
    
    def get_help(self) -> str:
        return "Exit the shell."
    
class EchoCommand(BaseCommand):
    def execute(self, args) -> CommandResult:
        if not args:
            return CommandResult(exit_code=0, stdout="")
        
        # Join arguments with spaces
        output = " ".join(arg.value for arg in args) + "\n"
        return CommandResult(exit_code=0, stdout=output)
    
    def get_help(self) -> str:
        return "Echo the arguments to standard output."
    
class HistoryCommand(BaseCommand):
    def __init__(self, history_manager):
        """
        Initialize history command with reference to history manager
        
        Args:
            history_manager: HistoryManager instance
        """
        self.history_manager = history_manager

    def execute(self, args) -> CommandResult:
        # Return the command history
        try:
            # Parse arguments
            if not args:
                # Show all history
                count = None
            elif len(args) == 1:
                try:
                    count = int(args[0].value)
                    if count <= 0:
                        return CommandResult(exit_code=1, stdout="", stderr="history: invalid count: must be positive integer\n")
                except ValueError:
                    return CommandResult(exit_code=1, stdout="", stderr=f"history: invalid argument: '{args[0]}'\n")
            else:
                return CommandResult(exit_code=1, stdout="", stderr="history: too many arguments\nUsage: history [n]\n")
            
            # Get history and format output
            history_list = self.history_manager.get_history(count)
            
            if not history_list:
                output = "No commands in history\n"
            else:
                output = ""
                for index, command in history_list:
                    output += f"{index:4d}  {command}\n"
            
            return CommandResult(exit_code=0, stdout=output, stderr="")
            
        except Exception as e:
            return CommandResult(exit_code=1, stdout="", stderr=f"history: error: {e}\n")

    
class CommandRegistry:
    def __init__(self, history_manager: HistoryManager = None):
        self.built_ins = {}
        self.history_manager = history_manager

        # Register built-in commands
        self.register_builtin("pwd", PwdCommand)
        self.register_builtin("type", TypeCommand)
        self.register_builtin("cd", ChangeDirCommand)
        self.register_builtin("exit", ExitCommand)
        self.register_builtin("echo", EchoCommand)
        self.register_builtin("history", HistoryCommand, history_manager=history_manager)
    
    def register_builtin(self, name: str, command_class: BaseCommand, **kwargs):
        # Check if command_class is already an instance
        if isinstance(command_class, BaseCommand):
            self.built_ins[name] = command_class
        else:
            # Instantiate the class with optional kwargs
            self.built_ins[name] = command_class(**kwargs)
        
    def get_command(self, name: str):
        # Look up command (built-ins first, then external)
        if name in self.built_ins:
            return self.built_ins[name]
        else:
            return None
        
    def is_builtin_command(self, name: str) -> bool:
        if name in self.built_ins:
            return True

    def is_external_command(self, name: str) -> bool:
        # Check if command exists in PATH

        if not name in self.built_ins:
            return True