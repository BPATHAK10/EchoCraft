from enum import Enum

class TokenType(Enum):
    WORD = "word"
    REDIRECT_OUT = "redirect_out"
    REDIRECT_APPEND = "redirect_append"
    REDIRECT_STDOUT = "redirect_stdout"
    REDIRECT_STDOUT_APPEND = "redirect_stdout_append"
    REDIRECT_STDERR = "redirect_error"
    REDIRECT_STDERR_APPEND = "redirect_error_append"
    PIPE = "pipe"
    COMMAND = "command"
    NUMBER = "number"

class Token:
    def __init__(self, type: TokenType = TokenType.WORD, value: str = "", position: int = 0):
        self.type = type
        self.value = value
        self.position = position

    def __str__(self):
        return f"Token(type={self.type}, value='{self.value}', position={self.position})"