# AI Pricing Tracker Scripts

This directory contains scripts for scraping and validating pricing data from AI providers.

## Usage

These scripts can be used in two ways:

1. **As command-line tools** (installed via pip):
   ```bash
   # Scrape pricing data
   ai-pricing-scrape
   
   # Validate pricing data
   ai-pricing-validate [path/to/pricing_file.json]
   ```

2. **As importable Python modules**:
   ```python
   from ai_pricing_tracker.scripts import AIPricingScraper, validate_pricing_data
   
   # Create a scraper and run it
   scraper = AIPricingScraper()
   scraper.run()
   
   # Validate pricing data
   validate_pricing_data("path/to/pricing_file.json")
   ```

## Scripts

### scrape_pricing.py

Scrapes pricing data from AI provider websites:

- Currently supports Anthropic and OpenAI
- Uses Playwright for web scraping
- Falls back to hardcoded values if scraping fails
- Saves data in multiple formats (current, timestamped, simplified)

### validate_pricing.py

Validates the structure and content of pricing data:

- Ensures all required fields are present
- Checks for empty model lists
- Validates price ranges for reasonableness
- Returns boolean success/failure value