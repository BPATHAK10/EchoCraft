import sys
from app.commands import CommandRegistry
from app.lexical import MyLex
from app.parser.pipe import PipeParser
from app.pipe import PipeProcessor
from app.history import HistoryManager

from app.utils import display_welcome_message

def main():
    history_manager = HistoryManager()
    registry = CommandRegistry(history_manager)
    pipe_parser = PipeParser()
    pipe_processor = PipeProcessor(registry)

    display_welcome_message()

    while True:
        try:
            # Get user input with history support
            raw_input = history_manager.get_input("$ ")

            # Handle empty input
            if not raw_input.strip():
                continue

            # Add command to history before processing
            history_manager.add_command(raw_input)

            # Tokenize
            tokens = MyLex(raw_input).parse()

            if not tokens:
                continue

            # Parse Pipes
            pipe_commands = pipe_parser.parse(tokens)

            # Execute pipeline (automatically handles all commands with timeout)
            exit_code, stdout_output, stderr_output = pipe_processor.execute_pipeline(pipe_commands)
            
            # Handle output and errors
            if exit_code == -1:
                # Exit signal from built-in command
                break
            elif exit_code != 0:
                # Command failed
                if stderr_output:
                    print(stderr_output, end="", file=sys.stderr)
                    sys.stderr.flush()
            
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

        finally:
            # Save history on exit
            pass

if __name__ == "__main__":
    main()