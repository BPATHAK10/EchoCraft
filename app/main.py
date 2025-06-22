import sys
import subprocess
import shutil
import shlex
import os
from app.commands import type, change_dir, SHELL_BUILTINS
from app.lexical import MyLex

def main():
    while True:
        sys.stdout.write("$ ")

        # Wait for user input
        raw_input = input()
        prompt = shlex.split(raw_input)

        # prompt = MyLex(raw_input).parse()
        # print(f"Parsed input: {prompt}")

        command = prompt[0] if prompt else ''
        args = prompt[1:] if len(prompt) > 1 else []

        if command == "exit":
            return 0
        elif command == '':
            continue
        elif command.startswith("echo"):
            print(' '.join(args))
        elif command.startswith("type"):
            type(args[0])
        elif command == "pwd":
            print(os.getcwd())
        elif command.startswith("cd"):
            change_dir(args[0])
        elif command not in SHELL_BUILTINS and shutil.which(command):
            try:
                # Execute the command using subprocess
                result = subprocess.run(raw_input, shell=True, capture_output=True, text=True, check=True)
                print(result.stdout, end="")
            except subprocess.CalledProcessError as e:
                print(e)

        else:
            print(f"{command}: command not found")

if __name__ == "__main__":
    main()
