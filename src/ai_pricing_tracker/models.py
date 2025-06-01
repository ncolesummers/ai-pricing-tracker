"""
Data models for AI pricing information.

This module defines the core data structures used to represent pricing
information for AI models across different providers.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Dict, Optional


@dataclass
class ModelPricing:
    """
    Pricing information for a single AI model.

    This class stores the pricing details for a specific AI model,
    including input and output token costs.

    Attributes:
        input_price: Price per 1 million input (prompt) tokens in the specified
            currency
        output_price: Price per 1 million output (completion) tokens in the specified
            currency
        currency: Currency code for the pricing (default: "USD")
        notes: Optional additional information about the model or pricing

    Examples:
        >>> model_pricing = ModelPricing(15.0, 75.0, "USD",
        ...     "Most powerful model")
        >>> cost = model_pricing.calculate_cost(1000, 500)
        >>> print(f"API call cost: ${cost:.4f}")
    """

    input_price: float  # Price per 1M input tokens
    output_price: float  # Price per 1M output tokens
    currency: str = "USD"
    notes: Optional[str] = None

    def calculate_cost(self, input_tokens: int, output_tokens: int) -> float:
        """
        Calculate cost for given token counts.

        Computes the total cost for an API call based on the number of
        input and output tokens used.

        Args:
            input_tokens: Number of input/prompt tokens
            output_tokens: Number of output/completion tokens

        Returns:
            Total cost in the model's currency, rounded to 6 decimal places

        Examples:
            >>> model = ModelPricing(15.0, 75.0)
            >>> cost = model.calculate_cost(1000, 500)
            >>> print(f"${cost:.6f}")  # $0.052500
        """
        input_cost = (input_tokens / 1_000_000) * self.input_price
        output_cost = (output_tokens / 1_000_000) * self.output_price
        return round(input_cost + output_cost, 6)

    def to_dict(self) -> dict:
        """
        Convert to dictionary representation.

        Creates a dictionary representation of the model pricing information,
        suitable for serialization to JSON.

        Returns:
            Dictionary with input price, output price, currency, and notes

        Examples:
            >>> model = ModelPricing(15.0, 75.0, notes="Premium model")
            >>> model_dict = model.to_dict()
            >>> print(model_dict)
            {'input': 15.0, 'output': 75.0, 'currency': 'USD',
            'notes': 'Premium model'}
        """
        return {
            "input": self.input_price,
            "output": self.output_price,
            "currency": self.currency,
            "notes": self.notes,
        }


@dataclass
class PricingData:
    """
    Container for all pricing data across providers and models.

    This class aggregates pricing information for multiple AI models
    across different providers, with metadata about when the pricing
    was last updated.

    Attributes:
        last_updated: Timestamp when the pricing data was last updated
        models: Dictionary mapping model identifiers to ModelPricing objects
        source_url: Optional URL where the pricing data was obtained from

    Notes:
        Model identifiers are typically in the format "provider/model-name",
        such as "anthropic/claude-opus-4" or "openai/gpt-4".
    """

    last_updated: datetime
    models: Dict[str, ModelPricing]
    source_url: Optional[str] = None

    @classmethod
    def from_dict(cls, data: dict) -> "PricingData":
        """
        Create PricingData from dictionary.

        Parses a dictionary (typically from JSON) into a PricingData object.
        The dictionary should have the following structure:
        {
            "last_updated": "2025-01-01T00:00:00Z",
            "source_url": "https://example.com/pricing",
            "pricing": {
                "provider/model-name": {
                    "input": 15.0,
                    "output": 75.0,
                    "currency": "USD",
                    "notes": "Optional notes"
                },
                ...
            }
        }

        Args:
            data: Dictionary containing pricing data

        Returns:
            Populated PricingData object

        Examples:
            >>> data = {
            ...     "last_updated": "2025-01-01T00:00:00Z",
            ...     "pricing": {
            ...         "openai/gpt-4": {"input": 30.0, "output": 60.0}
            ...     }
            ... }
            >>> pricing_data = PricingData.from_dict(data)
        """
        models = {}

        # Parse pricing data
        for key, value in data.get("pricing", {}).items():
            models[key] = ModelPricing(
                input_price=value.get("input", 0.0),
                output_price=value.get("output", 0.0),
                currency=value.get("currency", "USD"),
                notes=value.get("notes"),
            )

        # Parse timestamp
        last_updated_str = data.get("last_updated", datetime.utcnow().isoformat())
        if isinstance(last_updated_str, str):
            last_updated = datetime.fromisoformat(last_updated_str.replace("Z", "+00:00"))
        else:
            last_updated = last_updated_str

        return cls(
            last_updated=last_updated,
            models=models,
            source_url=data.get("source_url"),
        )

    def to_dict(self) -> dict:
        """
        Convert to dictionary representation.

        Creates a dictionary representation of all pricing data,
        suitable for serialization to JSON.

        Returns:
            Dictionary with last_updated timestamp, source_url, and all model pricing

        Examples:
            >>> pricing_data = PricingData(
            ...     datetime.fromisoformat("2025-01-01T00:00:00"),
            ...     {"openai/gpt-4": ModelPricing(30.0, 60.0)}
            ... )
            >>> data_dict = pricing_data.to_dict()
        """
        return {
            "last_updated": self.last_updated.isoformat(),
            "source_url": self.source_url,
            "pricing": {key: model.to_dict() for key, model in self.models.items()},
        }

    @classmethod
    def get_default(cls) -> "PricingData":
        """
        Get default pricing data as fallback.

        Creates a PricingData object with hardcoded default pricing
        for common models. This is used as a fallback when no other
        pricing data is available.

        Returns:
            PricingData object with default pricing for common models

        Notes:
            The default pricing may not reflect the most current rates.
            It's intended as a last resort when network and cache access fail.
        """
        return cls(
            last_updated=datetime.utcnow(),
            models={
                "anthropic/claude-opus-4": ModelPricing(15.0, 75.0),
                "anthropic/claude-sonnet-4": ModelPricing(3.0, 15.0),
                "anthropic/claude-haiku-3-5": ModelPricing(0.25, 1.25),
                "openai/gpt-4": ModelPricing(30.0, 60.0),
                "openai/gpt-4-turbo": ModelPricing(10.0, 30.0),
                "openai/gpt-3-5-turbo": ModelPricing(0.5, 1.5),
                "openai/gpt-4o": ModelPricing(5.0, 15.0),
                "openai/gpt-4o-mini": ModelPricing(0.15, 0.6),
            },
        )
