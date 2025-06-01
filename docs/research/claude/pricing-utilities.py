# scripts/validate_pricing.py
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


# ===== PRICING MANAGER CLASS FOR YOUR METRICS FRAMEWORK =====
# src/pricing/ai_pricing_manager.py
"""
AI Pricing Manager
Provides easy access to auto-updated AI API pricing data
"""

import json
from pathlib import Path
from typing import Dict, Optional, Tuple
from datetime import datetime
import requests
from functools import lru_cache

class AIPricingManager:
    """Manage AI API pricing data with automatic updates from GitHub"""
    
    def __init__(self, 
                 local_path: Path = Path("data/pricing/pricing_simple.json"),
                 github_url: Optional[str] = None):
        """
        Initialize pricing manager
        
        Args:
            local_path: Path to local pricing JSON file
            github_url: Optional URL to fetch latest pricing from GitHub
                       e.g., "https://raw.githubusercontent.com/USER/REPO/main/data/pricing/pricing_simple.json"
        """
        self.local_path = local_path
        self.github_url = github_url
        self._pricing_data = None
        self._last_loaded = None
        self.load_pricing()
    
    def load_pricing(self, force_reload: bool = False):
        """Load pricing data from file or GitHub"""
        # Try to fetch from GitHub first if URL provided
        if self.github_url and (force_reload or self._should_reload()):
            try:
                response = requests.get(self.github_url, timeout=5)
                if response.status_code == 200:
                    self._pricing_data = response.json()
                    self._last_loaded = datetime.utcnow()
                    # Cache locally
                    self.local_path.parent.mkdir(parents=True, exist_ok=True)
                    with open(self.local_path, 'w') as f:
                        json.dump(self._pricing_data, f, indent=2)
                    return
            except Exception as e:
                print(f"Failed to fetch pricing from GitHub: {e}")
        
        # Fall back to local file
        if self.local_path.exists():
            with open(self.local_path) as f:
                self._pricing_data = json.load(f)
                self._last_loaded = datetime.utcnow()
        else:
            # Use hardcoded defaults as last resort
            self._pricing_data = self._get_default_pricing()
    
    def _should_reload(self) -> bool:
        """Check if pricing data should be reloaded (older than 24 hours)"""
        if not self._last_loaded:
            return True
        age = datetime.utcnow() - self._last_loaded
        return age.total_seconds() > 86400  # 24 hours
    
    @lru_cache(maxsize=128)
    def get_model_pricing(self, provider: str, model: str) -> Tuple[float, float]:
        """
        Get input and output pricing for a specific model
        
        Args:
            provider: Provider name (e.g., "anthropic", "openai")
            model: Model identifier (e.g., "claude-opus-4", "gpt-4")
            
        Returns:
            Tuple of (input_price_per_1m_tokens, output_price_per_1m_tokens)
        """
        # Normalize inputs
        provider = provider.lower()
        model = model.lower()
        
        # Try different key formats
        keys_to_try = [
            f"{provider}/{model}",
            model,
            f"{provider}/{model.replace('_', '-')}",
            f"{provider}/{model.replace('-', '_')}"
        ]
        
        pricing = self._pricing_data.get("pricing", {})
        
        for key in keys_to_try:
            if key in pricing:
                model_data = pricing[key]
                return (
                    model_data.get("input", 0),
                    model_data.get("output", 0)
                )
        
        # Return zeros if not found
        return (0.0, 0.0)
    
    def calculate_cost(self, 
                      provider: str, 
                      model: str, 
                      input_tokens: int, 
                      output_tokens: int) -> float:
        """
        Calculate total cost for an API call
        
        Args:
            provider: Provider name
            model: Model identifier
            input_tokens: Number of input tokens
            output_tokens: Number of output tokens
            
        Returns:
            Total cost in USD
        """
        input_price, output_price = self.get_model_pricing(provider, model)
        
        # Prices are per 1M tokens
        input_cost = (input_tokens / 1_000_000) * input_price
        output_cost = (output_tokens / 1_000_000) * output_price
        
        return round(input_cost + output_cost, 6)
    
    def get_all_models(self) -> Dict[str, Dict[str, float]]:
        """Get all available model pricing"""
        return self._pricing_data.get("pricing", {})
    
    def get_last_updated(self) -> str:
        """Get timestamp of last pricing update"""
        return self._pricing_data.get("last_updated", "Unknown")
    
    def _get_default_pricing(self) -> Dict:
        """Hardcoded fallback pricing data"""
        return {
            "last_updated": datetime.utcnow().isoformat(),
            "pricing": {
                "anthropic/claude-opus-4": {"input": 15.0, "output": 75.0, "currency": "USD"},
                "anthropic/claude-sonnet-4": {"input": 3.0, "output": 15.0, "currency": "USD"},
                "anthropic/claude-haiku-3-5": {"input": 0.25, "output": 1.25, "currency": "USD"},
                "openai/gpt-4": {"input": 30.0, "output": 60.0, "currency": "USD"},
                "openai/gpt-4-turbo": {"input": 10.0, "output": 30.0, "currency": "USD"},
                "openai/gpt-3-5-turbo": {"input": 0.5, "output": 1.5, "currency": "USD"}
            }
        }


# ===== INTEGRATION WITH YOUR METRICS FRAMEWORK =====
# Example integration with the APIUsageTracker from your framework

class EnhancedAPIUsageTracker:
    """Enhanced version using auto-updated pricing"""
    
    def __init__(self, github_pricing_url: Optional[str] = None):
        self.usage_log = []
        self.pricing_manager = AIPricingManager(github_url=github_pricing_url)
    
    def track_api_call(self, model: str, provider: str = 'anthropic'):
        def decorator(func):
            def wrapper(*args, **kwargs):
                # ... existing tracking code ...
                
                # Get usage from response
                usage_data = self._extract_usage(response, provider)
                
                # Calculate cost using auto-updated pricing
                cost = self.pricing_manager.calculate_cost(
                    provider=provider,
                    model=model,
                    input_tokens=usage_data.get('input_tokens', 0),
                    output_tokens=usage_data.get('output_tokens', 0)
                )
                
                # Log the usage with calculated cost
                self._log_usage({
                    'timestamp': time.time(),
                    'model': model,
                    'provider': provider,
                    'input_tokens': usage_data.get('input_tokens', 0),
                    'output_tokens': usage_data.get('output_tokens', 0),
                    'total_cost': cost,
                    'pricing_last_updated': self.pricing_manager.get_last_updated()
                })
                
                return response
            return wrapper
        return decorator


# ===== USAGE EXAMPLE =====
if __name__ == "__main__":
    # Initialize with your GitHub repo URL
    pricing_mgr = AIPricingManager(
        github_url="https://raw.githubusercontent.com/YOUR_USERNAME/YOUR_REPO/main/data/pricing/pricing_simple.json"
    )
    
    # Get pricing for a model
    input_price, output_price = pricing_mgr.get_model_pricing("anthropic", "claude-opus-4")
    print(f"Claude Opus 4 - Input: ${input_price}/1M tokens, Output: ${output_price}/1M tokens")
    
    # Calculate cost for a specific usage
    cost = pricing_mgr.calculate_cost(
        provider="openai",
        model="gpt-4",
        input_tokens=1500,
        output_tokens=2000
    )
    print(f"Cost for 1.5k input + 2k output tokens: ${cost:.4f}")
    
    # Get all available models
    all_models = pricing_mgr.get_all_models()
    print(f"\nAvailable models: {len(all_models)}")
    for model, pricing in all_models.items():
        print(f"  {model}: ${pricing['input']}/{pricing['output']} per 1M tokens")