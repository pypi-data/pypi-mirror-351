"""Scraper for Hugging Face models."""
import json
import logging
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

import requests

from .base import BaseScraper

logger = logging.getLogger(__name__)

class HuggingFaceScraper(BaseScraper):
    """Scraper for Hugging Face models."""
    
    HF_API_URL = "https://huggingface.co/api/models-llm"
    
    # Default models to use when API is not available
    DEFAULT_MODELS = [
        {
            "name": "codellama/CodeLlama-7b-hf",
            "description": "Code completion model from Meta, 7B parameters",
            "tags": ["code", "7b", "meta"],
            "metadata": {
                "pulls": "1.2M",
                "updated": "3 months ago"
            }
        },
        {
            "name": "bigcode/starcoder",
            "description": "15.5B parameter model for code generation",
            "tags": ["code", "15.5b", "bigcode"],
            "metadata": {
                "pulls": "850k",
                "updated": "5 months ago"
            }
        },
        {
            "name": "deepseek-ai/deepseek-coder-6.7b-instruct",
            "description": "6.7B parameter model for code generation and instruction following",
            "tags": ["code", "6.7b", "instruct"],
            "metadata": {
                "pulls": "320k",
                "updated": "1 month ago"
            }
        },
        {
            "name": "TheBloke/CodeLlama-7B-GGUF",
            "description": "CodeLlama 7B in GGUF format for CPU inference",
            "tags": ["code", "7b", "gguf", "cpu"],
            "metadata": {
                "pulls": "280k",
                "updated": "2 months ago"
            }
        },
        {
            "name": "TheBloke/Mistral-7B-Code-16K-qlora-GGUF",
            "description": "Mistral 7B fine-tuned for code with 16K context length",
            "tags": ["code", "7b", "mistral", "16k"],
            "metadata": {
                "pulls": "190k",
                "updated": "1 month ago"
            }
        }
    ]
    
    def __init__(self, output_dir: Optional[Union[str, Path]] = None):
        """Initialize the Hugging Face scraper.
        
        Args:
            output_dir: Directory to save scraped data.
        """
        super().__init__(output_dir)
        self.output_dir = Path(output_dir) if output_dir else Path.cwd() / "huggingface_models_data"
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Set up session with headers
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'application/json',
            'Accept-Language': 'en-US,en;q=0.5',
        })
        
        # Cache file for models data
        self.cache_file = self.output_dir / "hf_models_cache.json"
    
    def _load_cached_models(self) -> List[Dict[str, Any]]:
        """Load models from cache file."""
        try:
            if self.cache_file.exists():
                with open(self.cache_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    if isinstance(data, list) and all('name' in item for item in data):
                        return data
        except Exception as e:
            logger.error(f"Error loading cached models: {e}")
        
        # Return default models if cache is not available
        return self.DEFAULT_MODELS
    
    def _save_models_to_cache(self, models: List[Dict[str, Any]]) -> None:
        """Save models to cache file."""
        try:
            with open(self.cache_file, 'w', encoding='utf-8') as f:
                json.dump(models, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"Error saving models to cache: {e}")
    
    def scrape_models(self, search_term: str = "code", limit: int = 100, **kwargs) -> List[Dict[str, Any]]:
        """Scrape available models from Hugging Face.
        
        Args:
            search_term: Term to search for in model names/descriptions.
            limit: Maximum number of models to return.
            
        Returns:
            List of model dictionaries.
        """
        logger.info(f"Scraping Hugging Face for {search_term} models...")
        
        try:
            params = {
                'search': search_term,
                'sort': 'downloads',
                'direction': '-1',
                'limit': limit,
                'full': 'true',
                'config': 'true'
            }
            
            response = self.session.get(self.HF_API_URL, params=params, timeout=30)
            response.raise_for_status()
            
            models_data = response.json()
            
            if not isinstance(models_data, list):
                logger.warning("Unexpected response format from Hugging Face API")
                return self._load_cached_models()
            
            # Process models data
            models = []
            for item in models_data:
                try:
                    model_name = item.get('id', '')
                    if not model_name:
                        continue
                    
                    # Extract model details
                    model_info = {
                        'name': model_name,
                        'url': f"https://huggingface.co/{model_name}",
                        'description': item.get('cardData', {}).get('description', 'No description'),
                        'tags': item.get('tags', []),
                        'metadata': {
                            'downloads': item.get('downloads', 0),
                            'likes': item.get('likes', 0),
                            'last_updated': item.get('lastModified'),
                            'pipeline_tag': item.get('pipeline_tag', '')
                        }
                    }
                    
                    # Add model sizes if available
                    if 'safetensors' in item.get('siblings', []):
                        model_info['formats'] = ['safetensors']
                    if 'pytorch_model.bin' in [s.get('rfilename', '') for s in item.get('siblings', [])]:
                        model_info.setdefault('formats', []).append('pytorch')
                    
                    models.append(model_info)
                    
                except Exception as e:
                    logger.error(f"Error processing model {model_name}: {e}")
            
            # Save to cache
            if models:
                self._save_models_to_cache(models)
            else:
                logger.warning("No models found, using cached data")
                models = self._load_cached_models()
            
            logger.info(f"Found {len(models)} models")
            return models
            
        except requests.RequestException as e:
            logger.error(f"Error fetching from Hugging Face: {e}")
            return self._load_cached_models()
        except Exception as e:
            logger.error(f"Unexpected error: {e}", exc_info=True)
            return self._load_cached_models()
    
    def monitor(self, interval: int = 3600, search_term: str = "code", **kwargs) -> None:
        """Monitor Hugging Face models for changes.
        
        Args:
            interval: Time in seconds between checks.
            search_term: Term to search for in model names/descriptions.
            **kwargs: Additional arguments to pass to scrape_models.
        """
        logger.info("Starting Hugging Face model monitor...")
        logger.info(f"Searching for models with term: {search_term}")
        logger.info(f"Data will be saved to: {self.output_dir}")
        logger.info("Press Ctrl+C to stop monitoring")
        
        prev_fingerprint = None
        
        try:
            while True:
                models = self.scrape_models(search_term=search_term, **kwargs)
                if not models:
                    logger.warning("No models found in this iteration.")
                    time.sleep(300)  # Wait 5 minutes before retrying
                    continue
                
                # Save models and get new fingerprint
                filename, new_fingerprint = self._save_models_data(models, prev_fingerprint)
                
                if filename:
                    logger.info(f"Changes detected, saved to {filename}")
                
                prev_fingerprint = new_fingerprint
                
                # Calculate sleep time, accounting for processing time
                next_run = datetime.now() + timedelta(seconds=interval)
                logger.info(f"Waiting until {next_run.strftime('%Y-%m-%d %H:%M:%S')} for next update...")
                time.sleep(interval)
                
        except KeyboardInterrupt:
            logger.info("\nMonitoring stopped by user.")
        except Exception as e:
            logger.error(f"Error during monitoring: {e}", exc_info=True)
