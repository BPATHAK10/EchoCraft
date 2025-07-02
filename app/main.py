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
        sys.stdout.write("$ ")

        # Wait for user input
        raw_input = input()

        # Tokenize
        tokens = MyLex(raw_input).parse()

        if not tokens:
            continue
        
        print("Tokens:")
        for p in tokens:
            print(p)

        # Parse Pipes
        pipe_commands = pipe_parser.parse(tokens)

        print("Pipe Commands:")
        for cmd in pipe_commands:
            print(cmd.command, cmd.args)

        #####################################

        # Execute pipeline
        exit_code, stdout_output, stderr_output = pipe_processor.execute_pipeline(pipe_commands)
        
        # For now, pipelines don't support redirects (implement later)
        if exit_code != 0:
            if stderr_output:
                print(stderr_output, end="")
        elif exit_code == -1:
            break
        else:
            if stdout_output:
                print(stdout_output, end="")
        
        #####################################


        # for p_cmd in pipe_commands:
        #     # Parse tokens into command and arguments for redirects
        #     command_tokens, redirect_instructions = redirect_parser.parse([p_cmd.command] + p_cmd.args)
            
        #     command_name = command_tokens[0].value if tokens else ''
        #     args = command_tokens[1:] if len(command_tokens) > 1 else []

        #     # Look up the command
        #     command = registry.get_command(command_name)

        #     if command:
        #         result = command.execute(args)
        #         # stdout_output = result.stdout
        #         # stderr_output = result.stderr
        #     elif registry.is_external_command(command_name):
        #         try:
        #             raw_cmd = command_tokens[0].value

        #             if raw_cmd.startswith(("'", '"')) and raw_cmd.endswith(("'", '"')):
        #                 raw_command_name = raw_cmd[1:-1]
        #             else:
        #                 raw_command_name = raw_cmd

        #             # separate the external command and its arguments
        #             ext_command = [raw_command_name] + [
        #                 arg.value for arg in args if arg.type in (TokenType.WORD, TokenType.COMMAND)
        #             ]

        #             # Execute the command using subprocess
        #             subprocess_result = subprocess.run(
        #                 ext_command,
        #                 # shell=True, 
        #                 capture_output=True, 
        #                 text=True, 
        #                 check=True
        #             )
        #             result = CommandResult(
        #                 exit_code=subprocess_result.returncode,
        #                 stdout=subprocess_result.stdout,
        #                 stderr=subprocess_result.stderr,
        #             )
        #         except FileNotFoundError as e:
        #             result = CommandResult(exit_code=1, stderr=f"{command_name}: command not found\n")
        #         except subprocess.CalledProcessError as e:
        #             if e.returncode == 127:
        #                 result = CommandResult(exit_code=1, stderr=f"{command_name}: command not found\n")
        #             else:
        #                 result = CommandResult(exit_code=1, stderr=e.stderr, stdout=e.stdout)

        #     results_dict[p_cmd] = result

        # print("Results:")
        # for cmd, res in results_dict.items():
        #     print(res)

        # # Final printing of results

        # if not redirect_parser.has_redirects(tokens):
        #     if result.exit_code == 1: # has error
        #         print(result.stderr, end="")
        #     elif result.exit_code == -1:
        #         break
        #     else:
        #         if result.stdout:
        #             print(result.stdout, end="")
        # else:
        #     success, final_output, final_stderr, error_message = redirect_processor.apply_redirects(
        #         # stdout_output, stderr_output, redirect_instructions
        #         result.stdout, result.stderr, redirect_instructions
        #         )
        #     if not success:
        #         print(error_message, end="")
        #     else:
        #         if final_output:
        #             print(final_output, end="")
        #         if final_stderr:
        #             print(final_stderr, end="")

if __name__ == "__main__":
    main()
