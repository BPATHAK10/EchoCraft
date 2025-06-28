import sys
import subprocess
from app.lexical.token import TokenType
from app.commands import CommandResult, CommandRegistry
from app.lexical import MyLex
from app.parser import Parser
from app.redirect import RedirectProcessor

def main():
    registry = CommandRegistry()
    parser = Parser()
    redirect_processor = RedirectProcessor()

    while True:
        sys.stdout.write("$ ")

        # Wait for user input
        raw_input = input()

        # Tokenize
        tokens = MyLex(raw_input).parse()

        if not tokens:
            continue
        
        # print("Tokens:")
        # for p in tokens:
        #     print(p)

        # Parse tokens into command and arguments
        command_tokens, redirect_instructions = parser.parse(tokens)
        
        command_name = command_tokens[0].value if tokens else ''
        args = command_tokens[1:] if len(command_tokens) > 1 else []

        # Look up the command
        command = registry.get_command(command_name)

        if command:
            result = command.execute(args)
            # stdout_output = result.stdout
            # stderr_output = result.stderr
        elif registry.is_external_command(command_name):
            try:
                raw_cmd = command_tokens[0].value

                if raw_cmd.startswith(("'", '"')) and raw_cmd.endswith(("'", '"')):
                    raw_command_name = raw_cmd[1:-1]
                else:
                    raw_command_name = raw_cmd

                # separate the external command and its arguments
                ext_command = [raw_command_name] + [
                    arg.value for arg in args if arg.type in (TokenType.WORD, TokenType.COMMAND)
                ]

                # Execute the command using subprocess
                subprocess_result = subprocess.run(
                    ext_command,
                    # shell=True, 
                    capture_output=True, 
                    text=True, 
                    check=True
                )
                result = CommandResult(
                    exit_code=subprocess_result.returncode,
                    stdout=subprocess_result.stdout,
                    stderr=subprocess_result.stderr,
                )
            except FileNotFoundError as e:
                result = CommandResult(exit_code=1, stderr=f"{command_name}: command not found\n")
            except subprocess.CalledProcessError as e:
                if e.returncode == 127:
                    result = CommandResult(exit_code=1, stderr=f"{command_name}: command not found\n")
                else:
                    result = CommandResult(exit_code=1, stderr=e.stderr, stdout=e.stdout)

        if not parser.has_redirects(tokens):
            if result.exit_code == 1: # has error
                print(result.stderr, end="")
            elif result.exit_code == -1:
                break
            else:
                if result.stdout:
                    print(result.stdout, end="")
        else:
            success, final_output, final_stderr, error_message = redirect_processor.apply_redirects(
                # stdout_output, stderr_output, redirect_instructions
                result.stdout, result.stderr, redirect_instructions
                )
            if not success:
                print(error_message, end="")
            else:
                if final_output:
                    print(final_output, end="")
                if final_stderr:
                    print(final_stderr, end="")

if __name__ == "__main__":
    main()
