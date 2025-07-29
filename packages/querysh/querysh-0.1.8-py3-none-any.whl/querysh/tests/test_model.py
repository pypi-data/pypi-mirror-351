import pytest
from unittest.mock import patch, MagicMock
from querysh.model import ModelManager

@pytest.fixture
def mock_progress():
    with patch('querysh.model.Progress') as mock:
        progress = MagicMock()
        mock.return_value.__enter__.return_value = progress
        yield progress

def test_model_manager_initialization(mock_progress):
    with patch('querysh.model.load') as mock_load:
        mock_model = MagicMock()
        mock_tokenizer = MagicMock()
        mock_load.return_value = (mock_model, mock_tokenizer)
        
        manager = ModelManager()
        assert manager.model == mock_model
        assert manager.tokenizer == mock_tokenizer
        mock_progress.add_task.assert_called_once_with("Loading model...", total=None)

def test_model_manager_initialization_failure(mock_progress):
    with patch('querysh.model.load') as mock_load:
        mock_load.side_effect = Exception("Model loading failed")
        
        with pytest.raises(RuntimeError) as exc_info:
            ModelManager()
        assert "Failed to load model" in str(exc_info.value)
        mock_progress.add_task.assert_called_once_with("Loading model...", total=None)

def test_generate_command(mock_progress):
    with patch('querysh.model.load') as mock_load, \
         patch('querysh.model.generate') as mock_generate:
        
        mock_model = MagicMock()
        mock_tokenizer = MagicMock()
        mock_tokenizer.apply_chat_template.return_value = "test prompt"
        mock_load.return_value = (mock_model, mock_tokenizer)
        mock_generate.return_value = "---command---\nls -la\n---end---"
        
        manager = ModelManager()
        result = manager.generate_command("list files")
        
        assert result == "---command---\nls -la\n---end---"
        mock_tokenizer.apply_chat_template.assert_called_once()
        mock_generate.assert_called_once_with(
            mock_model,
            mock_tokenizer,
            prompt="test prompt",
            verbose=False
        ) 
        mock_progress.add_task.assert_any_call("Loading model...", total=None)
        mock_progress.add_task.assert_any_call("Generating command...", total=None) 