"""Tests for the PricingManager class."""

import json
import os
import pytest
from datetime import datetime, timedelta
from unittest.mock import Mock, patch
from pathlib import Path

from ai_pricing_tracker import PricingManager, PricingNotFoundError


@pytest.fixture
def temp_cache_dir(tmp_path: Path) -> Path:
    """Create a temporary cache directory."""
    cache_dir = tmp_path / "test_cache"
    cache_dir.mkdir()
    return cache_dir


@pytest.fixture
def mock_pricing_data() -> dict:
    """Create mock pricing data."""
    return {
        "last_updated": datetime.utcnow().isoformat(),
        "pricing": {
            "anthropic/claude-opus-4": {"input": 15.0, "output": 75.0, "currency": "USD"},
            "openai/gpt-4": {"input": 30.0, "output": 60.0, "currency": "USD"},
        },
    }


class TestPricingManager:
    """Test cases for PricingManager."""

    def test_initialization(self, temp_cache_dir: Path) -> None:
        """Test manager initialization."""
        manager = PricingManager(cache_dir=temp_cache_dir, auto_update=False)
        assert manager.cache_dir == temp_cache_dir
        assert manager.cache_file == temp_cache_dir / "pricing_cache.json"

    def test_get_model_pricing_success(self, temp_cache_dir: Path, mock_pricing_data: dict) -> None:
        """Test successful model pricing retrieval."""
        # Create cache file
        cache_file = temp_cache_dir / "pricing_cache.json"
        with open(cache_file, "w") as f:
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

    def test_get_model_pricing_not_found(
        self, temp_cache_dir: Path, mock_pricing_data: dict
    ) -> None:
        """Test pricing not found error."""
        cache_file = temp_cache_dir / "pricing_cache.json"
        with open(cache_file, "w") as f:
            json.dump(mock_pricing_data, f)

        manager = PricingManager(cache_dir=temp_cache_dir, auto_update=False)

        with pytest.raises(PricingNotFoundError):
            manager.get_model_pricing("anthropic", "nonexistent-model")

    def test_calculate_cost(self, temp_cache_dir: Path, mock_pricing_data: dict) -> None:
        """Test cost calculation."""
        cache_file = temp_cache_dir / "pricing_cache.json"
        with open(cache_file, "w") as f:
            json.dump(mock_pricing_data, f)

        manager = PricingManager(cache_dir=temp_cache_dir, auto_update=False)

        # Test with 1000 input tokens and 500 output tokens
        cost = manager.calculate_cost("openai", "gpt-4", 1000, 500)
        expected_cost = (1000 / 1_000_000 * 30.0) + (500 / 1_000_000 * 60.0)
        assert cost == round(expected_cost, 6)

    @patch("requests.get")
    def test_fetch_latest_pricing(self, mock_get: Mock, temp_cache_dir: Path) -> None:
        """Test fetching latest pricing from URL."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "last_updated": datetime.utcnow().isoformat(),
            "pricing": {"test/model": {"input": 10.0, "output": 20.0}},
        }
        mock_get.return_value = mock_response

        manager = PricingManager(cache_dir=temp_cache_dir, auto_update=True)
        manager._fetch_latest_pricing()

        # Check cache file was created
        assert manager.cache_file.exists()
        with open(manager.cache_file) as f:
            data = json.load(f)
        assert "test/model" in data["pricing"]

    def test_should_update(self, temp_cache_dir: Path) -> None:
        """Test update check logic."""
        manager = PricingManager(cache_dir=temp_cache_dir, auto_update=True, cache_hours=24)

        # No cache file - should update
        assert manager._should_update() is True

        # Create fresh cache file
        cache_file = temp_cache_dir / "pricing_cache.json"
        with open(cache_file, "w") as f:
            json.dump({"pricing": {}}, f)

        # Fresh file - should not update
        assert manager._should_update() is False

        # Make file old
        old_time = datetime.now() - timedelta(hours=25)
        os.utime(cache_file, (old_time.timestamp(), old_time.timestamp()))

        # Old file - should update
        assert manager._should_update() is True

    def test_list_models(self, temp_cache_dir: Path, mock_pricing_data: dict) -> None:
        """Test listing models."""
        cache_file = temp_cache_dir / "pricing_cache.json"
        with open(cache_file, "w") as f:
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
