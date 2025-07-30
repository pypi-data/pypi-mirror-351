"""Base scraper class for LLM model providers."""
from abc import ABC, abstractmethod
from datetime import datetime
import json
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union

logger = logging.getLogger(__name__)

class BaseScraper(ABC):
    """Base class for model scrapers."""
    
    def __init__(self, output_dir: Optional[Union[str, Path]] = None):
        """Initialize the scraper with an optional output directory.
        
        Args:
            output_dir: Directory to save scraped data. If None, uses a default directory.
        """
        self.output_dir = Path(output_dir) if output_dir else Path.cwd() / "data"
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    @abstractmethod
    def scrape_models(self, **kwargs) -> List[Dict[str, Any]]:
        """Scrape models from the provider.
        
        Returns:
            List of model dictionaries.
        """
        pass
    
    def monitor(self, interval: int = 3600, **kwargs) -> None:
        """Monitor for changes in available models.
        
        Args:
            interval: Time in seconds between checks.
            **kwargs: Additional arguments to pass to scrape_models.
        """
        import time
        from datetime import datetime, timedelta
        
        logger.info(f"Starting {self.__class__.__name__} monitor...")
        logger.info(f"Data will be saved to: {self.output_dir}")
        logger.info(f"Press Ctrl+C to stop monitoring")
        
        prev_fingerprint = None
        
        try:
            while True:
                try:
                    models = self.scrape_models(**kwargs)
                    if not models:
                        logger.warning("No models found in this iteration.")
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
                    
                except Exception as e:
                    logger.error(f"Error during monitoring: {e}", exc_info=True)
                    logger.info("Waiting 60 seconds before retrying...")
                    time.sleep(60)
                    
        except KeyboardInterrupt:
            logger.info("\nMonitoring stopped by user.")
    
    def _get_models_fingerprint(self, models: List[Dict[str, Any]]) -> str:
        """Create a fingerprint of the models data to detect changes.
        
        Args:
            models: List of model dictionaries.
            
        Returns:
            A string fingerprint of the models data.
        """
        import hashlib
        import json
        
        def make_hashable(obj):
            if isinstance(obj, (str, int, float, bool, bytes)) or obj is None:
                return obj
            elif isinstance(obj, dict):
                return tuple(sorted((k, make_hashable(v)) for k, v in obj.items()))
            elif isinstance(obj, (list, tuple, set)):
                return tuple(sorted(make_hashable(x) for x in obj))
            else:
                return str(obj)
        
        # Sort models by name for consistent ordering
        sorted_models = sorted(models, key=lambda x: x.get('name', '').lower())
        
        # Create a hash of the sorted models data
        data = json.dumps(
            [make_hashable(model) for model in sorted_models],
            sort_keys=True
        ).encode('utf-8')
        
        return hashlib.md5(data).hexdigest()
    
    def _save_models_data(
        self, 
        models: List[Dict[str, Any]], 
        prev_fingerprint: Optional[str] = None
    ) -> Tuple[Optional[Path], str]:
        """Save models data to a JSON file if it has changed.
        
        Args:
            models: List of model dictionaries.
            prev_fingerprint: Previous fingerprint to compare against.
            
        Returns:
            Tuple of (saved_file_path, new_fingerprint).
            If no changes detected, returns (None, current_fingerprint).
        """
        if not models:
            logger.warning("No models to save.")
            return None, ""
        
        current_fingerprint = self._get_models_fingerprint(models)
        
        # Only save if the data has changed
        if current_fingerprint and current_fingerprint != prev_fingerprint:
            try:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = self.output_dir / f"{self.__class__.__name__.lower()}_models_{timestamp}.json"
                
                # Ensure output directory exists
                self.output_dir.mkdir(parents=True, exist_ok=True)
                
                # Save to JSON file
                with open(filename, 'w', encoding='utf-8') as f:
                    json.dump({
                        'timestamp': datetime.now().isoformat(),
                        'model_count': len(models),
                        'models': models
                    }, f, indent=2, ensure_ascii=False, sort_keys=True)
                
                logger.info(f"Saved {len(models)} models to {filename}")
                return filename, current_fingerprint
                
            except Exception as e:
                logger.error(f"Error saving models data: {e}", exc_info=True)
        else:
            logger.info("No changes detected in model data, skipping save.")
        
        return None, current_fingerprint
