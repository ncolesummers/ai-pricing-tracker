"""Custom exceptions for AI Pricing Tracker."""


class PricingError(Exception):
    """Base exception for pricing-related errors."""

    pass


class PricingNotFoundError(PricingError):
    """Raised when pricing for a specific model is not found."""

    pass


class PricingUpdateError(PricingError):
    """Raised when pricing update fails."""

    pass


class InvalidPricingDataError(PricingError):
    """Raised when pricing data is invalid or corrupted."""

    pass
