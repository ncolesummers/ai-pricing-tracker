# AI Pricing Tracker - Quick Start Guide for Claude Code

## What You're Building

An automated AI pricing tracker that:
- Scrapes pricing daily from Anthropic/OpenAI websites
- Publishes as a PyPI package
- Provides easy cost calculations for AI developers
- Maintains historical pricing via git

## Files to Download

Download these files into your repository root:

1. **IMPLEMENTATION_PLAN.md** - Master plan with step-by-step instructions
2. **MODELS.md** - Python model classes (`models.py` and `exceptions.py`)
3. **TESTS.md** - Test files (`test_manager.py` and `test_scraper.py`)
4. **DEFAULT_PRICING.md** - Default pricing JSON data
5. **README_TEMPLATE.md** - README.md template
6. **PYPI_SETUP.md** - PyPI publishing guide and workflow
7. **PYPI_PACKAGE.md** - Package file references

## Artifacts to Reference

These artifacts contain the actual code:
- `ai-pricing-github-action` - GitHub Actions workflow
- `pricing-scraper-script` - Web scraping script
- `pricing-utilities` - Validation script
- `pricing-dashboard` - HTML dashboard

## Quick Command Sequence

```bash
# 1. Create repo and clone
git clone https://github.com/YOUR_USERNAME/ai-pricing-tracker.git
cd ai-pricing-tracker

# 2. Run this to create structure
mkdir -p .github/workflows src/ai_pricing_tracker/data scripts data/pricing tests docs
touch src/ai_pricing_tracker/__init__.py tests/__init__.py

# 3. Copy files as directed in IMPLEMENTATION_PLAN.md

# 4. Test locally
python -m venv venv
source venv/bin/activate
pip install -e ".[dev,scraper]"
python scripts/scrape_pricing.py

# 5. Push and test GitHub Action
git add -A
git commit -m "Initial implementation"
git push origin main

# 6. Go to Actions tab and run workflow manually
```

## Critical Replacements

Search and replace these in all files:
- `YOUR_USERNAME` → Your GitHub username
- `Your Name` → Your actual name  
- `your.email@example.com` → Your email
- Update the GitHub raw content URL in dashboard

## Success Checklist

- [ ] Repository created and permissions set
- [ ] All files copied from artifacts/documents
- [ ] Placeholders replaced
- [ ] Local scraper test successful
- [ ] GitHub Action runs successfully
- [ ] TestPyPI package installs correctly
- [ ] PyPI package published

## Need Help?

The IMPLEMENTATION_PLAN.md has detailed instructions for each step. Follow it section by section for best results.

## Time Estimate

- Initial setup: 30 minutes
- Testing and debugging: 30 minutes  
- PyPI publishing: 20 minutes
- Total: ~80 minutes for complete implementation