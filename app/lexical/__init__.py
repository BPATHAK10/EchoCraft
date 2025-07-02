"""
My custom lexical analyzer for my shell
"""

from enum import Enum
from app.lexical.token import Token, TokenType

class State(Enum):
    NORMAL = "normal"
    SINGLE_QUOTE = "single_quote"
    DOUBLE_QUOTE = "double_quote"
    PIPE = "pipe"

class MyLex:
    def __init__(self, input_text: str):
        self.input_text = input_text
        self.state = State.NORMAL
        self.escape = False
        self.current_token = Token()
        self.tokens = []
        self.position = -1
        self.cmd_quote = input_text[0] if input_text[0] in ('"',"'") else ''

        self.escape_chars = {
            "\\",
            '"',
            "$",
            "`",
            "\n"
        }

        self.pipe = "|"

    def _finish_token(self, preserve_quote: bool = False, is_command: bool = False):
        """Finish the current token and add it to tokens list"""
        if self.current_token.value:
            self.position += 1
            self.current_token.position = self.position
            
            # If it's a command, set the type accordingly
            if is_command:
                self.current_token.type = TokenType.COMMAND

            # Handle preserve of quotes in the command
            if preserve_quote:
                self.current_token.value = self.cmd_quote + self.current_token.value + self.cmd_quote
            self.tokens.append(self.current_token)
            self.current_token = Token()

    
    def _add_char(self, char: str):
        """Add a character to the current token"""
        self.current_token.value += char    
    
    def _process_escaped_char(self, char: str):
        """Handle an escaped character"""
        self._add_char(char)
        self.escape = False
    
    def _handle_escape(self, i: int):
        """Handle escape character (\\)"""
        if self.state == State.SINGLE_QUOTE:
            # Inside single quotes, backslash is literal
            self._add_char("\\")
        elif self.state == State.DOUBLE_QUOTE:
            # Inside double quotes, backslash escapes only some next character
            if i + 1 < len(self.input_text):
                next_char = self.input_text[i+1]
                if next_char in self.escape_chars:
                    self.escape = True
                else:
                    self._add_char("\\")
                
            else:
                # If at end of input, treat backslash as literal
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
            if not self.tokens: # This means the first token so its a command
                self._finish_token(preserve_quote=True, is_command=True)
            else:
                self._finish_token()
        elif self.current_token.value and self.state == State.PIPE:
            self._finish_token(is_command=True)
            self.state = State.NORMAL
        elif self.state in (State.SINGLE_QUOTE, State.DOUBLE_QUOTE):
            # Inside quotes, whitespace is literal
            self._add_char(" ")

    def _handle_redirect(self,val,append: bool = False, stdout: bool = True, stderr: bool = False):
        """Handle redirect character """
        if self.state == State.NORMAL:
            if stdout and not append:
                # Finish current token before adding redirect
                self._finish_token()
                self.current_token = (
                    Token(type=TokenType.REDIRECT_OUT, value=val) if val == ">" 
                    else Token(type=TokenType.REDIRECT_STDOUT, value=val))
                self._finish_token()
            
            elif stdout and append:
                self._finish_token()
                self.current_token = Token(type=TokenType.REDIRECT_APPEND, value=val)
                self._finish_token()

            elif stderr and not append:
                # Finish current token before adding redirect
                self._finish_token()
                self.current_token = Token(type=TokenType.REDIRECT_STDERR, value=val)
                self._finish_token()

            elif stderr and append:
                self._finish_token()
                self.current_token = Token(type=TokenType.REDIRECT_STDERR_APPEND, value=val)
                self._finish_token()
            
        else:
            # Inside quotes, val is literal
            self._add_char(val)
        

    def _handle_pipe(self):
        """Handle pipe character"""
        if self.state == State.NORMAL:
            # Finish current token before adding pipe
            self._finish_token()
            self.current_token = Token(type=TokenType.PIPE, value=self.pipe)
            self._finish_token()
            self.state = State.PIPE
        elif self.state == State.SINGLE_QUOTE:
            # Inside quotes, pipe is literal
            self._add_char(self.pipe)

    
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

            # Handle pipe character
            if char == self.pipe:
                self._handle_pipe()
                i += 1
                continue
            
            # Handle redirect out and redirect append
            if char == "1" and i + 1 < len(self.input_text) and self.input_text[i + 1] == ">":
                if i + 2 < len(self.input_text) and self.input_text[i + 2] == ">":
                    self._handle_redirect(val="1>>", append=True)
                    i += 3
                else:
                    self._handle_redirect(val="1>")
                    i += 2
                continue
            if char == ">":
                if i + 1 < len(self.input_text) and self.input_text[i + 1] == ">":
                    self._handle_redirect(val=">>", append=True)
                    i += 2
                else:
                    self._handle_redirect(val=">")
                    i += 1
                continue

            # Handle stderr
            if char == "2" and i + 1 < len(self.input_text) and self.input_text[i + 1] == ">":
                if i + 2 < len(self.input_text) and self.input_text[i + 2] == ">":
                    self._handle_redirect(val="2>>", append=True, stdout=False, stderr=True)
                    i += 3
                else:
                    self._handle_redirect(val="2>", stdout=False ,stderr=True)
                    i += 2
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
        # Check if the last token is a command
        if self.state == State.PIPE and self.current_token.value:
            self._finish_token(is_command=True)
        else:
            self._finish_token()
    
    def parse(self) -> list[str]:
        """
        Parse the input and return list of tokens [command, arg1, arg2, ...]
        """
        # Reset state for fresh parsing
        self.state = State.NORMAL
        self.escape = False
        self.current_token = Token()
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