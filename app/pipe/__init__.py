import subprocess
from typing import List, Tuple
from app.parser.redirect import RedirectParser
from app.redirect import RedirectProcessor
from app.commands import CommandResult
from app.lexical.token import Token, TokenType
from app.parser.pipe import PipeCommand

class PipeProcessor:
    """Handles execution of command pipelines"""
    
    def __init__(self, command_registry):
        self.registry = command_registry
    
    def execute_pipeline(self, pipe_commands: List[PipeCommand]) -> Tuple[int, str, str]:
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
    
    def _execute_single_command(self, pipe_command: PipeCommand, input_data: str) -> Tuple[int, str, str]:
        """
        Execute a single command with given input
        
        Returns:
            tuple: (exit_code, stdout, stderr)
        """

        redirect_parser = RedirectParser()
        redirect_processor = RedirectProcessor()
        tokens = [pipe_command.command] + pipe_command.args

        # Parse the single command for redirect instruction
        command_tokens, redirect_instructions = redirect_parser.parse(tokens)

        # Get the commands from the redirect parser
        command_name = command_tokens[0].value
        args = command_tokens[1:]
        
        # Check if it's a built-in command
        command = self.registry.get_command(command_name)
        
        # execute commands
        if self.registry.is_external_command(command_name):
            # External command - use subprocess with pipes
            try:
                cmd_list = [command_name] + [arg.value for arg in args]
                
                result = subprocess.run(
                    cmd_list,
                    input=input_data,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    check=False  # Don't raise exception on non-zero exit
                )
                
                result = CommandResult(
                    exit_code=result.returncode,
                    stdout=result.stdout,
                    stderr=result.stderr
                )
            
            except FileNotFoundError:
                return 1, "", f"{command_name}: command not found\n"
            except Exception as e:
                return 1, "", f"{command_name}: {str(e)}"
        
        else:
            # add the input data to args if available
            if input_data:
                args.append(Token(type=TokenType.WORD, value=input_data))
            result = command.execute(args)

    
        if redirect_parser.has_redirects(tokens):
            success, final_output, final_stderr, error_message = redirect_processor.apply_redirects(
                result.stdout,
                result.stderr,
                redirect_instructions
            )

            if not success:
                return 1, "", error_message
            else:
                return result.exit_code, final_output, final_stderr
        
        return result.exit_code, result.stdout, result.stderr
            
        