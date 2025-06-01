#!/usr/bin/env python3
"""Validate scraped pricing data for consistency and completeness"""

import json
import sys
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def validate_pricing_data():
    """Validate the pricing data structure and values"""
    pricing_file = Path("data/pricing/current_pricing.json")

    if not pricing_file.exists():
        logger.error("Pricing file not found")
        return False

    with open(pricing_file) as f:
        data = json.load(f)

    # Check required fields
    if "providers" not in data or "last_updated" not in data:
        logger.error("Missing required top-level fields")
        return False

    # Validate each provider
    for provider in data["providers"]:
        if "models" not in provider:
            logger.error(f"Missing models for provider {provider.get('provider', 'unknown')}")
            return False

        # Check that we have at least some models
        if len(provider["models"]) == 0:
            logger.error(f"No models found for {provider.get('provider', 'unknown')}")
            return False

        # Validate each model
        for model_key, model_data in provider["models"].items():
            # Check for reasonable prices (not 0, not too high)
            input_price = model_data.get("input_price_per_1m_tokens", 0)
            output_price = model_data.get("output_price_per_1m_tokens", 0)

            if input_price <= 0 or input_price > 1000:
                logger.warning(f"Suspicious input price for {model_key}: ${input_price}")

            if output_price <= 0 or output_price > 1000:
                logger.warning(f"Suspicious output price for {model_key}: ${output_price}")

    logger.info("Pricing data validation passed")
    return True


if __name__ == "__main__":
    if not validate_pricing_data():
        sys.exit(1)
