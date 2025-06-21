"""
My custom lexical analyzer for my shell
"""

from enum import Enum

class State(Enum):
    NORMAL = "normal"
    SINGLE_QUOTE = "single_quote"
    DOUBLE_QUOTE = "double_quote"

class MyLex:
    def __init__(self, input_text: str):
        self.input_text = input_text
        self.state = State.NORMAL
        self.escape = False
        self.current_token = ""
        self.tokens = []
    
    def _finish_token(self):
        """Finish the current token and add it to tokens list"""
        if self.current_token:
            self.tokens.append(self.current_token)
            self.current_token = ""
    
    def _add_char(self, char: str):
        """Add a character to the current token"""
        self.current_token += char
    
    def _process_escaped_char(self, char: str):
        """Handle an escaped character"""
        self._add_char(char)
        self.escape = False
    
    def _handle_escape(self, i: int):
        """Handle escape character (\)"""
        if self.state == State.SINGLE_QUOTE or self.state == State.DOUBLE_QUOTE:
            # Inside single quotes, backslash is literal
            self._add_char("\\")
        else:
            # Set escape flag for next character
            self.escape = True
    
    def _handle_single_quote(self):
        """Handle single quote character"""
        if self.state == State.NORMAL:
            self.state = State.SINGLE_QUOTE
        elif self.state == State.SINGLE_QUOTE:
            self.state = State.NORMAL
        # Inside double quotes, single quote is literal
        elif self.state == State.DOUBLE_QUOTE:
            self._add_char("'")
    
    def _handle_double_quote(self):
        """Handle double quote character"""
        if self.state == State.NORMAL:
            self.state = State.DOUBLE_QUOTE
        elif self.state == State.DOUBLE_QUOTE:
            self.state = State.NORMAL
        # Inside single quotes, double quote is literal
        elif self.state == State.SINGLE_QUOTE:
            self._add_char('"')
    
    def _handle_whitespace(self):
        """Handle whitespace character"""
        if self.state == State.NORMAL:
            # Only finish token on whitespace in normal state
            self._finish_token()
        else:
            # Inside quotes, whitespace is literal
            self._add_char(" ")
    
    def _process(self):
        """Main processing method"""
        i = 0
        while i < len(self.input_text):
            char = self.input_text[i]
            
            # Handle escaped characters first
            if self.escape:
                self._process_escaped_char(char)
                i += 1
                continue
            
            # Handle escape character
            if char == "\\":
                self._handle_escape(i)
                i += 1
                continue
            
            # Handle quote characters
            if char == "'":
                self._handle_single_quote()
                i += 1
                continue
            
            if char == '"':
                self._handle_double_quote()
                i += 1
                continue
            
            # Handle whitespace
            if char == " ":
                self._handle_whitespace()
                i += 1
                continue
            
            # Regular character - add to current token
            self._add_char(char)
            i += 1
        
        # Finish the final token if it exists
        self._finish_token()
    
    def parse(self) -> list[str]:
        """
        Parse the input and return list of tokens [command, arg1, arg2, ...]
        """
        # Reset state for fresh parsing
        self.state = State.NORMAL
        self.escape = False
        self.current_token = ""
        self.tokens = []
        
        # Process the input
        self._process()
        
        # Return empty list if no tokens
        if not self.tokens:
            return []
        
        return self.tokens
    
    def get_command(self) -> str:
        """Get the command (first token)"""
        tokens = self.parse()
        return tokens[0] if tokens else ""
    
    def get_args(self) -> list[str]:
        """Get the arguments (all tokens except first)"""
        tokens = self.parse()
        return tokens[1:] if len(tokens) > 1 else []