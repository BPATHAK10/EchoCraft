import sys
from app.commands import CommandRegistry
from app.lexical import MyLex
from app.parser.pipe import PipeParser
from app.pipe import PipeProcessor

from app.utils import display_welcome_message

def main():
    registry = CommandRegistry()
    pipe_parser = PipeParser()
    pipe_processor = PipeProcessor(registry)

    display_welcome_message()

    while True:
        try:
            sys.stdout.write("$ ")
            sys.stdout.flush()  # Ensure prompt appears immediately

            # Wait for user input
            raw_input = input()

            # Handle empty input
            if not raw_input.strip():
                continue

            # Tokenize
            tokens = MyLex(raw_input).parse()

            if not tokens:
                continue
            
            # Debug output (you can remove these later)
            # print("Tokens:")
            # for p in tokens:
            #     print(p)

            # Parse Pipes
            pipe_commands = pipe_parser.parse(tokens)

            # print("Pipe Commands:")
            # for cmd in pipe_commands:
            #     print(cmd.command, cmd.args)

            # Execute pipeline (automatically handles all commands with timeout)
            exit_code, stdout_output, stderr_output = pipe_processor.execute_pipeline(pipe_commands)
            
            # Handle output and errors
            if exit_code == -1:
                # Exit signal from built-in command (like 'exit')
                break
            elif exit_code != 0:
                # Command failed
                if stderr_output:
                    print(stderr_output, end="", file=sys.stderr)
                    sys.stderr.flush()
                # Some commands output error info to stdout even on failure
                if stdout_output and not stderr_output:
                    print(stdout_output, end="")
                    sys.stdout.flush()
            else:
                # Command succeeded
                if stdout_output:
                    print(stdout_output, end="")
                    sys.stdout.flush()
                    
        except KeyboardInterrupt:
            # Handle Ctrl+C gracefully
            print("\n^C")
            continue
        except EOFError:
            # Handle Ctrl+D (EOF)
            print("\nexit")
            break
        except Exception as e:
            # Handle unexpected errors
            print(f"Shell error: {e}", file=sys.stderr)
            continue

if __name__ == "__main__":
    main()