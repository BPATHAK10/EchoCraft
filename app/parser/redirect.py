from typing import List
from app.lexical.token import TokenType

class RedirectInstruction:
    """Represents a single redirect instruction"""
    def __init__(self, redirect_type, target, stream='stdout'):
        self.redirect_type = redirect_type
        self.target = target  
        self.stream = stream 
        self.append = redirect_type.endswith('>>')

    def __str__(self):
        return f"RedirectInstruction({self.redirect_type} -> {self.target})"

class RedirectParser:
    """Parses tokens into command tokens and redirect instructions"""
    
    def __init__(self):
        # Define which token types are redirect operators
        self.redirect_operators = {
            'REDIRECT_OUT': '>',
            'REDIRECT_APPEND': '>>',
            'REDIRECT_STDOUT': '1>',
            'REDIRECT_STDOUT_APPEND': '1>>',
            'REDIRECT_STDERR': '2>',
            'REDIRECT_STDERR_APPEND': '2>>'
        }
    
    def parse(self, tokens: List[TokenType]) -> tuple:
        """Split tokens into command_tokens and redirect_instructions"""
        command_tokens = []
        redirect_instructions = []
        
        i = 0
        while i < len(tokens):
            token = tokens[i]
            token_type_name = token.type.name
            
            # Check if this is a redirect operator
            if token_type_name in self.redirect_operators:
                # We need the next token as the target
                if i + 1 >= len(tokens):
                    raise ValueError(f"Redirect operator '{self.redirect_operators[token_type_name]}' missing target")
                
                target_token = tokens[i + 1]
                redirect_type = self.redirect_operators[token_type_name]

                stream = self._get_stream_type(token_type_name)
                
                # Create redirect instruction
                instruction = RedirectInstruction(redirect_type, target_token.value, stream)
                redirect_instructions.append(instruction)
                
                # Skip both the operator and target
                i += 2
            else:
                # Regular command token
                command_tokens.append(token)
                i += 1
        
        return command_tokens, redirect_instructions
    
    def has_redirects(self, tokens: List[TokenType]) -> bool:
        """Quick check if tokens contain any redirects"""
        for token in tokens:
            if token.type.name in self.redirect_operators:
                return True
        return False
    
    def _get_stream_type(self, token_type_name: str) -> str:
        """Determine which stream the redirect affects"""
        if token_type_name in ['REDIRECT_STDERR', 'REDIRECT_STDERR_APPEND']:
            return 'stderr'
        else:
            return 'stdout'