"""Tests for the pricing scraper."""

import json
import pytest
from pathlib import Path
from unittest.mock import Mock, patch

from ai_pricing_tracker.scripts.scrape_pricing import AIPricingScraper


@pytest.fixture
def scraper(tmp_path: Path) -> AIPricingScraper:
    """Create a scraper instance with temp directory."""
    return AIPricingScraper()


class TestAIPricingScraper:
    """Test cases for the pricing scraper."""

    def test_initialization(self, scraper: AIPricingScraper) -> None:
        """Test scraper initialization."""
        assert scraper.data_dir.exists()
        assert scraper.timestamp is not None

    def test_normalize_model_name(self, scraper: AIPricingScraper) -> None:
        """Test model name normalization."""
        assert scraper.normalize_model_name("Claude Opus 4") == "claude-opus-4"
        assert scraper.normalize_model_name("GPT-4") == "gpt-4"
        assert scraper.normalize_model_name("claude.opus.4") == "claude-opus-4"

    def test_parse_price(self, scraper: AIPricingScraper) -> None:
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

    def test_create_simplified_pricing(self, scraper: AIPricingScraper) -> None:
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
                            "currency": "USD",
                        }
                    },
                },
                {
                    "provider": "openai",
                    "models": {
                        "gpt-4": {
                            "input_price_per_1m_tokens": 30.0,
                            "output_price_per_1m_tokens": 60.0,
                            "currency": "USD",
                        }
                    },
                },
            ],
        }

        simplified = scraper.create_simplified_pricing(all_pricing)

        assert "anthropic/claude-opus-4" in simplified["pricing"]
        assert "openai/gpt-4" in simplified["pricing"]
        assert simplified["pricing"]["anthropic/claude-opus-4"]["input"] == 15.0
        assert simplified["pricing"]["openai/gpt-4"]["output"] == 60.0

    @patch("ai_pricing_tracker.scripts.scrape_pricing.sync_playwright")
    def test_scrape_anthropic_pricing_fallback(
        self, mock_playwright: Mock, scraper: AIPricingScraper
    ) -> None:
        """Test Anthropic scraping with fallback data."""
        # Mock playwright to raise an exception when called
        mock_playwright.side_effect = Exception("Network error")

        result = scraper.scrape_anthropic_pricing()

        assert result["provider"] == "anthropic"
        assert "claude-opus-4" in result["models"]
        assert "scraping_error" in result
        assert result["models"]["claude-opus-4"]["note"] == "Fallback data - update manually"

    @patch("ai_pricing_tracker.scripts.scrape_pricing.sync_playwright")
    def test_scrape_openai_pricing_fallback(
        self, mock_playwright: Mock, scraper: AIPricingScraper
    ) -> None:
        """Test OpenAI scraping with fallback data."""
        # Mock playwright to raise an exception when called
        mock_playwright.side_effect = Exception("Network error")

        result = scraper.scrape_openai_pricing()

        assert result["provider"] == "openai"
        assert "gpt-4" in result["models"]
        assert "scraping_error" in result
        assert result["models"]["gpt-4"]["note"] == "Fallback data - update manually"

    def test_save_pricing_data(self, scraper: AIPricingScraper, tmp_path: Path) -> None:
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
                            "output_price_per_1m_tokens": 20.0,
                        }
                    },
                }
            ],
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
