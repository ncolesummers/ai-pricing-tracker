"""Tests for pricing data validation."""

import json
import logging
from pathlib import Path
from typing import Any, Dict, TypedDict, List


# Define type hints for pricing data structure
class ModelData(TypedDict, total=False):
    input_price_per_1m_tokens: float
    output_price_per_1m_tokens: float
    currency: str


class ProviderData(TypedDict):
    provider: str
    models: Dict[str, ModelData]


class PricingData(TypedDict):
    last_updated: str
    providers: List[ProviderData]


# Standard imports
import pytest
from unittest.mock import patch, MagicMock

# Import directly from the package
from ai_pricing_tracker.scripts.validate_pricing import validate_pricing_data


@pytest.fixture
def valid_pricing_data() -> PricingData:
    """Load valid pricing data fixture."""
    fixture_path = Path(__file__).parent.parent / "fixtures" / "data" / "valid_pricing.json"
    with open(fixture_path, "r", encoding="utf-8") as f:
        # Cast the loaded JSON to the appropriate type
        loaded_data = json.load(f)
        return loaded_data  # type: ignore


@pytest.fixture
def invalid_pricing_data() -> Dict[str, Any]:  # Use Any for invalid data
    """Load invalid pricing data fixture."""
    fixture_path = Path(__file__).parent.parent / "fixtures" / "data" / "invalid_pricing.json"
    with open(fixture_path, "r", encoding="utf-8") as f:
        result: Dict[str, Any] = json.load(f)
        return result


@pytest.fixture
def edge_case_pricing_data() -> Dict[str, Any]:  # Use Any for edge cases
    """Load edge case pricing data fixture."""
    fixture_path = Path(__file__).parent.parent / "fixtures" / "data" / "edge_case_pricing.json"
    with open(fixture_path, "r", encoding="utf-8") as f:
        result: Dict[str, Any] = json.load(f)
        return result


class TestPricingValidation:
    """Test cases for pricing data validation."""

    def test_validate_complete_valid_data(
        self, valid_pricing_data: PricingData, tmp_path: Path
    ) -> None:
        """Test validation with completely valid data."""
        # Create a temporary pricing file
        data_file = tmp_path / "current_pricing.json"
        with open(data_file, "w") as f:
            json.dump(valid_pricing_data, f)

        # Run validation with our test file
        result = validate_pricing_data(data_file)
        assert result is True

    def test_validate_missing_required_fields(
        self, invalid_pricing_data: Dict[str, Any], tmp_path: Path
    ) -> None:
        """Test validation with missing required fields."""
        # Create a temporary pricing file
        data_file = tmp_path / "current_pricing.json"
        with open(data_file, "w") as f:
            json.dump(invalid_pricing_data, f)

        # Run validation with our test file
        result = validate_pricing_data(data_file)
        assert result is False

    def test_validate_file_not_found(self) -> None:
        """Test validation when pricing file doesn't exist."""
        with patch("ai_pricing_tracker.scripts.validate_pricing.Path") as mock_path:
            mock_path.return_value = MagicMock()
            mock_path.return_value.exists.return_value = False

            # Run validation
            result = validate_pricing_data()
            assert result is False

    def test_validate_suspicious_prices(
        self,
        edge_case_pricing_data: Dict[str, Any],
        tmp_path: Path,
        caplog: pytest.LogCaptureFixture,
    ) -> None:
        """Test validation with suspicious price values."""
        # Create a temporary pricing file
        data_file = tmp_path / "current_pricing.json"
        with open(data_file, "w") as f:
            json.dump(edge_case_pricing_data, f)

        # Configure logging capture
        caplog.set_level(logging.WARNING)

        # Run validation
        result = validate_pricing_data(data_file)

        # Validation should pass but with warnings
        assert result is True

        # Check for warnings about suspicious prices
        log_text = caplog.text
        assert "Suspicious input price" in log_text
        assert "Suspicious output price" in log_text

    def test_validate_empty_models(self, tmp_path: Path) -> None:
        """Test validation with a provider having no models."""
        # Create data with empty models
        data = {
            "last_updated": "2024-05-01T12:00:00Z",
            "providers": [{"provider": "test-provider", "models": {}}],  # Empty models
        }

        # Create a temporary pricing file
        data_file = tmp_path / "current_pricing.json"
        with open(data_file, "w") as f:
            json.dump(data, f)

        # Run validation
        result = validate_pricing_data(data_file)
        assert result is False

    def test_validate_missing_models_field(self, tmp_path: Path) -> None:
        """Test validation with a provider missing the models field."""
        # Create data with missing models field
        data = {
            "last_updated": "2024-05-01T12:00:00Z",
            "providers": [
                {
                    "provider": "test-provider"
                    # Missing models field
                }
            ],
        }

        # Create a temporary pricing file
        data_file = tmp_path / "current_pricing.json"
        with open(data_file, "w") as f:
            json.dump(data, f)

        # Run validation
        result = validate_pricing_data(data_file)
        assert result is False

    def test_validate_invalid_json(self, tmp_path: Path) -> None:
        """Test validation with invalid JSON file."""
        # Create a temporary pricing file with invalid JSON
        data_file = tmp_path / "current_pricing.json"
        with open(data_file, "w") as f:
            f.write("This is not valid JSON")

        # Run validation
        with pytest.raises(json.JSONDecodeError):
            validate_pricing_data(data_file)

    @patch("ai_pricing_tracker.scripts.validate_pricing.logger")
    def test_validation_logging(
        self,
        mock_logger: MagicMock,
        valid_pricing_data: PricingData,
        tmp_path: Path,
    ) -> None:
        """Test that validation logs appropriate messages."""
        # Create a temporary pricing file
        data_file = tmp_path / "current_pricing.json"
        with open(data_file, "w") as f:
            json.dump(valid_pricing_data, f)

        # Call validation directly with our test file
        result = validate_pricing_data(data_file)
        assert result is True

        # Check for info log
        mock_logger.info.assert_called_with("Pricing data validation passed")

    def test_enhanced_validation_rules(self) -> None:
        """Test additional validation rules that could be implemented."""
        # This test demonstrates additional validation that could be added
        # to the validation script:

        # Example: Ensure currency is a valid ISO code
        def validate_currency(currency: str) -> bool:
            valid_currencies = ["USD", "EUR", "GBP", "JPY", "CAD", "AUD"]
            return currency in valid_currencies

        # Example: Ensure timestamp is in ISO format
        def validate_timestamp(timestamp: str) -> bool:
            try:
                from datetime import datetime

                # Simple date (YYYY-MM-DD) is valid ISO format
                if len(timestamp) == 10 and timestamp.count("-") == 2:
                    # This is valid ISO format
                    return True

                # Full datetime
                datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
                return True
            except (ValueError, TypeError):
                return False

        # Example: Validate model identifiers
        def validate_model_id(model_id: str) -> bool:
            return "-" in model_id and not any(c.isupper() for c in model_id)

        # Simple tests for the enhanced validation functions
        assert validate_currency("USD") is True
        assert validate_currency("XYZ") is False

        assert validate_timestamp("2024-05-01T12:00:00Z") is True
        # Date without time is also valid ISO format
        assert validate_timestamp("2024-05-01") is True

        assert validate_model_id("claude-opus-4") is True
        assert validate_model_id("ClaudeOpus4") is False
