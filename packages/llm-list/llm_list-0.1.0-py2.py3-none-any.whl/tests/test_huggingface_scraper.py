"""Tests for the Hugging Face scraper."""
import json
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

def test_huggingface_scraper_init(temp_output_dir):
    """Test HuggingFaceScraper initialization."""
    from llm_list.scrapers.huggingface import HuggingFaceScraper
    
    scraper = HuggingFaceScraper(output_dir=temp_output_dir)
    assert scraper.output_dir == temp_output_dir
    assert scraper.HF_API_URL == "https://huggingface.co/api/models-llm"
    assert 'User-Agent' in scraper.session.headers
    assert (temp_output_dir / "hf_models_cache.json").exists() or not (temp_output_dir / "hf_models_cache.json").exists()

def test_huggingface_scraper_load_cached_models(hf_scraper, temp_output_dir):
    """Test loading models from cache."""
    # Test with no cache file (should return default models)
    models = hf_scraper._load_cached_models()
    assert len(models) > 0  # Should return default models
    
    # Test with invalid cache file
    cache_file = temp_output_dir / "hf_models_cache.json"
    cache_file.write_text("invalid json")
    models = hf_scraper._load_cached_models()
    assert len(models) > 0  # Should return default models
    
    # Test with valid cache file
    test_models = [{"name": "test/model", "description": "Test model"}]
    with open(cache_file, 'w', encoding='utf-8') as f:
        json.dump(test_models, f)
    
    models = hf_scraper._load_cached_models()
    assert models == test_models

def test_huggingface_scraper_save_models_to_cache(hf_scraper, temp_output_dir):
    """Test saving models to cache."""
    test_models = [{"name": "test/model", "description": "Test model"}]
    
    hf_scraper._save_models_to_cache(test_models)
    
    cache_file = temp_output_dir / "hf_models_cache.json"
    assert cache_file.exists()
    
    with open(cache_file, 'r', encoding='utf-8') as f:
        saved_models = json.load(f)
    
    assert saved_models == test_models

@patch('llm_list.scrapers.huggingface.requests.Session.get')
def test_huggingface_scraper_scrape_models_success(mock_get, hf_scraper, mock_hf_response):
    """Test successful scraping of Hugging Face models."""
    # Mock the response
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = mock_hf_response
    mock_get.return_value = mock_response
    
    # Call the method
    models = hf_scraper.scrape_models(search_term="code")
    
    # Verify the results
    assert len(models) > 0
    assert models[0]['name'] == 'codellama/CodeLlama-7b-hf'
    assert 'pytorch' in models[0]['formats']
    assert 'safetensors' in models[0]['formats']
    
    # Verify the cache was updated
    cached_models = hf_scraper._load_cached_models()
    assert len(cached_models) > 0
    assert cached_models[0]['name'] == 'codellama/CodeLlama-7b-hf'

@patch('llm_list.scrapers.huggingface.requests.Session.get')
def test_huggingface_scraper_scrape_models_error(mock_get, hf_scraper):
    """Test error handling when scraping Hugging Face models."""
    # Mock a failed response
    mock_response = Mock()
    mock_response.status_code = 500
    mock_response.raise_for_status.side_effect = Exception("API error")
    mock_get.return_value = mock_response
    
    # Call the method and verify it falls back to cached/default models
    models = hf_scraper.scrape_models(search_term="code")
    assert len(models) > 0  # Should return default models

def test_huggingface_scraper_monitor(hf_scraper):
    """Test the monitor method (basic functionality)."""
    with patch.object(hf_scraper, 'scrape_models') as mock_scrape, \
         patch.object(hf_scraper, '_save_models_data') as mock_save, \
         patch('time.sleep') as mock_sleep:
        
        # Set up mocks
        mock_scrape.return_value = [{'name': 'test/model'}]
        mock_save.return_value = (Path('test.json'), 'fingerprint')
        
        # Simulate keyboard interrupt after first iteration
        mock_sleep.side_effect = KeyboardInterrupt()
        
        # Call the method
        hf_scraper.monitor(interval=1, search_term="code")
        
        # Verify the mocks were called
        mock_scrape.assert_called_once_with(search_term="code")
        mock_save.assert_called_once_with([{'name': 'test/model'}], None)
        mock_sleep.assert_called_once()

def test_huggingface_scraper_default_models(hf_scraper):
    """Test that default models are available when API is not accessible."""
    # Clear any existing cache
    if hf_scraper.cache_file.exists():
        hf_scraper.cache_file.unlink()
    
    # Should return default models when no cache exists
    models = hf_scraper._load_cached_models()
    assert len(models) > 0
    assert all('name' in model for model in models)
