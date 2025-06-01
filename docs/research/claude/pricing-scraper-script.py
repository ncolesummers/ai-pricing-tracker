#!/usr/bin/env python3
"""
AI Pricing Scraper
Scrapes pricing data from Anthropic and OpenAI websites
Maintains historical pricing data with git versioning
"""

import json
import re
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any
import logging
from playwright.sync_api import sync_playwright
import time

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class AIPricingScraper:
    def __init__(self):
        self.data_dir = Path("data/pricing")
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.timestamp = datetime.utcnow().isoformat()
        
    def scrape_anthropic_pricing(self) -> Dict[str, Any]:
        """Scrape Anthropic's pricing page"""
        pricing_data = {
            "provider": "anthropic",
            "url": "https://www.anthropic.com/pricing",
            "last_updated": self.timestamp,
            "models": {}
        }
        
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            
            try:
                # Navigate to pricing page
                page.goto("https://www.anthropic.com/pricing", wait_until="networkidle")
                time.sleep(2)  # Allow dynamic content to load
                
                # Extract pricing data using selectors
                # Note: These selectors need to be updated if Anthropic changes their site
                pricing_sections = page.query_selector_all('[data-testid="pricing-card"], .pricing-card, [class*="pricing"]')
                
                for section in pricing_sections:
                    # Try multiple approaches to extract model info
                    model_name = None
                    input_price = None
                    output_price = None
                    
                    # Look for model name
                    name_elem = section.query_selector('h2, h3, [class*="model-name"], [class*="title"]')
                    if name_elem:
                        model_name = name_elem.inner_text().strip()
                    
                    # Look for pricing info
                    price_text = section.inner_text()
                    
                    # Extract prices using regex patterns
                    # Pattern for "$X per YM tokens" format
                    input_pattern = r'\$?([\d.]+)\s*(?:per|/)\s*(?:1M|million)\s*(?:input\s*)?tokens'
                    output_pattern = r'\$?([\d.]+)\s*(?:per|/)\s*(?:1M|million)\s*output\s*tokens'
                    
                    input_match = re.search(input_pattern, price_text, re.IGNORECASE)
                    output_match = re.search(output_pattern, price_text, re.IGNORECASE)
                    
                    if input_match:
                        input_price = float(input_match.group(1))
                    if output_match:
                        output_price = float(output_match.group(1))
                    
                    # If we found valid data, add it
                    if model_name and (input_price or output_price):
                        pricing_data["models"][self.normalize_model_name(model_name)] = {
                            "name": model_name,
                            "input_price_per_1m_tokens": input_price,
                            "output_price_per_1m_tokens": output_price,
                            "currency": "USD"
                        }
                
                # Also try to extract from script tags or JSON-LD
                scripts = page.query_selector_all('script')
                for script in scripts:
                    content = script.inner_html()
                    if 'pricing' in content.lower() or 'price' in content.lower():
                        # Try to extract JSON data
                        try:
                            # Look for JSON objects in script
                            json_matches = re.findall(r'\{[^{}]*"(?:price|cost|pricing)"[^{}]*\}', content)
                            for match in json_matches:
                                data = json.loads(match)
                                # Process extracted JSON pricing data
                                logger.info(f"Found pricing JSON: {data}")
                        except:
                            pass
                
            except Exception as e:
                logger.error(f"Error scraping Anthropic pricing: {e}")
                # Add fallback manual data (update these regularly)
                pricing_data["models"] = {
                    "claude-opus-4": {
                        "name": "Claude Opus 4",
                        "input_price_per_1m_tokens": 15.0,
                        "output_price_per_1m_tokens": 75.0,
                        "currency": "USD",
                        "note": "Fallback data - update manually"
                    },
                    "claude-sonnet-4": {
                        "name": "Claude Sonnet 4",
                        "input_price_per_1m_tokens": 3.0,
                        "output_price_per_1m_tokens": 15.0,
                        "currency": "USD",
                        "note": "Fallback data - update manually"
                    },
                    "claude-haiku-3-5": {
                        "name": "Claude Haiku 3.5",
                        "input_price_per_1m_tokens": 0.25,
                        "output_price_per_1m_tokens": 1.25,
                        "currency": "USD",
                        "note": "Fallback data - update manually"
                    }
                }
                pricing_data["scraping_error"] = str(e)
            finally:
                browser.close()
        
        return pricing_data
    
    def scrape_openai_pricing(self) -> Dict[str, Any]:
        """Scrape OpenAI's pricing page"""
        pricing_data = {
            "provider": "openai",
            "url": "https://openai.com/pricing",
            "last_updated": self.timestamp,
            "models": {}
        }
        
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            
            try:
                page.goto("https://openai.com/pricing", wait_until="networkidle")
                time.sleep(2)
                
                # Extract pricing tables
                tables = page.query_selector_all('table, [class*="pricing-table"], [class*="price-table"]')
                
                for table in tables:
                    rows = table.query_selector_all('tr')
                    
                    for row in rows:
                        cells = row.query_selector_all('td, th')
                        if len(cells) >= 3:  # Model, Input price, Output price
                            model_cell = cells[0].inner_text().strip()
                            
                            # Skip header rows
                            if 'model' in model_cell.lower() or 'input' in cells[1].inner_text().lower():
                                continue
                            
                            # Extract prices
                            input_price_text = cells[1].inner_text().strip()
                            output_price_text = cells[2].inner_text().strip()
                            
                            # Parse prices (handle various formats)
                            input_price = self.parse_price(input_price_text)
                            output_price = self.parse_price(output_price_text)
                            
                            if input_price is not None or output_price is not None:
                                pricing_data["models"][self.normalize_model_name(model_cell)] = {
                                    "name": model_cell,
                                    "input_price_per_1m_tokens": input_price,
                                    "output_price_per_1m_tokens": output_price,
                                    "currency": "USD"
                                }
                
            except Exception as e:
                logger.error(f"Error scraping OpenAI pricing: {e}")
                # Fallback data
                pricing_data["models"] = {
                    "gpt-4-turbo": {
                        "name": "GPT-4 Turbo",
                        "input_price_per_1m_tokens": 10.0,
                        "output_price_per_1m_tokens": 30.0,
                        "currency": "USD",
                        "note": "Fallback data - update manually"
                    },
                    "gpt-4": {
                        "name": "GPT-4",
                        "input_price_per_1m_tokens": 30.0,
                        "output_price_per_1m_tokens": 60.0,
                        "currency": "USD",
                        "note": "Fallback data - update manually"
                    },
                    "gpt-3-5-turbo": {
                        "name": "GPT-3.5 Turbo",
                        "input_price_per_1m_tokens": 0.5,
                        "output_price_per_1m_tokens": 1.5,
                        "currency": "USD",
                        "note": "Fallback data - update manually"
                    }
                }
                pricing_data["scraping_error"] = str(e)
            finally:
                browser.close()
        
        return pricing_data
    
    def parse_price(self, price_text: str) -> float:
        """Parse price from various text formats"""
        # Remove currency symbols and whitespace
        price_text = price_text.replace('$', '').replace(',', '').strip()
        
        # Handle "per 1M tokens" or "/ 1M tokens" format
        price_match = re.search(r'([\d.]+)\s*(?:per|/)\s*1M', price_text)
        if price_match:
            return float(price_match.group(1))
        
        # Handle simple numeric format
        simple_match = re.search(r'^([\d.]+)$', price_text)
        if simple_match:
            return float(simple_match.group(1))
        
        return None
    
    def normalize_model_name(self, name: str) -> str:
        """Normalize model names for consistent keys"""
        return name.lower().replace(' ', '-').replace('.', '-')
    
    def save_pricing_data(self, all_pricing: Dict[str, Any]):
        """Save pricing data to JSON files"""
        # Save current pricing
        current_file = self.data_dir / "current_pricing.json"
        with open(current_file, 'w') as f:
            json.dump(all_pricing, f, indent=2)
        
        # Save timestamped version
        timestamp_file = self.data_dir / f"pricing_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.json"
        with open(timestamp_file, 'w') as f:
            json.dump(all_pricing, f, indent=2)
        
        # Create simplified version for easy import
        simplified = self.create_simplified_pricing(all_pricing)
        simple_file = self.data_dir / "pricing_simple.json"
        with open(simple_file, 'w') as f:
            json.dump(simplified, f, indent=2)
        
        logger.info(f"Saved pricing data to {current_file}")
    
    def create_simplified_pricing(self, all_pricing: Dict[str, Any]) -> Dict[str, Any]:
        """Create a simplified pricing structure for easy use in code"""
        simplified = {
            "last_updated": self.timestamp,
            "pricing": {}
        }
        
        for provider_data in all_pricing["providers"]:
            provider = provider_data["provider"]
            for model_key, model_data in provider_data["models"].items():
                # Create a unified key like "anthropic/claude-opus-4"
                unified_key = f"{provider}/{model_key}"
                simplified["pricing"][unified_key] = {
                    "input": model_data.get("input_price_per_1m_tokens", 0),
                    "output": model_data.get("output_price_per_1m_tokens", 0),
                    "currency": model_data.get("currency", "USD")
                }
        
        return simplified
    
    def run(self):
        """Main execution method"""
        logger.info("Starting AI pricing scraper")
        
        # Scrape all providers
        anthropic_data = self.scrape_anthropic_pricing()
        openai_data = self.scrape_openai_pricing()
        
        # Combine all data
        all_pricing = {
            "last_updated": self.timestamp,
            "providers": [anthropic_data, openai_data]
        }
        
        # Save data
        self.save_pricing_data(all_pricing)
        
        logger.info("Pricing scraper completed successfully")

if __name__ == "__main__":
    scraper = AIPricingScraper()
    scraper.run()