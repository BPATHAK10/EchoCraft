import pexpect
import pytest
import os

@pytest.fixture
def shell_process(tmp_path):
    shell_script_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "echo-craft.sh"))
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

    env = os.environ.copy()
    env["PYTHONPATH"] = project_root

    proc = pexpect.spawn(
        shell_script_path,
        cwd=str(tmp_path),
        env=env,             
        encoding='utf-8',
        timeout=5
    )

    # Wait for *any* prompt after banner (just once)
    proc.expect(r'(?:\x1b\[[0-9;]*m)*\$ ')

    yield proc
    proc.terminate(force=True)


def run_shell_command(proc, command, prompt=r'(?:\x1b\[[0-9;]*m)*\$ '):
    """
    Wait for prompt, send a command, wait for next prompt,
    return the output between them.
    """
    proc.sendline(command)
    proc.expect(prompt)
    output = proc.before.strip()
    
    # Remove echoed command
    lines = output.splitlines()
    if lines and lines[0].strip() == command:
        lines = lines[1:]
    return lines


def test_echo(shell_process):
    output = run_shell_command(shell_process, "echo hello")
    assert output == ["hello"]

def test_stdout_redirection(shell_process):
    run_shell_command(shell_process, "echo hello > file1.txt")
    output = run_shell_command(shell_process, "ls")
    print(f"[DEBUG] Files after redirection: {output}")
    output = run_shell_command(shell_process, "cat file1.txt")
    assert output == ["hello"]

def test_redirect_append(shell_process):
    run_shell_command(shell_process, "echo line1 > file.txt")
    run_shell_command(shell_process, "echo line2 >> file.txt")
    output = run_shell_command(shell_process, "cat file.txt")
    assert output == ["line1", "line2"]

def test_simple_pipeline(shell_process):
    output = run_shell_command(shell_process, "echo one two | wc -w")
    assert [line.strip() for line in output] == ["2"]

def test_multi_stage_pipeline(shell_process):
    run_shell_command(shell_process, "echo apple > fruits.txt")
    run_shell_command(shell_process, "echo banana >> fruits.txt")
    output = run_shell_command(shell_process, "cat fruits.txt | grep apple | wc -l")
    assert [line.strip() for line in output] == ["1"]


def test_pipeline_with_output_redirection(shell_process):
    run_shell_command(shell_process, "echo hello world | tr a-z A-Z > caps.txt")
    output = run_shell_command(shell_process, "cat caps.txt")
    assert output == ["HELLO WORLD"]


def test_command_not_found(shell_process):
    output = run_shell_command(shell_process, "nonexistentcommand")
    
    error_output = "".join(output).strip()
    assert "nonexistentcommand: command not found" == error_output


def test_history(shell_process):
    # First command
    run_shell_command(shell_process, "echo first")
    # Second command
    run_shell_command(shell_process, "ls")
    
    # Check history
    output = run_shell_command(shell_process, "history")

    # Parse the output to remove the command number prefix
    output = [line.strip().split(" ", 1)[1].strip() for line in output]
    
    # Expecting the last two commands in history
    assert output[-3:] == ["echo first", "ls", "history"]