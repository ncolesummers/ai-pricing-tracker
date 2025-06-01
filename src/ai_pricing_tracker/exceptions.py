"""
Custom exceptions for AI Pricing Tracker.

This module defines the exception hierarchy used by the AI Pricing Tracker
package to handle various error conditions in a structured way.
"""


class PricingError(Exception):
    """
    Base exception for all pricing-related errors.
    
    This is the parent class for all exceptions raised by the AI Pricing Tracker
    package. Catching this exception will catch all pricing-related errors.
    
    Examples:
        >>> try:
        ...     pricing_manager.get_model_pricing("unknown", "model")
        ... except PricingError as e:
        ...     print(f"Pricing error: {e}")
    """

    pass


class PricingNotFoundError(PricingError):
    """
    Raised when pricing for a specific model is not found.
    
    This exception is raised when attempting to retrieve pricing information
    for a model that doesn't exist in the pricing data.
    
    Examples:
        >>> try:
        ...     pricing_manager.get_model_pricing("nonexistent", "model")
        ... except PricingNotFoundError as e:
        ...     print(f"Model not found: {e}")
        ...     # Fallback to a known model
        ...     pricing_manager.get_model_pricing("openai", "gpt-3-5-turbo")
    """

    pass


class PricingUpdateError(PricingError):
    """
    Raised when pricing update fails.
    
    This exception is raised when an attempt to update pricing data
    from the remote source fails (e.g., network issues, server errors).
    
    Examples:
        >>> try:
        ...     pricing_manager.load_pricing(force_update=True)
        ... except PricingUpdateError as e:
        ...     print(f"Failed to update pricing: {e}")
        ...     print("Using cached pricing data instead")
    """

    pass


class InvalidPricingDataError(PricingError):
    """
    Raised when pricing data is invalid or corrupted.
    
    This exception is raised when the pricing data format is invalid,
    corrupted, or otherwise cannot be parsed correctly.
    
    Examples:
        >>> try:
        ...     PricingData.from_dict(invalid_data)
        ... except InvalidPricingDataError as e:
        ...     print(f"Invalid pricing data: {e}")
        ...     # Fall back to default data
        ...     pricing_data = PricingData.get_default()
    """

    pass