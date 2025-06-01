# setup.py
from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="ai-pricing-tracker",
    version="0.1.0",
    author="Your Name",
    author_email="your.email@example.com",
    description="Auto-updating AI API pricing data for Claude, OpenAI, and more",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/YOUR_USERNAME/ai-pricing-tracker",
    project_urls={
        "Bug Tracker": "https://github.com/YOUR_USERNAME/ai-pricing-tracker/issues",
        "Documentation": "https://github.com/YOUR_USERNAME/ai-pricing-tracker#readme",
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    python_requires=">=3.8",
    install_requires=[
        "requests>=2.28.0",
        "python-dateutil>=2.8.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0",
            "black>=22.0",
            "flake8>=4.0",
            "mypy>=0.990",
            "build>=0.7.0",
            "twine>=4.0.0",
        ],
        "scraper": [
            "playwright>=1.30.0",
            "beautifulsoup4>=4.11.0",
        ],
    },
    package_data={
        "ai_pricing_tracker": ["data/*.json"],
    },
    entry_points={
        "console_scripts": [
            "ai-pricing-update=ai_pricing_tracker.cli:main",
        ],
    },
)

# pyproject.toml (modern Python packaging)
[build-system]
requires = ["setuptools>=61.0", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "ai-pricing-tracker"
version = "0.1.0"
authors = [
    {name = "Your Name", email = "your.email@example.com"},
]
description = "Auto-updating AI API pricing data for Claude, OpenAI, and more"
readme = "README.md"
requires-python = ">=3.8"
license = {text = "MIT"}
keywords = ["ai", "pricing", "api", "openai", "anthropic", "claude", "gpt"]
classifiers = [
    "Development Status :: 4 - Beta",
    "Intended Audience :: Developers",
    "License :: OSI Approved :: MIT License",
    "Programming Language :: Python :: 3",
    "Topic :: Software Development :: Libraries :: Python Modules",
]
dependencies = [
    "requests>=2.28.0",
    "python-dateutil>=2.8.0",
]

[project.urls]
Homepage = "https://github.com/YOUR_USERNAME/ai-pricing-tracker"
Documentation = "https://github.com/YOUR_USERNAME/ai-pricing-tracker#readme"
Repository = "https://github.com/YOUR_USERNAME/ai-pricing-tracker"
Issues = "https://github.com/YOUR_USERNAME/ai-pricing-tracker/issues"

[project.optional-dependencies]
dev = [
    "pytest>=7.0",
    "black>=22.0",
    "flake8>=4.0",
    "mypy>=0.990",
    "build>=0.7.0",
    "twine>=4.0.0",
]
scraper = [
    "playwright>=1.30.0",
    "beautifulsoup4>=4.11.0",
]

[project.scripts]
ai-pricing-update = "ai_pricing_tracker.cli:main"

# src/ai_pricing_tracker/__init__.py
"""
AI Pricing Tracker
Auto-updating pricing data for AI APIs including OpenAI, Anthropic, and more.
"""

__version__ = "0.1.0"
__author__ = "Your Name"
__email__ = "your.email@example.com"

from .manager import PricingManager
from .models import PricingData, ModelPricing
from .exceptions import PricingError, PricingNotFoundError

__all__ = [
    "PricingManager",
    "PricingData", 
    "ModelPricing",
    "PricingError",
    "PricingNotFoundError",
]

# Convenience function for quick access
def get_pricing(provider: str, model: str) -> tuple:
    """
    Quick helper to get pricing for a model.
    
    Args:
        provider: Provider name (e.g., 'anthropic', 'openai')
        model: Model name (e.g., 'claude-opus-4', 'gpt-4')
        
    Returns:
        Tuple of (input_price_per_1m, output_price_per_1m)
    """
    manager = PricingManager()
    return manager.get_model_pricing(provider, model)

# src/ai_pricing_tracker/manager.py
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
from .exceptions import PricingError, PricingNotFoundError

logger = logging.getLogger(__name__)

class PricingManager:
    """
    Manage AI API pricing data with automatic updates.
    
    Automatically fetches the latest pricing data from the community-maintained
    repository and caches it locally. Updates are fetched at most once per day.
    """
    
    # Default GitHub URL for pricing data
    DEFAULT_PRICING_URL = "https://raw.githubusercontent.com/ai-pricing-tracker/data/main/pricing_simple.json"
    
    def __init__(self, 
                 cache_dir: Optional[Path] = None,
                 update_url: Optional[str] = None,
                 auto_update: bool = True,
                 cache_hours: int = 24):
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
            "AI_PRICING_TRACKER_URL", 
            self.DEFAULT_PRICING_URL
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
        
        return self._pricing_data
    
    def _should_update(self) -> bool:
        """Check if pricing data should be updated."""
        if not self.auto_update:
            return False
            
        if not self.cache_file.exists():
            return True
            
        # Check cache age
        cache_age = datetime.now() - datetime.fromtimestamp(
            self.cache_file.stat().st_mtime
        )
        return cache_age > timedelta(hours=self.cache_hours)
    
    def _fetch_latest_pricing(self):
        """Fetch latest pricing from GitHub."""
        logger.info(f"Fetching latest pricing from {self.update_url}")
        
        response = requests.get(self.update_url, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        self._pricing_data = PricingData.from_dict(data)
        
        # Cache the data
        with open(self.cache_file, 'w') as f:
            json.dump(data, f, indent=2)
        
        logger.info("Successfully updated pricing data")
    
    def _load_from_cache(self):
        """Load pricing from local cache."""
        with open(self.cache_file, 'r') as f:
            data = json.load(f)
        self._pricing_data = PricingData.from_dict(data)
    
    def _load_bundled_data(self):
        """Load bundled pricing data (fallback)."""
        # This would load from package data
        bundled_file = Path(__file__).parent / "data" / "default_pricing.json"
        if bundled_file.exists():
            with open(bundled_file, 'r') as f:
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
        if not self._pricing_data:
            self.load_pricing()
        
        key = f"{provider.lower()}/{model.lower()}"
        
        if key in self._pricing_data.models:
            model_pricing = self._pricing_data.models[key]
            return (model_pricing.input_price, model_pricing.output_price)
        
        # Try without provider prefix
        if model.lower() in self._pricing_data.models:
            model_pricing = self._pricing_data.models[model.lower()]
            return (model_pricing.input_price, model_pricing.output_price)
        
        raise PricingNotFoundError(f"Pricing not found for {provider}/{model}")
    
    def calculate_cost(self, 
                      provider: str, 
                      model: str, 
                      input_tokens: int, 
                      output_tokens: int) -> float:
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
        
        if provider:
            provider_lower = provider.lower()
            return {
                k: v for k, v in self._pricing_data.models.items()
                if k.startswith(f"{provider_lower}/")
            }
        
        return self._pricing_data.models
    
    def get_last_updated(self) -> datetime:
        """Get the last update timestamp."""
        if not self._pricing_data:
            self.load_pricing()
        return self._pricing_data.last_updated

# src/ai_pricing_tracker/cli.py
"""Command-line interface for AI Pricing Tracker"""

import argparse
import json
import sys
from typing import Optional

from .manager import PricingManager
from .exceptions import PricingNotFoundError

def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="AI Pricing Tracker - Get current AI API pricing"
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Commands")
    
    # List models command
    list_parser = subparsers.add_parser("list", help="List available models")
    list_parser.add_argument(
        "--provider", 
        help="Filter by provider (e.g., anthropic, openai)"
    )
    list_parser.add_argument(
        "--json", 
        action="store_true",
        help="Output as JSON"
    )
    
    # Get pricing command
    get_parser = subparsers.add_parser("get", help="Get pricing for a model")
    get_parser.add_argument("provider", help="Provider name")
    get_parser.add_argument("model", help="Model name")
    
    # Calculate cost command
    calc_parser = subparsers.add_parser("calc", help="Calculate API call cost")
    calc_parser.add_argument("provider", help="Provider name")
    calc_parser.add_argument("model", help="Model name")
    calc_parser.add_argument("input_tokens", type=int, help="Input token count")
    calc_parser.add_argument("output_tokens", type=int, help="Output token count")
    
    # Update command
    update_parser = subparsers.add_parser("update", help="Force update pricing data")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 1
    
    manager = PricingManager()
    
    try:
        if args.command == "list":
            models = manager.list_models(args.provider)
            
            if args.json:
                output = {
                    k: {
                        "input": v.input_price,
                        "output": v.output_price,
                        "currency": v.currency
                    }
                    for k, v in models.items()
                }
                print(json.dumps(output, indent=2))
            else:
                print(f"Available models (Last updated: {manager.get_last_updated()}):\n")
                for key, pricing in sorted(models.items()):
                    print(f"{key}:")
                    print(f"  Input:  ${pricing.input_price:>7.2f} per 1M tokens")
                    print(f"  Output: ${pricing.output_price:>7.2f} per 1M tokens")
                    print()
        
        elif args.command == "get":
            input_price, output_price = manager.get_model_pricing(
                args.provider, args.model
            )
            print(f"{args.provider}/{args.model}:")
            print(f"  Input:  ${input_price:.2f} per 1M tokens")
            print(f"  Output: ${output_price:.2f} per 1M tokens")
        
        elif args.command == "calc":
            cost = manager.calculate_cost(
                args.provider, 
                args.model,
                args.input_tokens,
                args.output_tokens
            )
            print(f"Cost calculation for {args.provider}/{args.model}:")
            print(f"  Input tokens:  {args.input_tokens:,}")
            print(f"  Output tokens: {args.output_tokens:,}")
            print(f"  Total cost:    ${cost:.6f}")
        
        elif args.command == "update":
            print("Updating pricing data...")
            manager.load_pricing(force_update=True)
            print(f"Updated successfully. Last updated: {manager.get_last_updated()}")
        
        return 0
        
    except PricingNotFoundError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        return 1

if __name__ == "__main__":
    sys.exit(main())