import pytest
from unittest.mock import MagicMock, patch

@pytest.fixture
def mock_model():
    model = MagicMock()
    tokenizer = MagicMock()
    tokenizer.apply_chat_template.return_value = "test prompt"
    return model, tokenizer

@pytest.fixture
def mock_subprocess():
    with pytest.MonkeyPatch.context() as m:
        mock_run = MagicMock()
        m.setattr("subprocess.run", mock_run)
        yield mock_run

@pytest.fixture
def mock_rich_components():
    with patch('querysh.cli.Console') as mock_console, \
         patch('querysh.cli.Panel') as mock_panel, \
         patch('querysh.cli.Prompt') as mock_prompt, \
         patch('querysh.cli.Syntax') as mock_syntax:
        
        mock_console.return_value = MagicMock()
        mock_panel.fit.return_value = MagicMock()
        mock_prompt.ask.return_value = "test input"
        mock_syntax.return_value = MagicMock()
        
        yield {
            'console': mock_console.return_value,
            'panel': mock_panel,
            'prompt': mock_prompt,
            'syntax': mock_syntax
        }

@pytest.fixture
def mock_model_manager():
    with patch('querysh.model.load') as mock_load, \
         patch('querysh.model.generate') as mock_generate:
        
        mock_model = MagicMock()
        mock_tokenizer = MagicMock()
        mock_tokenizer.apply_chat_template.return_value = "test prompt"
        mock_load.return_value = (mock_model, mock_tokenizer)
        mock_generate.return_value = "---command---\nls -la\n---end---"
        
        yield {
            'model': mock_model,
            'tokenizer': mock_tokenizer,
            'load': mock_load,
            'generate': mock_generate
        } 