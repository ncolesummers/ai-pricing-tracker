# Test Files for AI Pricing Tracker

## File: tests/test_manager.py

```python
"""Tests for the PricingManager class."""

import json
import pytest
from pathlib import Path
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, MagicMock

from ai_pricing_tracker import PricingManager, PricingNotFoundError
from ai_pricing_tracker.models import PricingData, ModelPricing


@pytest.fixture
def temp_cache_dir(tmp_path):
    """Create a temporary cache directory."""
    cache_dir = tmp_path / "test_cache"
    cache_dir.mkdir()
    return cache_dir


@pytest.fixture
def mock_pricing_data():
    """Create mock pricing data."""
    return {
        "last_updated": datetime.utcnow().isoformat(),
        "pricing": {
            "anthropic/claude-opus-4": {
                "input": 15.0,
                "output": 75.0,
                "currency": "USD"
            },
            "openai/gpt-4": {
                "input": 30.0,
                "output": 60.0,
                "currency": "USD"
            }
        }
    }


class TestPricingManager:
    """Test cases for PricingManager."""
    
    def test_initialization(self, temp_cache_dir):
        """Test manager initialization."""
        manager = PricingManager(cache_dir=temp_cache_dir, auto_update=False)
        assert manager.cache_dir == temp_cache_dir
        assert manager.cache_file == temp_cache_dir / "pricing_cache.json"
    
    def test_get_model_pricing_success(self, temp_cache_dir, mock_pricing_data):
        """Test successful model pricing retrieval."""
        # Create cache file
        cache_file = temp_cache_dir / "pricing_cache.json"
        with open(cache_file, 'w') as f:
            json.dump(mock_pricing_data, f)
        
        manager = PricingManager(cache_dir=temp_cache_dir, auto_update=False)
        
        # Test with provider/model format
        input_price, output_price = manager.get_model_pricing("anthropic", "claude-opus-4")
        assert input_price == 15.0
        assert output_price == 75.0
        
        # Test case insensitive
        input_price, output_price = manager.get_model_pricing("Anthropic", "Claude-Opus-4")
        assert input_price == 15.0
        assert output_price == 75.0
    
    def test_get_model_pricing_not_found(self, temp_cache_dir, mock_pricing_data):
        """Test pricing not found error."""
        cache_file = temp_cache_dir / "pricing_cache.json"
        with open(cache_file, 'w') as f:
            json.dump(mock_pricing_data, f)
        
        manager = PricingManager(cache_dir=temp_cache_dir, auto_update=False)
        
        with pytest.raises(PricingNotFoundError):
            manager.get_model_pricing("anthropic", "nonexistent-model")
    
    def test_calculate_cost(self, temp_cache_dir, mock_pricing_data):
        """Test cost calculation."""
        cache_file = temp_cache_dir / "pricing_cache.json"
        with open(cache_file, 'w') as f:
            json.dump(mock_pricing_data, f)
        
        manager = PricingManager(cache_dir=temp_cache_dir, auto_update=False)
        
        # Test with 1000 input tokens and 500 output tokens
        cost = manager.calculate_cost("openai", "gpt-4", 1000, 500)
        expected_cost = (1000 / 1_000_000 * 30.0) + (500 / 1_000_000 * 60.0)
        assert cost == round(expected_cost, 6)
    
    @patch('requests.get')
    def test_fetch_latest_pricing(self, mock_get, temp_cache_dir):
        """Test fetching latest pricing from URL."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "last_updated": datetime.utcnow().isoformat(),
            "pricing": {
                "test/model": {"input": 10.0, "output": 20.0}
            }
        }
        mock_get.return_value = mock_response
        
        manager = PricingManager(cache_dir=temp_cache_dir, auto_update=True)
        manager._fetch_latest_pricing()
        
        # Check cache file was created
        assert manager.cache_file.exists()
        with open(manager.cache_file) as f:
            data = json.load(f)
        assert "test/model" in data["pricing"]
    
    def test_should_update(self, temp_cache_dir):
        """Test update check logic."""
        manager = PricingManager(cache_dir=temp_cache_dir, auto_update=True, cache_hours=24)
        
        # No cache file - should update
        assert manager._should_update() is True
        
        # Create fresh cache file
        cache_file = temp_cache_dir / "pricing_cache.json"
        with open(cache_file, 'w') as f:
            json.dump({"pricing": {}}, f)
        
        # Fresh file - should not update
        assert manager._should_update() is False
        
        # Make file old
        old_time = datetime.now() - timedelta(hours=25)
        import os
        os.utime(cache_file, (old_time.timestamp(), old_time.timestamp()))
        
        # Old file - should update
        assert manager._should_update() is True
    
    def test_list_models(self, temp_cache_dir, mock_pricing_data):
        """Test listing models."""
        cache_file = temp_cache_dir / "pricing_cache.json"
        with open(cache_file, 'w') as f:
            json.dump(mock_pricing_data, f)
        
        manager = PricingManager(cache_dir=temp_cache_dir, auto_update=False)
        
        # List all models
        all_models = manager.list_models()
        assert len(all_models) == 2
        assert "anthropic/claude-opus-4" in all_models
        assert "openai/gpt-4" in all_models
        
        # Filter by provider
        anthropic_models = manager.list_models("anthropic")
        assert len(anthropic_models) == 1
        assert "anthropic/claude-opus-4" in anthropic_models
        
        openai_models = manager.list_models("openai")
        assert len(openai_models) == 1
        assert "openai/gpt-4" in openai_models
```

## File: tests/test_scraper.py

```python
"""Tests for the pricing scraper."""

import pytest
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path
import json

import sys
sys.path.insert(0, 'scripts')
from scrape_pricing import AIPricingScraper


@pytest.fixture
def scraper(tmp_path):
    """Create a scraper instance with temp directory."""
    return AIPricingScraper()


class TestAIPricingScraper:
    """Test cases for the pricing scraper."""
    
    def test_initialization(self, scraper):
        """Test scraper initialization."""
        assert scraper.data_dir.exists()
        assert scraper.timestamp is not None
    
    def test_normalize_model_name(self, scraper):
        """Test model name normalization."""
        assert scraper.normalize_model_name("Claude Opus 4") == "claude-opus-4"
        assert scraper.normalize_model_name("GPT-4") == "gpt-4"
        assert scraper.normalize_model_name("claude.opus.4") == "claude-opus-4"
    
    def test_parse_price(self, scraper):
        """Test price parsing from various formats."""
        # Test standard format
        assert scraper.parse_price("$15.00 per 1M tokens") == 15.0
        assert scraper.parse_price("10.5 / 1M tokens") == 10.5
        
        # Test simple numeric
        assert scraper.parse_price("25.50") == 25.50
        assert scraper.parse_price("$5") == 5.0
        
        # Test invalid formats
        assert scraper.parse_price("free") is None
        assert scraper.parse_price("") is None
    
    def test_create_simplified_pricing(self, scraper):
        """Test simplified pricing creation."""
        all_pricing = {
            "last_updated": "2024-01-01T00:00:00",
            "providers": [
                {
                    "provider": "anthropic",
                    "models": {
                        "claude-opus-4": {
                            "input_price_per_1m_tokens": 15.0,
                            "output_price_per_1m_tokens": 75.0,
                            "currency": "USD"
                        }
                    }
                },
                {
                    "provider": "openai",
                    "models": {
                        "gpt-4": {
                            "input_price_per_1m_tokens": 30.0,
                            "output_price_per_1m_tokens": 60.0,
                            "currency": "USD"
                        }
                    }
                }
            ]
        }
        
        simplified = scraper.create_simplified_pricing(all_pricing)
        
        assert "anthropic/claude-opus-4" in simplified["pricing"]
        assert "openai/gpt-4" in simplified["pricing"]
        assert simplified["pricing"]["anthropic/claude-opus-4"]["input"] == 15.0
        assert simplified["pricing"]["openai/gpt-4"]["output"] == 60.0
    
    @patch('playwright.sync_api.sync_playwright')
    def test_scrape_anthropic_pricing_fallback(self, mock_playwright, scraper):
        """Test Anthropic scraping with fallback data."""
        # Mock playwright to raise an exception
        mock_playwright.side_effect = Exception("Network error")
        
        result = scraper.scrape_anthropic_pricing()
        
        assert result["provider"] == "anthropic"
        assert "claude-opus-4" in result["models"]
        assert "scraping_error" in result
        assert result["models"]["claude-opus-4"]["note"] == "Fallback data - update manually"
    
    @patch('playwright.sync_api.sync_playwright')
    def test_scrape_openai_pricing_fallback(self, mock_playwright, scraper):
        """Test OpenAI scraping with fallback data."""
        # Mock playwright to raise an exception
        mock_playwright.side_effect = Exception("Network error")
        
        result = scraper.scrape_openai_pricing()
        
        assert result["provider"] == "openai"
        assert "gpt-4" in result["models"]
        assert "scraping_error" in result
        assert result["models"]["gpt-4"]["note"] == "Fallback data - update manually"
    
    def test_save_pricing_data(self, scraper, tmp_path):
        """Test saving pricing data."""
        scraper.data_dir = tmp_path / "test_pricing"
        scraper.data_dir.mkdir()
        
        test_data = {
            "last_updated": "2024-01-01T00:00:00",
            "providers": [
                {
                    "provider": "test",
                    "models": {
                        "test-model": {
                            "input_price_per_1m_tokens": 10.0,
                            "output_price_per_1m_tokens": 20.0
                        }
                    }
                }
            ]
        }
        
        scraper.save_pricing_data(test_data)
        
        # Check current pricing file
        current_file = scraper.data_dir / "current_pricing.json"
        assert current_file.exists()
        
        with open(current_file) as f:
            saved_data = json.load(f)
        assert saved_data == test_data
        
        # Check simplified pricing file
        simple_file = scraper.data_dir / "pricing_simple.json"
        assert simple_file.exists()
        
        with open(simple_file) as f:
            simple_data = json.load(f)
        assert "test/test-model" in simple_data["pricing"]
```