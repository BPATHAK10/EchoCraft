import sys

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
            builtin = command.split(" ", 1)[1]
            if builtin in SHELL_BUILTINS:
                print(f"{builtin} is a shell builtin")
            else:
                print(f"{builtin}: not found")
        else:
            print(f"{command}: command not found")

if __name__ == "__main__":
    main()
