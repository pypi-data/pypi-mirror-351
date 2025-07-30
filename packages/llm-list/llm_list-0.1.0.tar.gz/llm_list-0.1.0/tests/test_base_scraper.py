"""Tests for the base scraper class."""
import json
from pathlib import Path

import pytest

from llm_list.scrapers.base import BaseScraper

def test_base_scraper_init(temp_output_dir):
    """Test BaseScraper initialization with custom output directory."""
    scraper = BaseScraper(output_dir=temp_output_dir)
    assert scraper.output_dir == temp_output_dir
    assert scraper.output_dir.exists()

def test_base_scraper_get_models_fingerprint():
    """Test model fingerprint generation."""
    models = [
        {'name': 'model1', 'description': 'Test model', 'sizes': ['7B']},
        {'name': 'model2', 'description': 'Another model', 'sizes': ['13B']}
    ]
    
    scraper = BaseScraper()
    fingerprint1 = scraper._get_models_fingerprint(models)
    
    # Same models should produce same fingerprint
    fingerprint2 = scraper._get_models_fingerprint(models)
    assert fingerprint1 == fingerprint2
    
    # Different models should produce different fingerprint
    different_models = models.copy()
    different_models[0]['name'] = 'different_name'
    fingerprint3 = scraper._get_models_fingerprint(different_models)
    assert fingerprint1 != fingerprint3

def test_base_scraper_save_models_data(temp_output_dir):
    """Test saving models data to file."""
    models = [
        {'name': 'test_model', 'description': 'A test model'}
    ]
    
    scraper = BaseScraper(output_dir=temp_output_dir)
    filename, fingerprint = scraper._save_models_data(models)
    
    assert filename is not None
    assert filename.exists()
    assert fingerprint is not None
    
    # Verify file contents
    with open(filename, 'r', encoding='utf-8') as f:
        data = json.load(f)
        assert data['model_count'] == 1
        assert data['models'][0]['name'] == 'test_model'
    
    # Test no changes detection
    filename2, fingerprint2 = scraper._save_models_data(models, fingerprint)
    assert filename2 is None  # No changes, so no new file
    assert fingerprint2 == fingerprint

@pytest.mark.parametrize('models', [
    [],
    None,
    [{'name': 'model1'}, {'name': 'model2'}]
])
def test_base_scraper_scrape_models_abstract(models):
    """Test that scrape_models is abstract and must be implemented by subclasses."""
    class TestScraper(BaseScraper):
        def scrape_models(self, **kwargs):
            return models
    
    scraper = TestScraper()
    assert scraper.scrape_models() == models
