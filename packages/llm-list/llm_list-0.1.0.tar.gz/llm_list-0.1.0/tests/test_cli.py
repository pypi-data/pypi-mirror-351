"""Tests for the command-line interface."""
import argparse
from unittest.mock import patch, MagicMock

import pytest

def test_main_no_args(capsys):
    """Test main function with no arguments shows help."""
    from llm_list.__main__ import main
    
    with patch('sys.argv', ['llm-list']), \
         pytest.raises(SystemExit):
        main()
    
    captured = capsys.readouterr()
    assert "usage:" in captured.out.lower()

def test_ollama_command(capsys):
    """Test the ollama subcommand."""
    from llm_list.__main__ import ollama_command
    
    # Create a mock args object
    args = MagicMock()
    args.monitor = False
    
    # Mock the OllamaScraper
    with patch('llm_list.__main__.OllamaScraper') as mock_scraper:
        mock_instance = mock_scraper.return_value
        mock_instance.scrape_models.return_value = [
            {'name': 'test-model', 'description': 'A test model'}
        ]
        
        ollama_command(args)
        
        # Verify the output
        captured = capsys.readouterr()
        assert "test-model" in captured.out
        mock_instance.scrape_models.assert_called_once()

def test_huggingface_command(capsys):
    """Test the huggingface subcommand."""
    from llm_list.__main__ import huggingface_command
    
    # Create a mock args object
    args = MagicMock()
    args.monitor = False
    args.search = "code"
    
    # Mock the HuggingFaceScraper
    with patch('llm_list.__main__.HuggingFaceScraper') as mock_scraper:
        mock_instance = mock_scraper.return_value
        mock_instance.scrape_models.return_value = [
            {'name': 'test/model', 'description': 'A test model'}
        ]
        
        huggingface_command(args)
        
        # Verify the output
        captured = capsys.readouterr()
        assert "test/model" in captured.out
        mock_instance.scrape_models.assert_called_once_with(search_term="code")

@patch('llm_list.__main__.ollama_command')
def test_main_ollama_command(mock_ollama, capsys):
    """Test main function with ollama subcommand."""
    from llm_list.__main__ import main
    
    with patch('sys.argv', ['llm-list', 'ollama']):
        main()
    
    mock_ollama.assert_called_once()

@patch('llm_list.__main__.huggingface_command')
def test_main_huggingface_command(mock_hf, capsys):
    """Test main function with huggingface subcommand."""
    from llm_list.__main__ import main
    
    with patch('sys.argv', ['llm-list', 'huggingface']):
        main()
    
    mock_hf.assert_called_once()

def test_main_verbose_flag(capsys):
    """Test that verbose flag enables debug logging."""
    from llm_list.__main__ import setup_logging
    import logging
    
    # Test with verbose=False (default)
    setup_logging(verbose=False)
    logger = logging.getLogger('test')
    logger.debug("This is a debug message")
    
    captured = capsys.readouterr()
    assert "This is a debug message" not in captured.out
    
    # Test with verbose=True
    setup_logging(verbose=True)
    logger.debug("This is a debug message")
    
    captured = capsys.readouterr()
    assert "This is a debug message" in captured.out
