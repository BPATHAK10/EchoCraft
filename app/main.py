import sys


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
        else:
            print(f"{command}: command not found")

if __name__ == "__main__":
    main()
