"""
AI Pricing Tracker
Auto-updating pricing data for AI APIs including OpenAI, Anthropic, and more.
"""

__version__ = "0.1.0"
__author__ = "Cole Summers"
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
