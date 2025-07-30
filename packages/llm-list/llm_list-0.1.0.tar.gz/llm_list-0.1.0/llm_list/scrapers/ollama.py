"""Scraper for Ollama models."""
import json
import logging
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

import requests
from bs4 import BeautifulSoup

from .base import BaseScraper

logger = logging.getLogger(__name__)

class OllamaScraper(BaseScraper):
    """Scraper for Ollama models."""
    
    OLLAMA_LIBRARY_URL = "https://ollama.com/library"
    
    def __init__(self, output_dir: Optional[Union[str, Path]] = None):
        """Initialize the Ollama scraper.
        
        Args:
            output_dir: Directory to save scraped data.
        """
        super().__init__(output_dir)
        self.output_dir = Path(output_dir) if output_dir else Path.cwd() / "ollama_models_data"
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Set up session with headers to mimic a browser
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        })
    
    def scrape_models(self, **kwargs) -> List[Dict[str, Any]]:
        """Scrape available models from Ollama library.
        
        Returns:
            List of model dictionaries.
        """
        logger.info("Scraping Ollama models...")
        logger.info(f"Making request to Ollama library...")
        
        try:
            response = self.session.get(self.OLLAMA_LIBRARY_URL, timeout=30)
            response.raise_for_status()
            
            logger.info(f"Got response with status code: {response.status_code}")
            
            # Save debug HTML for inspection if needed
            debug_file = self.output_dir / "debug_ollama_page.html"
            with open(debug_file, 'w', encoding='utf-8') as f:
                f.write(response.text)
            logger.debug(f"Saved debug HTML to {debug_file}")
            
            logger.info("Parsing HTML content...")
            soup = BeautifulSoup(response.text, 'lxml')
            
            # Find all model items - adjust selector based on actual page structure
            model_items = soup.select('li[x-test-model]')
            logger.info(f"Found {len(model_items)} model items")
            
            models = []
            for i, item in enumerate(model_items, 1):
                try:
                    logger.debug(f"Processing model {i}/{len(model_items)}")
                    
                    # Extract model name from the h2 element
                    h2 = item.select_one('h2')
                    if not h2:
                        logger.debug(f"Skipping model {i} - no h2 found")
                        continue
                        
                    model_name = h2.get_text(strip=True)
                    if not model_name:
                        logger.debug(f"Skipping model {i} - no model name found")
                        continue
                        
                    logger.debug(f"Found model: {model_name}")
                    
                    # Extract model URL
                    model_url = ''
                    link = item.find('a', href=True)
                    if link and link.get('href', '').startswith('/library/'):
                        model_url = f"https://ollama.com{link['href']}"
                    
                    # Extract description - first p tag after h2
                    description = ''
                    desc_p = h2.find_next_sibling('p')
                    if desc_p:
                        description = desc_p.get_text(strip=True)
                    
                    # Extract model sizes from spans with specific classes
                    sizes = []
                    size_spans = item.select('span.bg-gray-100, span.bg-gray-200')
                    for span in size_spans:
                        size_text = span.get_text(strip=True)
                        if size_text and any(x in size_text.lower() for x in ['b', 'k', 'm', 'g']):
                            sizes.append(size_text)
                    
                    # Extract metadata (pulls, last updated, etc.)
                    metadata = {}
                    meta_div = item.select_one('div.flex.space-x-5')
                    if meta_div:
                        for span in meta_div.find_all('span'):
                            text = span.get_text(strip=True)
                            if ':' in text:
                                key, value = text.split(':', 1)
                                metadata[key.strip().lower()] = value.strip()
                    
                    # Extract tags - look for spans with specific classes
                    tags = []
                    tag_elements = item.select('span.inline-flex.items-center.rounded-md')
                    for tag in tag_elements:
                        tag_text = tag.get_text(strip=True)
                        if tag_text and tag_text not in sizes:  # Avoid duplicating size tags
                            tags.append(tag_text)
                    
                    model_data = {
                        'name': model_name,
                        'url': model_url,
                        'description': description or "No description",
                        'sizes': sizes,
                        'tags': tags,
                        'metadata': metadata
                    }
                    models.append(model_data)
                    
                except Exception as e:
                    logger.error(f"Error processing model {i}: {e}", exc_info=True)
            
            logger.info(f"Successfully processed {len(models)} models")
            return models
            
        except requests.RequestException as e:
            logger.error(f"Error fetching Ollama library: {e}")
            return []
        except Exception as e:
            logger.error(f"Unexpected error: {e}", exc_info=True)
            return []

    def monitor(self, interval: int = 300, **kwargs) -> None:
        """Monitor Ollama models for changes.
        
        Args:
            interval: Time in seconds between checks.
            **kwargs: Additional arguments to pass to scrape_models.
        """
        logger.info("Starting Ollama model monitor...")
        logger.info(f"Data will be saved to: {self.output_dir}")
        logger.info("Press Ctrl+C to stop monitoring")
        
        prev_fingerprint = None
        
        try:
            while True:
                models = self.scrape_models(**kwargs)
                if not models:
                    logger.warning("No models found in this iteration.")
                    time.sleep(60)  # Wait a minute before retrying
                    continue
                
                # Save models and get new fingerprint
                filename, new_fingerprint = self._save_models_data(models, prev_fingerprint)
                
                if filename:
                    logger.info(f"Changes detected, saved to {filename}")
                
                prev_fingerprint = new_fingerprint
                
                # Calculate sleep time, accounting for processing time
                next_run = datetime.now() + timedelta(seconds=interval)
                logger.info(f"Waiting until {next_run.strftime('%H:%M:%S')} for next update...")
                time.sleep(interval)
                
        except KeyboardInterrupt:
            logger.info("\nMonitoring stopped by user.")
        except Exception as e:
            logger.error(f"Error during monitoring: {e}", exc_info=True)
