import sys
import subprocess
import shutil
import os

SHELL_BUILTINS = {
    "echo",
    "exit",
    "type",
}

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
            # search in all the path dirs
            builtin = command.split(" ", 1)[1]
            
            if builtin in SHELL_BUILTINS:
                print(f"{builtin} is a shell builtin")
            
            elif path := shutil.which(builtin):
                print(f"{builtin} is {path}")
            
            else:
                print(f"{builtin}: not found")
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
