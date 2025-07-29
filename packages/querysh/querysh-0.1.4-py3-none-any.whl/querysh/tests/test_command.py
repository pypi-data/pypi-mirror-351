import pytest
from querysh.command import CommandProcessor

def test_extract_command_with_markers():
    text = "Some text\n---command---\nls -la\n---end---\nMore text"
    command = CommandProcessor.extract_command(text)
    assert command == "ls -la"

def test_extract_command_without_markers():
    text = "ls -la"
    command = CommandProcessor.extract_command(text)
    assert command == "ls -la"

def test_extract_command_with_code_blocks():
    text = "```bash\nls -la\n```"
    command = CommandProcessor.extract_command(text)
    assert command == "ls -la"

def test_validate_command_length():
    command = "x" * 201
    is_valid, error_msg = CommandProcessor.validate_command(command)
    assert not is_valid
    assert "exceeds maximum length" in error_msg

def test_validate_dangerous_command():
    command = "rm -rf /"
    is_valid, error_msg = CommandProcessor.validate_command(command)
    assert not is_valid
    assert "dangerous operations" in error_msg

def test_validate_safe_command():
    command = "ls -la"
    is_valid, error_msg = CommandProcessor.validate_command(command)
    assert is_valid
    assert error_msg is None

def test_execute_command_success(mock_subprocess):
    mock_subprocess.return_value.stdout = "file1.txt\nfile2.txt"
    mock_subprocess.return_value.stderr = ""
    mock_subprocess.return_value.check_returncode.return_value = None

    success, stdout, stderr = CommandProcessor.execute_command("ls")
    assert success
    assert stdout == "file1.txt\nfile2.txt"
    assert stderr == ""

def test_execute_command_failure(mock_subprocess):
    mock_subprocess.side_effect = Exception("Command failed")
    success, stdout, stderr = CommandProcessor.execute_command("invalid")
    assert not success
    assert stdout == ""
    assert stderr == "Command failed" 