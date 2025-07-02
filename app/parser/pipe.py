from app.lexical.token import TokenType, Token

class PipeCommand:
    """Represents a single command in a pipeline"""
    def __init__(self, command : Token, args : list[Token]):
        self.command = command
        self.args = args
    
    def __repr__(self):
        return f"PipeCommand({self.command_name}, {self.args})"

class PipeParser:
    """Parses tokens into pipeline commands"""
    
    def parse(self, tokens):
        """
        Split tokens into individual commands separated by pipes
        
        Args:
            tokens: List of Token objects from lexer
            
        Returns:
            list: List of PipeCommand objects
        """
        if not tokens:
            return []
        
        if not self.is_pipeline(tokens):
            # Single command, no pipes
            command = tokens[0]
            args = tokens[1:] if len(tokens) > 1 else []
            return [PipeCommand(command, args)]
        
        # Parse pipeline
        commands = []
        current_command_tokens = []
        
        for token in tokens:
            if token.type == TokenType.PIPE:
                # End of current command, start of next
                if current_command_tokens:
                    cmd = current_command_tokens[0]
                    cmd_args = current_command_tokens[1:] if len(current_command_tokens) > 1 else []
                    commands.append(PipeCommand(cmd, cmd_args))
                    current_command_tokens = []
            else:
                current_command_tokens.append(token)
        
        # Add the last command
        if current_command_tokens:
            cmd = current_command_tokens[0]
            cmd_args = current_command_tokens[1:] if len(current_command_tokens) > 1 else []
            commands.append(PipeCommand(cmd, cmd_args))
        
        return commands
    
    def is_pipeline(self, tokens):
        """Check if tokens represent a pipeline"""
        return any(token.type == TokenType.PIPE for token in tokens)