"""QuerySH - A local, offline shell interface powered by MLX-optimized Llama model."""

__version__ = "0.1.5"

from .cli import main
from .model import ModelManager
from .command import CommandProcessor

__all__ = ["main", "ModelManager", "CommandProcessor"] 