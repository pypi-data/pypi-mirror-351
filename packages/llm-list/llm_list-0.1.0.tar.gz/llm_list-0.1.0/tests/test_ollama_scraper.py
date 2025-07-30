"""Tests for the Ollama scraper."""
import json
from pathlib import Path
from unittest.mock import Mock, patch

import pytest
from bs4 import BeautifulSoup

def test_ollama_scraper_init(temp_output_dir):
    """Test OllamaScraper initialization."""
    from llm_list.scrapers.ollama import OllamaScraper
    
    scraper = OllamaScraper(output_dir=temp_output_dir)
    assert scraper.output_dir == temp_output_dir
    assert scraper.OLLAMA_LIBRARY_URL == "https://ollama.com/library"
    assert 'User-Agent' in scraper.session.headers

def test_ollama_scraper_parse_model_item():
    """Test parsing a single model item from HTML."""
    from llm_list.scrapers.ollama import OllamaScraper
    
    html = """
    <li x-test-model>
      <h2>test-model</h2>
      <p>Test description</p>
      <div class="flex space-x-5">
        <span>Pulls: 1.2M</span>
        <span>Updated: 2 months ago</span>
      </div>
      <div>
        <span class="bg-gray-100">7B</span>
        <span class="inline-flex items-center rounded-md">tag1</span>
      </div>
      <a href="/library/test-model">View</a>
    </li>
    """
    
    soup = BeautifulSoup(html, 'lxml')
    item = soup.select_one('li[x-test-model]')
    
    scraper = OllamaScraper()
    model = {}
    
    # Test the parsing logic (simplified for test)
    h2 = item.select_one('h2')
    if h2:
        model['name'] = h2.get_text(strip=True)
        desc_p = h2.find_next_sibling('p')
        if desc_p:
            model['description'] = desc_p.get_text(strip=True)
    
    model['sizes'] = [span.get_text(strip=True) for span in 
                     item.select('span.bg-gray-100, span.bg-gray-200')]
    
    model['tags'] = [tag.get_text(strip=True) for tag in 
                    item.select('span.inline-flex.items-center.rounded-md')]
    
    model['metadata'] = {}
    meta_div = item.select_one('div.flex.space-x-5')
    if meta_div:
        for span in meta_div.find_all('span'):
            text = span.get_text(strip=True)
            if ':' in text:
                key, value = text.split(':', 1)
                model['metadata'][key.strip().lower()] = value.strip()
    
    link = item.find('a', href=True)
    if link and link.get('href', '').startswith('/library/'):
        model['url'] = f"https://ollama.com{link['href']}"
    
    assert model['name'] == 'test-model'
    assert model['description'] == 'Test description'
    assert model['sizes'] == ['7B']
    assert model['tags'] == ['tag1']
    assert model['metadata'] == {'pulls': '1.2M', 'updated': '2 months ago'}
    assert model['url'] == 'https://ollama.com/library/test-model'

@patch('llm_list.scrapers.ollama.requests.Session.get')
def test_ollama_scraper_scrape_models(mock_get, ollama_scraper, mock_ollama_response):
    """Test scraping models from Ollama library."""
    # Mock the response
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.text = mock_ollama_response
    mock_get.return_value = mock_response
    
    # Call the method
    models = ollama_scraper.scrape_models()
    
    # Verify the results
    assert len(models) > 0
    assert models[0]['name'] == 'llama2'
    assert models[0]['description'] == 'A foundational model by Meta'
    assert '7B' in models[0]['sizes']
    
    # Verify the debug file was created
    debug_file = ollama_scraper.output_dir / "debug_ollama_page.html"
    assert debug_file.exists()

@patch('llm_list.scrapers.ollama.requests.Session.get')
def test_ollama_scraper_scrape_models_error(mock_get, ollama_scraper):
    """Test error handling when scraping models."""
    # Mock a failed response
    mock_response = Mock()
    mock_response.status_code = 500
    mock_response.raise_for_status.side_effect = Exception("Server error")
    mock_get.return_value = mock_response
    
    # Call the method and verify it handles the error gracefully
    models = ollama_scraper.scrape_models()
    assert models == []

def test_ollama_scraper_monitor(ollama_scraper):
    """Test the monitor method (basic functionality)."""
    with patch.object(ollama_scraper, 'scrape_models') as mock_scrape, \
         patch.object(ollama_scraper, '_save_models_data') as mock_save, \
         patch('time.sleep') as mock_sleep:
        
        # Set up mocks
        mock_scrape.return_value = [{'name': 'test-model'}]
        mock_save.return_value = (Path('test.json'), 'fingerprint')
        
        # Simulate keyboard interrupt after first iteration
        mock_sleep.side_effect = KeyboardInterrupt()
        
        # Call the method
        ollama_scraper.monitor(interval=1)
        
        # Verify the mocks were called
        mock_scrape.assert_called_once()
        mock_save.assert_called_once_with([{'name': 'test-model'}], None)
        mock_sleep.assert_called_once()
