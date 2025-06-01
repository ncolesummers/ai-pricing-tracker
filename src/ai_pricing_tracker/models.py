"""Data models for AI pricing information."""

from dataclasses import dataclass
from datetime import datetime
from typing import Dict, Optional


@dataclass
class ModelPricing:
    """Pricing information for a single AI model."""

    input_price: float  # Price per 1M input tokens
    output_price: float  # Price per 1M output tokens
    currency: str = "USD"
    notes: Optional[str] = None

    def calculate_cost(self, input_tokens: int, output_tokens: int) -> float:
        """Calculate cost for given token counts."""
        input_cost = (input_tokens / 1_000_000) * self.input_price
        output_cost = (output_tokens / 1_000_000) * self.output_price
        return round(input_cost + output_cost, 6)

    def to_dict(self) -> dict:
        """Convert to dictionary representation."""
        return {
            "input": self.input_price,
            "output": self.output_price,
            "currency": self.currency,
            "notes": self.notes,
        }


@dataclass
class PricingData:
    """Container for all pricing data."""

    last_updated: datetime
    models: Dict[str, ModelPricing]
    source_url: Optional[str] = None

    @classmethod
    def from_dict(cls, data: dict) -> "PricingData":
        """Create PricingData from dictionary."""
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

        return cls(last_updated=last_updated, models=models, source_url=data.get("source_url"))

    def to_dict(self) -> dict:
        """Convert to dictionary representation."""
        return {
            "last_updated": self.last_updated.isoformat(),
            "source_url": self.source_url,
            "pricing": {key: model.to_dict() for key, model in self.models.items()},
        }

    @classmethod
    def get_default(cls) -> "PricingData":
        """Get default pricing data as fallback."""
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
