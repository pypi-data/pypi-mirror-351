import os
from contextlib import redirect_stderr, redirect_stdout
import io
from mlx_lm import load, generate
from rich.progress import Progress, SpinnerColumn, TextColumn, TimeElapsedColumn, BarColumn
from rich.console import Console

os.environ["TOKENIZERS_PARALLELISM"] = "false"

class ModelManager:
    def __init__(self, model_path=None):
        self.model_path = model_path or os.getenv("QUERYSH_MODEL_PATH", "mlx-community/Llama-3.2-1B-Instruct-4bit")
        self.model = None
        self.tokenizer = None
        self._load_model()

    def _load_model(self):
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TimeElapsedColumn(),
            console=Console(force_terminal=True)
        ) as progress:
            task = progress.add_task(
                "[cyan]Initializing local model...",
                total=None
            )
            try:
                with redirect_stdout(io.StringIO()), redirect_stderr(io.StringIO()):
                    self.model, self.tokenizer = load(self.model_path)
            except Exception as e:
                raise RuntimeError(f"Failed to load model: {str(e)}")

    def generate_command(self, user_input):
        system_message = (
            "You are a command-line assistant. Your task is to convert natural language instructions "
            "into simple, single-line shell commands. Keep commands short and precise. "
            "Do not include explanations or multiple commands."
        )
        
        instruction = (
            f"Convert this instruction into a single, simple shell command. "
            f"Output ONLY the command between ---command--- and ---end---. "
            f"Keep it short and precise. No explanations or markdown.\n"
            f"Instruction: {user_input}"
        )
        
        messages = [
            {"role": "system", "content": system_message},
            {"role": "user", "content": instruction}
        ]
        
        prompt = self.tokenizer.apply_chat_template(messages, add_generation_prompt=True)
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TimeElapsedColumn(),
            console=Console(force_terminal=True)
        ) as progress:
            task = progress.add_task(
                "[cyan]Processing command...",
                total=None
            )
            with redirect_stderr(io.StringIO()):
                text = generate(self.model, self.tokenizer, prompt=prompt, verbose=False)
        
        return text 