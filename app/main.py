import sys
import subprocess
import shutil
import os
from app.commands import type, SHELL_BUILTINS

def main():
    while True:
        # Uncomment this block to pass the first stage
        sys.stdout.write("$ ")

        # Wait for user input
        command = input()
        if command == "exit 0":
            return 0
        elif command.startswith("echo"):
            print(command.split(" ", 1)[1] if " " in command else "")
        elif command.startswith("type"):
            type(command)
        elif command == "pwd":
            print(os.getcwd())
        elif command not in SHELL_BUILTINS and shutil.which(command.split()[0]):
            try:
                # Execute the command using subprocess
                result = subprocess.run(command, shell=True, capture_output=True, text=True, check=True)
                print(result.stdout, end="")
            except subprocess.CalledProcessError as e:
                print(e)

        else:
            print(f"{command}: command not found")

if __name__ == "__main__":
    main()
