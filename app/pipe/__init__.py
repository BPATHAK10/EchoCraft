import subprocess
import sys
from io import StringIO

class PipeProcessor:
    """Handles execution of command pipelines"""
    
    def __init__(self, command_registry):
        self.registry = command_registry
    
    def execute_pipeline(self, pipe_commands):
        """
        Execute a pipeline of commands
        
        Args:
            pipe_commands: List of PipeCommand objects
            
        Returns:
            tuple: (exit_code, final_stdout, final_stderr)
        """
        if len(pipe_commands) == 1:
            # Single command, no pipe needed
            return self._execute_single_command(pipe_commands[0], input_data="")
        
        # Execute pipeline
        current_input = ""
        
        for i, cmd in enumerate(pipe_commands):
            is_last = (i == len(pipe_commands) - 1)
            
            exit_code, stdout, stderr = self._execute_single_command(cmd, current_input)
            
            if exit_code != 0:
                # Command failed, stop pipeline
                return exit_code, stdout, stderr
            
            if is_last:
                # Last command, return its output
                return exit_code, stdout, stderr
            else:
                # Use this command's output as next command's input
                current_input = stdout
        
        return 0, "", ""
    
    def _execute_single_command(self, pipe_command, input_data):
        """
        Execute a single command with given input
        
        Returns:
            tuple: (exit_code, stdout, stderr)
        """
        command_name = pipe_command.command.value
        args = [arg.value for arg in pipe_command.args]
        
        # Check if it's a built-in command
        command = self.registry.get_command(command_name)
        
        if command:
            # Built-in command - simulate input by temporarily changing stdin
            if input_data:
                # For built-in commands, we might need special handling
                # For now, most built-ins don't read from stdin
                pass
            
            result = command.execute(pipe_command.args)
            return result.exit_code, result.stdout, ""
        
        elif self.registry.is_external_command(command_name):
            # External command - use subprocess with pipes
            try:
                cmd_list = [command_name] + args
                
                result = subprocess.run(
                    cmd_list,
                    input=input_data,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    check=False  # Don't raise exception on non-zero exit
                )
                
                return result.returncode, result.stdout, result.stderr
                
            except FileNotFoundError:
                return 1, "", f"{command_name}: command not found"
            except Exception as e:
                return 1, "", f"{command_name}: {str(e)}"
        
        else:
            return 1, "", f"{command_name}: command not found"