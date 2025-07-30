"""
Pytest configuration and fixtures for llm-list tests.
"""
import json
from pathlib import Path
from typing import Any, Dict, List

import pytest

# Sample data for testing
SAMPLE_OLLAMA_HTML = """
<!DOCTYPE html>
<html>
<head><title>Ollama Models</title></head>
<body>
  <ul>
    <li x-test-model>
      <h2>llama2</h2>
      <p>A foundational model by Meta</p>
      <div class="flex space-x-5">
        <span>Pulls: 1.2M</span>
        <span>Updated: 2 months ago</span>
      </div>
      <div>
        <span class="bg-gray-100">7B</span>
        <span class="inline-flex items-center rounded-md">text-generation</span>
      </div>
      <a href="/library/llama2">View</a>
    </li>
  </ul>
</body>
</html>
"""

SAMPLE_HF_RESPONSE = [
    {
        "id": "codellama/CodeLlama-7b-hf",
        "cardData": {
            "description": "Code completion model from Meta, 7B parameters"
        },
        "tags": ["code", "7b", "meta"],
        "downloads": 1200000,
        "likes": 3500,
        "lastModified": "2023-10-15T12:00:00Z",
        "pipeline_tag": "text-generation",
        "siblings": [
            {"rfilename": "pytorch_model.bin"},
            {"rfilename": "model.safetensors"}
        ]
    }
]

@pytest.fixture
def mock_ollama_response():
    """Return sample HTML response from Ollama library."""
    return SAMPLE_OLLAMA_HTML

@pytest.fixture
def mock_hf_response():
    """Return sample JSON response from Hugging Face API."""
    return SAMPLE_HF_RESPONSE

@pytest.fixture
def temp_output_dir(tmp_path):
    """Create a temporary output directory for tests."""
    return tmp_path / "output"

@pytest.fixture
def ollama_scraper(temp_output_dir):
    """Create an OllamaScraper instance with a temporary output directory."""
    from llm_list.scrapers.ollama import OllamaScraper
    return OllamaScraper(output_dir=temp_output_dir)

@pytest.fixture
def hf_scraper(temp_output_dir):
    """Create a HuggingFaceScraper instance with a temporary output directory."""
    from llm_list.scrapers.huggingface import HuggingFaceScraper
    return HuggingFaceScraper(output_dir=temp_output_dir)
