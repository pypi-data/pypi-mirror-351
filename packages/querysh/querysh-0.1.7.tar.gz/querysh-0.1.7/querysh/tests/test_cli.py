import pytest
from unittest.mock import patch, MagicMock
from querysh.cli import main

@pytest.fixture
def mock_console():
    with patch('querysh.cli.Console') as mock:
        console = MagicMock()
        mock.return_value = console
        yield console

@pytest.fixture
def mock_model_manager():
    with patch('querysh.cli.ModelManager') as mock:
        manager = MagicMock()
        manager.generate_command.return_value = "---command---\nls -la\n---end---"
        mock.return_value = manager
        yield manager

@pytest.fixture
def mock_prompt():
    with patch('querysh.cli.Prompt') as mock:
        yield mock

def test_cli_exit_command(mock_console, mock_model_manager, mock_prompt):
    mock_prompt.ask.side_effect = ["exit"]
    main()
    mock_console.print.assert_any_call("[yellow]Goodbye! 👋[/yellow]")

def test_cli_successful_command(mock_console, mock_model_manager, mock_prompt):
    mock_prompt.ask.side_effect = ["list files", "n", "exit"]
    main()
    mock_console.print.assert_any_call("\n[bold blue]Suggested command:[/bold blue]")
    mock_console.print.assert_any_call("[yellow]Goodbye! 👋[/yellow]")

def test_cli_run_command(mock_console, mock_model_manager, mock_prompt):
    mock_prompt.ask.side_effect = ["list files", "y", "exit"]
    mock_model_manager.generate_command.return_value = "---command---\nls -la\n---end---"
    
    with patch('querysh.cli.CommandProcessor') as mock_cp:
        processor = MagicMock()
        processor.extract_command.return_value = "ls -la"
        processor.validate_command.return_value = (True, None)
        processor.execute_command.return_value = (True, "file1.txt\nfile2.txt", "")
        mock_cp.return_value = processor
        
        main()
        mock_console.print.assert_any_call("\n[bold green]Output:[/bold green]")

def test_cli_invalid_command(mock_console, mock_model_manager, mock_prompt):
    mock_prompt.ask.side_effect = ["list files", "exit"]
    mock_model_manager.generate_command.return_value = "---command---\nls -la\n---end---"
    
    with patch('querysh.cli.CommandProcessor') as mock_cp:
        processor = MagicMock()
        processor.extract_command.return_value = "rm -rf /"
        processor.validate_command.return_value = (False, "Dangerous command")
        mock_cp.return_value = processor
        
        main()
        mock_console.print.assert_any_call("[bold red]Error:[/bold red] Dangerous command")

def test_cli_model_loading_error(mock_console, mock_prompt):
    mock_prompt.ask.side_effect = ["exit"]
    
    with patch('querysh.cli.ModelManager') as mock_mm:
        mock_mm.side_effect = RuntimeError("Failed to load model")
        
        with pytest.raises(SystemExit) as exc_info:
            main()
        assert exc_info.value.code == 1
        mock_console.print.assert_any_call("[bold red]Error:[/bold red] Failed to load model")

def test_cli_command_execution_error(mock_console, mock_model_manager, mock_prompt):
    mock_prompt.ask.side_effect = ["list files", "y", "exit"]
    mock_model_manager.generate_command.return_value = "---command---\nls -la\n---end---"
    
    with patch('querysh.cli.CommandProcessor') as mock_cp:
        processor = MagicMock()
        processor.extract_command.return_value = "ls -la"
        processor.validate_command.return_value = (True, None)
        processor.execute_command.return_value = (False, "", "Permission denied")
        mock_cp.return_value = processor
        
        main()
        mock_console.print.assert_any_call("\n[bold red]Error executing command:[/bold red] Permission denied")

def test_cli_stderr_output(mock_console, mock_model_manager, mock_prompt):
    mock_prompt.ask.side_effect = ["list files", "y", "exit"]
    mock_model_manager.generate_command.return_value = "---command---\nls -la\n---end---"
    
    with patch('querysh.cli.CommandProcessor') as mock_cp:
        processor = MagicMock()
        processor.extract_command.return_value = "ls -la"
        processor.validate_command.return_value = (True, None)
        processor.execute_command.return_value = (True, "file1.txt", "warning: some files were skipped")
        mock_cp.return_value = processor
        
        main()
        mock_console.print.assert_any_call("\n[bold yellow]Warnings:[/bold yellow]")

def test_cli_generation_error(mock_console, mock_model_manager, mock_prompt):
    mock_prompt.ask.side_effect = ["list files", "exit"]
    mock_model_manager.generate_command.side_effect = Exception("Generation failed")
    
    main()
    mock_console.print.assert_any_call("\n[bold red]Error:[/bold red] Generation failed") 