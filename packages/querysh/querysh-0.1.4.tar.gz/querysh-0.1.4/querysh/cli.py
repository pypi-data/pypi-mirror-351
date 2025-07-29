import sys
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt
from rich.syntax import Syntax

from querysh.model import ModelManager
from querysh.command import CommandProcessor

def main():
    console = Console()
    
    try:
        model_manager = ModelManager()
    except RuntimeError as e:
        console.print(f"[bold red]Error:[/bold red] {str(e)}")
        sys.exit(1)

    command_processor = CommandProcessor()

    console.print(Panel.fit(
        "[bold blue]🤖 querysh[/bold blue]\n"
        "[dim]Use natural language commands to interact with your system[/dim]\n"
        "[dim]Type 'exit' to quit[/dim]",
        border_style="blue"
    ))
    console.print()

    while True:
        user_input = Prompt.ask("[bold green]querysh[/bold green]")
        if user_input.strip().lower() == 'exit':
            console.print("[yellow]Goodbye! 👋[/yellow]")
            break

        try:
            generated_text = model_manager.generate_command(user_input)
            command = command_processor.extract_command(generated_text)
            
            is_valid, error_msg = command_processor.validate_command(command)
            if not is_valid:
                console.print(f"[bold red]Error:[/bold red] {error_msg}")
                continue

            console.print("\n[bold blue]Suggested command:[/bold blue]")
            console.print(Syntax(command, "bash", theme="monokai"))

            run = Prompt.ask("\nRun this command?", choices=["y", "n"], default="n")
            if run == 'y':
                success, stdout, stderr = command_processor.execute_command(command)
                
                if success:
                    if stdout:
                        console.print("\n[bold green]Output:[/bold green]")
                        console.print(Syntax(stdout, "bash", theme="monokai"))
                    if stderr:
                        console.print("\n[bold yellow]Warnings:[/bold yellow]")
                        console.print(Syntax(stderr, "bash", theme="monokai"))
                else:
                    console.print(f"\n[bold red]Error executing command:[/bold red] {stderr}")

        except Exception as e:
            console.print(f"\n[bold red]Error:[/bold red] {str(e)}")

        console.print()

if __name__ == "__main__":
    main() 