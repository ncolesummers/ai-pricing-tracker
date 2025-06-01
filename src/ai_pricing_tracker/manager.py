"""
Core pricing manager with automatic updates.

This module provides the main interface for accessing AI API pricing data.
It handles automatic updates, caching, and fallback mechanisms to ensure
pricing data is always available, even when offline.
"""

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

    The PricingManager is the main entry point for accessing AI model pricing data.
    It automatically fetches the latest pricing from the community-maintained
    repository and caches it locally for offline use. The manager handles
    various failure scenarios with fallback options to ensure it always returns
    valid pricing data.

    Features:
        - Automatic updates when pricing data is outdated
        - Local caching for offline use
        - Fallback to bundled data when network is unavailable
        - Model price lookup by provider/model name
        - Token cost calculation
        - Listing of available models

    Examples:
        >>> from ai_pricing_tracker import PricingManager
        >>> pricing = PricingManager()
        >>> input_price, output_price = pricing.get_model_pricing("anthropic", "claude-opus-4")
        >>> cost = pricing.calculate_cost("openai", "gpt-4", 1000, 500)
        >>> models = pricing.list_models(provider="anthropic")
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
            cache_dir: Directory to cache pricing data. If None, defaults to
                ~/.ai_pricing_tracker
            update_url: Custom URL for pricing updates. If None, uses the
                default community-maintained repository. Can also be set via
                the AI_PRICING_TRACKER_URL environment variable.
            auto_update: Whether to automatically fetch updates when cache is
                outdated. Set to False in environments where you want explicit
                control over when updates occur.
            cache_hours: How many hours to consider cached data valid before
                attempting to update. Default is 24 hours.

        Note:
            The manager will fetch pricing data upon initialization unless
            auto_update is set to False.
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

        This method is the main entry point for loading pricing data. It handles
        the following scenarios in order:
        1. Check if an update is needed (based on cache age) or forced
        2. Attempt to fetch the latest pricing data from the remote source
        3. If fetching fails, attempt to load from local cache
        4. If local cache doesn't exist, fall back to bundled data
        5. If all else fails, use hardcoded default data

        Args:
            force_update: Force an update even if cache is fresh. Useful for
                ensuring you have the latest pricing data.

        Returns:
            PricingData object with current pricing information

        Note:
            This method is called automatically during initialization,
            but can be called manually to force a refresh.
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
        """
        Check if pricing data should be updated.

        Determines whether to update the pricing data based on:
        1. The auto_update setting
        2. Whether a cache file exists
        3. The age of the cached data

        Returns:
            True if data should be updated, False otherwise
        """
        if not self.auto_update:
            return False

        if not self.cache_file.exists():
            return True

        # Check cache age
        cache_age = datetime.now() - datetime.fromtimestamp(self.cache_file.stat().st_mtime)
        return cache_age > timedelta(hours=self.cache_hours)

    def _fetch_latest_pricing(self) -> None:
        """
        Fetch latest pricing from the remote source.

        Makes an HTTP request to retrieve the latest pricing data, parses it,
        and stores it both in memory and in the local cache file.

        Raises:
            requests.RequestException: If there's an error fetching the data
            json.JSONDecodeError: If the response isn't valid JSON
        """
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
        """
        Load pricing from local cache.

        Reads the cached pricing data from disk and parses it into
        a PricingData object.

        Raises:
            FileNotFoundError: If cache file doesn't exist
            json.JSONDecodeError: If cache file isn't valid JSON
        """
        with open(self.cache_file, "r") as f:
            data = json.load(f)
        self._pricing_data = PricingData.from_dict(data)

    def _load_bundled_data(self) -> None:
        """
        Load bundled pricing data (fallback).

        Attempts to load pricing data bundled with the package.
        If that fails, falls back to hardcoded default data.
        """
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

        Retrieves the pricing information for a given AI model, identified by
        its provider and model name. The pricing is returned as a tuple of
        input and output prices per 1 million tokens.

        Args:
            provider: Provider name (e.g., 'anthropic', 'openai')
            model: Model name (e.g., 'claude-opus-4', 'gpt-4')

        Returns:
            Tuple of (input_price_per_1m_tokens, output_price_per_1m_tokens)

        Raises:
            PricingNotFoundError: If pricing for the specified model cannot be found

        Examples:
            >>> pricing = PricingManager()
            >>> input_price, output_price = pricing.get_model_pricing("openai", "gpt-4")
            >>> print(f"GPT-4 costs ${input_price}/1M input tokens, ${output_price}/1M output tokens")
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

        Computes the total cost for a model API call based on the number of
        input and output tokens used.

        Args:
            provider: Provider name (e.g., 'anthropic', 'openai')
            model: Model name (e.g., 'claude-opus-4', 'gpt-4')
            input_tokens: Number of input/prompt tokens
            output_tokens: Number of output/completion tokens

        Returns:
            Total cost in USD, rounded to 6 decimal places

        Raises:
            PricingNotFoundError: If pricing for the specified model cannot be found

        Examples:
            >>> pricing = PricingManager()
            >>> cost = pricing.calculate_cost("anthropic", "claude-opus-4", 1000, 500)
            >>> print(f"API call cost: ${cost:.4f}")
        """
        input_price, output_price = self.get_model_pricing(provider, model)

        input_cost = (input_tokens / 1_000_000) * input_price
        output_cost = (output_tokens / 1_000_000) * output_price

        return round(input_cost + output_cost, 6)

    def list_models(self, provider: Optional[str] = None) -> Dict[str, ModelPricing]:
        """
        List available models and their pricing.

        Returns a dictionary of all available models and their pricing information.
        If a provider is specified, only models from that provider are returned.

        Args:
            provider: Optional provider filter (e.g., 'anthropic', 'openai')

        Returns:
            Dictionary mapping model keys to ModelPricing objects

        Examples:
            >>> pricing = PricingManager()
            >>> # Get all models
            >>> all_models = pricing.list_models()
            >>> # Get only Anthropic models
            >>> anthropic_models = pricing.list_models("anthropic")
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
        """
        Get the last update timestamp.

        Returns the timestamp when the pricing data was last updated.

        Returns:
            Datetime object representing when the pricing data was last updated

        Examples:
            >>> pricing = PricingManager()
            >>> last_updated = pricing.get_last_updated()
            >>> print(f"Pricing data last updated: {last_updated.isoformat()}")
        """
        if not self._pricing_data:
            self.load_pricing()

        # At this point self._pricing_data should never be None due to our check in load_pricing
        assert self._pricing_data is not None, "Pricing data should not be None"

        return self._pricing_data.last_updated