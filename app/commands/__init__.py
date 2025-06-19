import os
import re

SHELL_BUILTINS = {
    "echo",
    "exit",
    "type",
    "pwd",
    "cd",
}

def type(builtin):
    import shutil
    
    if builtin in SHELL_BUILTINS:
        print(f"{builtin} is a shell builtin")
    
    elif path := shutil.which(builtin):
        print(f"{builtin} is {path}")
    
    else:
        print(f"{builtin}: not found")


def change_dir(dir):
    if dir == "~":
        dir = os.environ.get("HOME")
    # change the cwd to dir
    try:
        os.chdir(dir)
    except FileNotFoundError:
        print(f"cd: {dir}: No such file or directory")

def handle_quotes(command):
    exp = r"'([^']*)'"
    matches = re.findall(exp, command)

    # print(matches)

    if not matches:
        return command.split(' ')
    
    return matches