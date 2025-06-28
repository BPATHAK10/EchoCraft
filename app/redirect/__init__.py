import os
from typing import List

class RedirectProcessor:
    """Handles applying redirect instructions to command output"""
    
    def apply_redirects(self, output: str, error_output: str, redirect_instructions: List) -> tuple:
        """
        Apply redirect instructions to command output
        
        Args:
            output: The command's output string
            redirect_instructions: List of RedirectInstruction objects
            
        Returns:
            tuple: (success: bool, final_output: str, error_message: str)
        """
        # If no redirects, return output as-is
        if not redirect_instructions:
            return True, output, ""
        
        # For now, handle only output redirects (>, >>)
        final_stdout = output  # What gets printed to terminal
        final_stderr = error_output  # What gets printed to terminal for stderr
        
        for instruction in redirect_instructions:
            if instruction.stream == 'stdout':
                if instruction.redirect_type in ('>', '1>'):
                    # Output redirect - write to file (overwrite)
                    success, error = self._write_to_file(output, instruction.target, mode='w')
                    if not success:
                        return False, "", error
                    final_stdout = ""  # Don't print to terminal
                    
                elif instruction.redirect_type in ('>>', '1>>'):
                    # Append redirect - append to file
                    success, error = self._write_to_file(output, instruction.target, mode='a')
                    if not success:
                        return False, "", error
                    final_stdout = ""  # Don't print to terminal

            elif instruction.stream == 'stderr':
                if instruction.redirect_type in ('2>', '2>>'):
                    # Redirect stderr to file
                    success, error = self._write_to_file(error_output, instruction.target, mode='w' if instruction.redirect_type == '2>' else 'a')
                    if not success:
                        return False, "", error
                    final_stderr = ""
        
        return True, final_stdout, final_stderr, ""
    
    def _write_to_file(self, content: str, filename: str, mode: str) -> tuple:
        """
        Write content to file
        
        Returns:
            tuple: (success: bool, error_message: str)
        """
        try:
            with open(filename, mode) as f:
                f.write(content)
            return True, ""
        except PermissionError:
            return False, f"Permission denied: {filename}"
        except FileNotFoundError:
            return False, f"No such file or directory: {os.path.dirname(filename)}"
        except Exception as e:
            return False, f"Error writing to {filename}: {str(e)}"