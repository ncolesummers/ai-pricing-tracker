"""Core pricing manager with automatic updates"""

import json
import os
from pathlib import Path
from typing import Dict, Optional, Tuple
from datetime import datetime, timedelta
import requests
from functools import lru_cache
import logging

from .models import PricingData, ModelPricing
from .exceptions import PricingNotFoundError

logger = logging.getLogger(__name__)


class PricingManager:
    """
    Manage AI API pricing data with automatic updates.

    Automatically fetches the latest pricing data from the community-maintained
    repository and caches it locally. Updates are fetched at most once per day.
    """

    # Default GitHub URL for pricing data
    DEFAULT_PRICING_URL = (
        "https://raw.githubusercontent.com/colesummers/ai-pricing-tracker/"
        "main/data/pricing/pricing_simple.json"
    )

    def __init__(
        self,
        cache_dir: Optional[Path] = None,
        update_url: Optional[str] = None,
        auto_update: bool = True,
        cache_hours: int = 24,
    ):
        """
        Initialize the pricing manager.

        Args:
            cache_dir: Directory to cache pricing data (default: ~/.ai_pricing_tracker)
            update_url: Custom URL for pricing updates
            auto_update: Whether to automatically fetch updates
            cache_hours: How many hours to cache data before updating
        """
        self.cache_dir = cache_dir or Path.home() / ".ai_pricing_tracker"
        self.cache_dir.mkdir(parents=True, exist_ok=True)

        self.update_url = update_url or os.getenv(
            "AI_PRICING_TRACKER_URL", self.DEFAULT_PRICING_URL
        )
        self.auto_update = auto_update
        self.cache_hours = cache_hours

        self.cache_file = self.cache_dir / "pricing_cache.json"
        self._pricing_data: Optional[PricingData] = None

        # Load pricing on initialization
        self.load_pricing()

    def load_pricing(self, force_update: bool = False) -> PricingData:
        """
        Load pricing data, updating if necessary.

        Args:
            force_update: Force an update even if cache is fresh

        Returns:
            PricingData object with current pricing
        """
        if self._should_update() or force_update:
            try:
                self._fetch_latest_pricing()
            except Exception as e:
                logger.warning(f"Failed to fetch latest pricing: {e}")
                # Fall back to cached data
                if self.cache_file.exists():
                    self._load_from_cache()
                else:
                    # Use bundled data as last resort
                    self._load_bundled_data()
        else:
            self._load_from_cache()

        if self._pricing_data is None:
            # This should never happen, but prevents mypy error
            self._pricing_data = PricingData.get_default()

        return self._pricing_data

    def _should_update(self) -> bool:
        """Check if pricing data should be updated."""
        if not self.auto_update:
            return False

        if not self.cache_file.exists():
            return True

        # Check cache age
        cache_age = datetime.now() - datetime.fromtimestamp(self.cache_file.stat().st_mtime)
        return cache_age > timedelta(hours=self.cache_hours)

    def _fetch_latest_pricing(self) -> None:
        """Fetch latest pricing from GitHub."""
        logger.info(f"Fetching latest pricing from {self.update_url}")

        # Use str() to ensure we pass a string, not Optional[str]
        url = str(self.update_url)
        response = requests.get(url, timeout=10)
        response.raise_for_status()

        data = response.json()
        self._pricing_data = PricingData.from_dict(data)

        # Cache the data
        with open(self.cache_file, "w") as f:
            json.dump(data, f, indent=2)

        logger.info("Successfully updated pricing data")

    def _load_from_cache(self) -> None:
        """Load pricing from local cache."""
        with open(self.cache_file, "r") as f:
            data = json.load(f)
        self._pricing_data = PricingData.from_dict(data)

    def _load_bundled_data(self) -> None:
        """Load bundled pricing data (fallback)."""
        # This would load from package data
        bundled_file = Path(__file__).parent / "data" / "default_pricing.json"
        if bundled_file.exists():
            with open(bundled_file, "r") as f:
                data = json.load(f)
            self._pricing_data = PricingData.from_dict(data)
        else:
            # Ultimate fallback - hardcoded data
            self._pricing_data = PricingData.get_default()

    @lru_cache(maxsize=128)
    def get_model_pricing(self, provider: str, model: str) -> Tuple[float, float]:
        """
        Get input and output pricing for a specific model.

        Args:
            provider: Provider name (e.g., 'anthropic', 'openai')
            model: Model name (e.g., 'claude-opus-4', 'gpt-4')

        Returns:
            Tuple of (input_price_per_1m_tokens, output_price_per_1m_tokens)

        Raises:
            PricingNotFoundError: If model pricing not found
        """
        # Load pricing data if not loaded yet
        if not self._pricing_data:
            self.load_pricing()

        # At this point self._pricing_data should never be None due to our check in load_pricing
        assert self._pricing_data is not None, "Pricing data should not be None"

        key = f"{provider.lower()}/{model.lower()}"

        if key in self._pricing_data.models:
            model_pricing = self._pricing_data.models[key]
            return (model_pricing.input_price, model_pricing.output_price)

        # Try without provider prefix
        if model.lower() in self._pricing_data.models:
            model_pricing = self._pricing_data.models[model.lower()]
            return (model_pricing.input_price, model_pricing.output_price)

        raise PricingNotFoundError(f"Pricing not found for {provider}/{model}")

    def calculate_cost(
        self, provider: str, model: str, input_tokens: int, output_tokens: int
    ) -> float:
        """
        Calculate total cost for an API call.

        Args:
            provider: Provider name
            model: Model name
            input_tokens: Number of input tokens
            output_tokens: Number of output tokens

        Returns:
            Total cost in USD
        """
        input_price, output_price = self.get_model_pricing(provider, model)

        input_cost = (input_tokens / 1_000_000) * input_price
        output_cost = (output_tokens / 1_000_000) * output_price

        return round(input_cost + output_cost, 6)

    def list_models(self, provider: Optional[str] = None) -> Dict[str, ModelPricing]:
        """
        List available models and their pricing.

        Args:
            provider: Optional provider filter

        Returns:
            Dictionary of model keys to ModelPricing objects
        """
        if not self._pricing_data:
            self.load_pricing()

        # At this point self._pricing_data should never be None due to our check in load_pricing
        assert self._pricing_data is not None, "Pricing data should not be None"

        if provider:
            provider_lower = provider.lower()
            return {
                k: v
                for k, v in self._pricing_data.models.items()
                if k.startswith(f"{provider_lower}/")
            }

        return self._pricing_data.models

    def get_last_updated(self) -> datetime:
        """Get the last update timestamp."""
        if not self._pricing_data:
            self.load_pricing()

        # At this point self._pricing_data should never be None due to our check in load_pricing
        assert self._pricing_data is not None, "Pricing data should not be None"

        return self._pricing_data.last_updated
