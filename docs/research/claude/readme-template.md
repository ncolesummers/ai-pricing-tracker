# README Template

## File: README.md

```markdown
# AI Pricing Tracker

[![PyPI version](https://badge.fury.io/py/ai-pricing-tracker.svg)](https://badge.fury.io/py/ai-pricing-tracker)
[![Python Versions](https://img.shields.io/pypi/pyversions/ai-pricing-tracker.svg)](https://pypi.org/project/ai-pricing-tracker/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![GitHub Actions](https://github.com/YOUR_USERNAME/ai-pricing-tracker/workflows/Update%20AI%20Pricing%20Data/badge.svg)](https://github.com/YOUR_USERNAME/ai-pricing-tracker/actions)

Auto-updating pricing data for AI/LLM APIs. Never hardcode prices again!

## Why This Package?

AI API pricing changes frequently, and keeping track of costs across multiple providers is challenging. This package:

- 🔄 **Auto-updates** daily via GitHub Actions
- 💰 **Current pricing** for OpenAI, Anthropic, Google, and more  
- 📊 **Historical tracking** via git history
- 🚀 **Zero configuration** required
- 🔒 **No API keys** needed for pricing data

## Installation

```bash
pip install ai-pricing-tracker
```

## Quick Start

```python
from ai_pricing_tracker import PricingManager

# Initialize (auto-downloads latest pricing)
pricing = PricingManager()

# Calculate costs
cost = pricing.calculate_cost(
    provider="anthropic",
    model="claude-opus-4",
    input_tokens=1000,
    output_tokens=500
)
print(f"Cost: ${cost:.4f}")
# Output: Cost: $0.0525

# Get pricing for specific model
input_price, output_price = pricing.get_model_pricing("openai", "gpt-4")
print(f"GPT-4: ${input_price}/1M input, ${output_price}/1M output")
# Output: GPT-4: $30.0/1M input, $60.0/1M output

# List all available models
models = pricing.list_models()
for model_key, model_pricing in models.items():
    print(f"{model_key}: ${model_pricing.input_price}/{model_pricing.output_price}")
```

## CLI Usage

The package includes a command-line interface:

```bash
# List all models
ai-pricing-update list

# Get specific model pricing
ai-pricing-update get anthropic claude-opus-4

# Calculate cost for specific token usage
ai-pricing-update calc openai gpt-4 1500 2000

# Force update pricing data
ai-pricing-update update
```

## Supported Providers

- **Anthropic**: Claude Opus 4, Claude Sonnet 4, Claude Haiku 3.5
- **OpenAI**: GPT-4, GPT-4 Turbo, GPT-3.5 Turbo, GPT-4o, GPT-4o mini
- **Google**: Gemini 1.5 Pro, Gemini 1.5 Flash
- More providers coming soon!

## Advanced Usage

### Custom Update URL

Use your own pricing data source:

```python
pricing = PricingManager(
    update_url="https://your-domain.com/pricing.json"
)
```

### Disable Auto-Updates

For environments where you want to control updates:

```python
pricing = PricingManager(auto_update=False)
```

### Get Pricing History

Since the data is tracked via git, you can analyze pricing trends:

```bash
# Clone the pricing data repository
git clone https://github.com/YOUR_USERNAME/ai-pricing-tracker.git
cd ai-pricing-tracker

# View price history for a specific model
git log -p --follow data/pricing/current_pricing.json | grep -A 2 -B 2 "claude-opus"
```

## Integration Examples

### With LangChain

```python
from ai_pricing_tracker import PricingManager
from langchain.llms import Anthropic
from langchain.callbacks import get_openai_callback

pricing = PricingManager()

# Track costs in your LangChain app
llm = Anthropic(model="claude-opus-4")
with get_openai_callback() as cb:
    result = llm("What is the meaning of life?")
    
    # Calculate actual cost
    cost = pricing.calculate_cost(
        "anthropic", 
        "claude-opus-4",
        cb.prompt_tokens,
        cb.completion_tokens
    )
    print(f"This query cost: ${cost:.4f}")
```

### Cost Tracking Decorator

```python
from ai_pricing_tracker import PricingManager
from functools import wraps

pricing = PricingManager()

def track_ai_costs(provider, model):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            result = func(*args, **kwargs)
            
            # Extract token usage from your API response
            input_tokens = result.get('usage', {}).get('input_tokens', 0)
            output_tokens = result.get('usage', {}).get('output_tokens', 0)
            
            cost = pricing.calculate_cost(provider, model, input_tokens, output_tokens)
            print(f"API call cost: ${cost:.4f}")
            
            return result
        return wrapper
    return decorator

@track_ai_costs("openai", "gpt-4")
def call_gpt4(prompt):
    # Your API call here
    pass
```

## Data Structure

The package uses a simple JSON structure that's easy to parse:

```json
{
  "last_updated": "2025-05-31T10:30:00Z",
  "pricing": {
    "anthropic/claude-opus-4": {
      "input": 15.0,
      "output": 75.0,
      "currency": "USD"
    },
    "openai/gpt-4": {
      "input": 30.0,
      "output": 60.0,
      "currency": "USD"
    }
  }
}
```

## Contributing

We welcome contributions! Areas where you can help:

- Add new AI providers
- Improve scraping reliability  
- Add cost optimization features
- Create integrations with popular frameworks

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## Development

```bash
# Clone the repository
git clone https://github.com/YOUR_USERNAME/ai-pricing-tracker.git
cd ai-pricing-tracker

# Install in development mode
pip install -e ".[dev]"

# Run tests
pytest

# Format code
black src tests

# Type checking
mypy src
```

## How It Works

1. **GitHub Actions** run daily to scrape pricing from official sources
2. **Data is committed** to the repository, creating a historical record
3. **Package fetches** latest data on first use
4. **Local caching** prevents unnecessary requests
5. **Fallback data** ensures the package always works

## License

MIT License - see [LICENSE](LICENSE) file for details.

## Acknowledgments

- Inspired by the need for accurate AI cost tracking across projects
- Thanks to all contributors and the open-source community

## Support

- 🐛 [Report bugs](https://github.com/YOUR_USERNAME/ai-pricing-tracker/issues)
- 💡 [Request features](https://github.com/YOUR_USERNAME/ai-pricing-tracker/issues)
- 📖 [Read documentation](https://github.com/YOUR_USERNAME/ai-pricing-tracker/wiki)
- ⭐ Star this repo if you find it useful!

---

Built with ❤️ for the AI development community
```

## Replacements Needed

1. Replace `YOUR_USERNAME` with your GitHub username throughout
2. Update badge URLs after first release
3. Add your contact information if desired
4. Customize the acknowledgments section