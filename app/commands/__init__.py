SHELL_BUILTINS = {
    "echo",
    "exit",
    "type",
}

def type(command):
    import shutil

    # search in all the path dirs
    builtin = command.split(" ", 1)[1]
    
    if builtin in SHELL_BUILTINS:
        print(f"{builtin} is a shell builtin")
    
    elif path := shutil.which(builtin):
        print(f"{builtin} is {path}")
    
    else:
        print(f"{builtin}: not found")