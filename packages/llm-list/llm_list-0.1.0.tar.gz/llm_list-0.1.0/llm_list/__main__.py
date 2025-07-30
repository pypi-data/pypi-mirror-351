""
Command-line interface for LLM List.
"""
import argparse
import logging
import sys
from typing import Optional

from .scrapers.ollama import OllamaScraper
from .scrapers.huggingface import HuggingFaceScraper

logger = logging.getLogger(__name__)

def setup_logging(verbose: bool = False) -> None:
    """Set up basic logging configuration."""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[logging.StreamHandler(sys.stdout)]
    )

def ollama_command(args) -> None:
    """Handle the ollama subcommand."""
    scraper = OllamaScraper()
    
    if args.monitor:
        try:
            scraper.monitor(interval=args.interval)
        except KeyboardInterrupt:
            print("\nMonitoring stopped by user.")
    else:
        models = scraper.scrape_models()
        for model in models:
            print(f"{model['name']} - {model.get('description', 'No description')}")

def huggingface_command(args) -> None:
    """Handle the huggingface subcommand."""
    scraper = HuggingFaceScraper()
    
    if args.monitor:
        try:
            scraper.monitor(interval=args.interval, search_term=args.search)
        except KeyboardInterrupt:
            print("\nMonitoring stopped by user.")
    else:
        models = scraper.scrape_models(search_term=args.search)
        for model in models:
            print(f"{model['name']} - {model.get('description', 'No description')}")

def main() -> None:
    """Parse command line arguments and execute commands."""
    parser = argparse.ArgumentParser(description="List and monitor LLM models from various providers.")
    parser.add_argument("-v", "--verbose", action="store_true", help="Enable verbose output")
    
    subparsers = parser.add_subparsers(dest="command", help="Sub-command help")
    
    # Ollama command
    ollama_parser = subparsers.add_parser("ollama", help="Interact with Ollama models")
    ollama_parser.add_argument("--monitor", action="store_true", help="Monitor for changes")
    ollama_parser.add_argument("--interval", type=int, default=300, 
                             help="Interval in seconds between checks (default: 300)")
    ollama_parser.set_defaults(func=ollama_command)
    
    # Hugging Face command
    hf_parser = subparsers.add_parser("huggingface", aliases=["hf"], 
                                    help="Interact with Hugging Face models")
    hf_parser.add_argument("--monitor", action="store_true", help="Monitor for changes")
    hf_parser.add_argument("--interval", type=int, default=3600,
                         help="Interval in seconds between checks (default: 3600)")
    hf_parser.add_argument("--search", type=str, default="code",
                         help="Search term for filtering models (default: code)")
    hf_parser.set_defaults(func=huggingface_command)
    
    args = parser.parse_args()
    
    setup_logging(args.verbose)
    
    if hasattr(args, 'func'):
        args.func(args)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
