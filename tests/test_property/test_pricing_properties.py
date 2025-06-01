"""Property-based tests for pricing calculations."""

import json
import pytest
from datetime import datetime
from pathlib import Path
from hypothesis import given, strategies as st, settings, HealthCheck
from hypothesis.control import assume

from ai_pricing_tracker import PricingManager, ModelPricing


@pytest.fixture
def temp_cache_dir(tmp_path: Path) -> Path:
    """Create a temporary cache directory."""
    cache_dir = tmp_path / "test_cache"
    cache_dir.mkdir()
    return cache_dir


class TestPricingCalculationProperties:
    """Property-based tests for pricing calculations."""

    @given(
        input_price=st.floats(min_value=0.01, max_value=1000),
        output_price=st.floats(min_value=0.01, max_value=1000),
        input_tokens=st.integers(min_value=1, max_value=1_000_000),
        output_tokens=st.integers(min_value=1, max_value=1_000_000),
    )
    def test_model_pricing_calculation(
        self,
        input_price: float,
        output_price: float,
        input_tokens: int,
        output_tokens: int,
    ) -> None:
        """Test that ModelPricing calculates costs correctly for various inputs."""
        # Create a model pricing object
        model = ModelPricing(input_price, output_price, "USD")

        # Calculate cost
        cost = model.calculate_cost(input_tokens, output_tokens)

        # Verify basic properties
        expected_cost = (input_tokens / 1_000_000 * input_price) + (
            output_tokens / 1_000_000 * output_price
        )
        expected_cost = round(expected_cost, 6)

        assert cost == expected_cost
        assert cost >= 0  # Cost should never be negative

    @settings(suppress_health_check=[HealthCheck.function_scoped_fixture])
    @given(
        input_price=st.floats(min_value=0.01, max_value=1000),
        output_price=st.floats(min_value=0.01, max_value=1000),
        input_tokens=st.integers(min_value=100, max_value=1_000_000),
        output_tokens=st.integers(min_value=100, max_value=1_000_000),
        multiplier=st.integers(min_value=2, max_value=10),
    )
    def test_scaling_property(
        self,
        input_price: float,
        output_price: float,
        input_tokens: int,
        output_tokens: int,
        multiplier: int,
        temp_cache_dir: Path,
    ) -> None:
        """Test that scaling token counts scales the cost proportionally."""
        # Create a pricing manager with a single model
        cache_file = temp_cache_dir / "pricing_cache.json"
        with open(cache_file, "w") as f:
            json.dump(
                {
                    "last_updated": datetime.utcnow().isoformat(),
                    "pricing": {
                        "test/model": {
                            "input": input_price,
                            "output": output_price,
                            "currency": "USD",
                        }
                    },
                },
                f,
            )

        manager = PricingManager(cache_dir=temp_cache_dir, auto_update=False)

        # Calculate costs for original and scaled token counts
        original_cost = manager.calculate_cost("test", "model", input_tokens, output_tokens)
        scaled_cost = manager.calculate_cost(
            "test",
            "model",
            input_tokens * multiplier,
            output_tokens * multiplier,
        )

        # Skip test if original cost is zero to avoid division by zero
        if original_cost == 0:
            return

        # Use a special case for the cost ratio to deal with floating point precision
        if scaled_cost < 1e-5 or original_cost < 1e-5:
            # For tiny values, check that they're close enough
            assert abs(scaled_cost - (original_cost * multiplier)) < 1e-9
        else:
            # For larger values, use a very relaxed relative tolerance
            assert pytest.approx(scaled_cost / original_cost, rel=1e-1) == multiplier

    @settings(suppress_health_check=[HealthCheck.function_scoped_fixture])
    @given(
        input_price=st.floats(min_value=0.01, max_value=1000),
        output_price=st.floats(min_value=0.01, max_value=1000),
        input_tokens_a=st.integers(min_value=100, max_value=500_000),
        output_tokens_a=st.integers(min_value=100, max_value=500_000),
        input_tokens_b=st.integers(min_value=100, max_value=500_000),
        output_tokens_b=st.integers(min_value=100, max_value=500_000),
    )
    def test_additivity_property(
        self,
        input_price: float,
        output_price: float,
        input_tokens_a: int,
        output_tokens_a: int,
        input_tokens_b: int,
        output_tokens_b: int,
        temp_cache_dir: Path,
    ) -> None:
        """Test that costs are additive (cost(A+B) = cost(A) + cost(B))."""
        # Create a pricing manager with a single model
        cache_file = temp_cache_dir / "pricing_cache.json"
        with open(cache_file, "w") as f:
            json.dump(
                {
                    "last_updated": datetime.utcnow().isoformat(),
                    "pricing": {
                        "test/model": {
                            "input": input_price,
                            "output": output_price,
                            "currency": "USD",
                        }
                    },
                },
                f,
            )

        manager = PricingManager(cache_dir=temp_cache_dir, auto_update=False)

        # Calculate costs
        cost_a = manager.calculate_cost("test", "model", input_tokens_a, output_tokens_a)
        cost_b = manager.calculate_cost("test", "model", input_tokens_b, output_tokens_b)
        combined_cost = manager.calculate_cost(
            "test",
            "model",
            input_tokens_a + input_tokens_b,
            output_tokens_a + output_tokens_b,
        )

        # Due to rounding in the PricingManager.calculate_cost() method (which rounds to 6 decimal places),
        # we need to manually calculate what we expect the costs to be, following the same logic.
        # This way we can properly account for rounding differences.

        # Calculate what the exact values should be without rounding
        input_cost_a = (input_tokens_a / 1_000_000) * input_price
        output_cost_a = (output_tokens_a / 1_000_000) * output_price

        input_cost_b = (input_tokens_b / 1_000_000) * input_price
        output_cost_b = (output_tokens_b / 1_000_000) * output_price

        # Calculate combined input/output costs (before rounding)
        combined_input_cost = ((input_tokens_a + input_tokens_b) / 1_000_000) * input_price
        combined_output_cost = ((output_tokens_a + output_tokens_b) / 1_000_000) * output_price

        # Round the sums as they would be rounded in the calculate_cost method
        expected_cost_a = round(input_cost_a + output_cost_a, 6)
        expected_cost_b = round(input_cost_b + output_cost_b, 6)
        expected_combined = round(combined_input_cost + combined_output_cost, 6)

        # Now we can verify that our manually calculated rounded values match what the function returns
        assert cost_a == expected_cost_a
        assert cost_b == expected_cost_b
        assert combined_cost == expected_combined

        # Due to the rounding and floating-point precision issues, the sum of individually rounded costs
        # might not exactly equal the rounded combined cost. Allow for slightly larger tolerance.
        assert abs(combined_cost - (expected_cost_a + expected_cost_b)) <= 2e-6

    @settings(suppress_health_check=[HealthCheck.function_scoped_fixture])
    @given(
        input_price=st.floats(min_value=0.01, max_value=1000),
        output_price=st.floats(min_value=0.01, max_value=1000),
    )
    def test_zero_tokens_property(
        self, input_price: float, output_price: float, temp_cache_dir: Path
    ) -> None:
        """Test that zero tokens results in zero cost."""
        # Create a pricing manager with a single model
        cache_file = temp_cache_dir / "pricing_cache.json"
        with open(cache_file, "w") as f:
            json.dump(
                {
                    "last_updated": datetime.utcnow().isoformat(),
                    "pricing": {
                        "test/model": {
                            "input": input_price,
                            "output": output_price,
                            "currency": "USD",
                        }
                    },
                },
                f,
            )

        manager = PricingManager(cache_dir=temp_cache_dir, auto_update=False)

        # Test zero tokens
        zero_input_cost = manager.calculate_cost("test", "model", 0, 100)
        zero_output_cost = manager.calculate_cost("test", "model", 100, 0)
        zero_both_cost = manager.calculate_cost("test", "model", 0, 0)

        # Expected costs
        expected_zero_input = (0 / 1_000_000 * input_price) + (100 / 1_000_000 * output_price)
        expected_zero_output = (100 / 1_000_000 * input_price) + (0 / 1_000_000 * output_price)

        # Check that the costs match expectations
        assert pytest.approx(zero_input_cost, rel=1e-5) == round(expected_zero_input, 6)
        assert pytest.approx(zero_output_cost, rel=1e-5) == round(expected_zero_output, 6)
        assert zero_both_cost == 0.0

    @settings(suppress_health_check=[HealthCheck.function_scoped_fixture])
    @given(
        model_name=st.text(
            min_size=1, max_size=20, alphabet="abcdefghijklmnopqrstuvwxyz0123456789"
        ),
        provider_name=st.text(
            min_size=1, max_size=20, alphabet="abcdefghijklmnopqrstuvwxyz0123456789"
        ),
        input_price=st.floats(min_value=0.01, max_value=1000),
        output_price=st.floats(min_value=0.01, max_value=1000),
        input_tokens=st.integers(min_value=1, max_value=1_000_000),
        output_tokens=st.integers(min_value=1, max_value=1_000_000),
    )
    def test_case_insensitivity(
        self,
        model_name: str,
        provider_name: str,
        input_price: float,
        output_price: float,
        input_tokens: int,
        output_tokens: int,
        temp_cache_dir: Path,
    ) -> None:
        """Test that model and provider names are case-insensitive."""
        assume(not any(c.isspace() for c in model_name))
        assume(not any(c.isspace() for c in provider_name))

        # Lowercase names for the cache file
        lower_provider = provider_name.lower()
        lower_model = model_name.lower()

        # Create a pricing manager with the model
        cache_file = temp_cache_dir / "pricing_cache.json"
        with open(cache_file, "w") as f:
            json.dump(
                {
                    "last_updated": datetime.utcnow().isoformat(),
                    "pricing": {
                        f"{lower_provider}/{lower_model}": {
                            "input": input_price,
                            "output": output_price,
                            "currency": "USD",
                        }
                    },
                },
                f,
            )

        manager = PricingManager(cache_dir=temp_cache_dir, auto_update=False)

        # Try different case combinations
        uppercase_provider = provider_name.upper()
        uppercase_model = model_name.upper()
        mixed_provider = provider_name.title()
        mixed_model = model_name.title()

        # Calculate costs with different case variations
        cost_lower = manager.calculate_cost(
            lower_provider, lower_model, input_tokens, output_tokens
        )
        cost_upper = manager.calculate_cost(
            uppercase_provider, uppercase_model, input_tokens, output_tokens
        )
        cost_mixed = manager.calculate_cost(
            mixed_provider, mixed_model, input_tokens, output_tokens
        )

        # All costs should be identical regardless of case
        assert cost_lower == cost_upper
        assert cost_lower == cost_mixed

    @settings(suppress_health_check=[HealthCheck.function_scoped_fixture])
    @given(
        input_price=st.floats(min_value=0.01, max_value=1000),
        output_price=st.floats(min_value=0.01, max_value=1000),
        tokens=st.integers(min_value=1, max_value=1_000_000),
    )
    def test_input_output_symmetry(
        self,
        input_price: float,
        output_price: float,
        tokens: int,
        temp_cache_dir: Path,
    ) -> None:
        """Test that swapping input/output prices and token counts produces expected results."""
        # Create a pricing manager with two models that have swapped prices
        cache_file = temp_cache_dir / "pricing_cache.json"
        with open(cache_file, "w") as f:
            json.dump(
                {
                    "last_updated": datetime.utcnow().isoformat(),
                    "pricing": {
                        "test/model-a": {
                            "input": input_price,
                            "output": output_price,
                            "currency": "USD",
                        },
                        "test/model-b": {
                            "input": output_price,  # Swapped
                            "output": input_price,  # Swapped
                            "currency": "USD",
                        },
                    },
                },
                f,
            )

        manager = PricingManager(cache_dir=temp_cache_dir, auto_update=False)

        # Calculate costs with swapped input/output tokens
        cost_a = manager.calculate_cost("test", "model-a", tokens, tokens)
        cost_b = manager.calculate_cost("test", "model-b", tokens, tokens)

        # For equal input and output tokens, costs should be equal
        assert pytest.approx(cost_a, rel=1e-5) == cost_b

        # Now test with different input/output token counts
        cost_a_input_heavy = manager.calculate_cost("test", "model-a", tokens * 2, tokens)
        cost_b_output_heavy = manager.calculate_cost("test", "model-b", tokens, tokens * 2)

        # These should be equal since we've swapped both prices and token counts
        assert pytest.approx(cost_a_input_heavy, rel=1e-5) == cost_b_output_heavy
