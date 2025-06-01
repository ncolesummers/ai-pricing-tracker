#!/usr/bin/env python3
"""Validate scraped pricing data for consistency and completeness"""

import json
import sys
from pathlib import Path
import logging
from typing import Optional, Union

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def validate_pricing_data(pricing_file: Optional[Union[str, Path]] = None) -> bool:
    """
    Validate the pricing data structure and values

    Args:
        pricing_file: Path to the pricing data file to validate.
                     If None, defaults to "data/pricing/current_pricing.json"

    Returns:
        bool: True if validation passes, False otherwise
    """
    if pricing_file is None:
        pricing_file = Path("data/pricing/current_pricing.json")
    elif isinstance(pricing_file, str):
        pricing_file = Path(pricing_file)

    if not pricing_file.exists():
        logger.error(f"Pricing file not found: {pricing_file}")
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

            if input_price is not None and (input_price <= 0 or input_price > 1000):
                logger.warning(f"Suspicious input price for {model_key}: ${input_price}")

            if output_price is not None and (output_price <= 0 or output_price > 1000):
                logger.warning(f"Suspicious output price for {model_key}: ${output_price}")

    logger.info("Pricing data validation passed")
    return True


def main() -> None:
    """Main entry point for CLI usage"""
    if len(sys.argv) > 1:
        pricing_file = Path(sys.argv[1])
        result = validate_pricing_data(pricing_file)
    else:
        result = validate_pricing_data()

    if not result:
        sys.exit(1)


if __name__ == "__main__":
    main()
