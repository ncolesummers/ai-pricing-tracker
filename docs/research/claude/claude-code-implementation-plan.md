# AI Pricing Tracker - Implementation Plan for Claude Code

## Project Overview
Build an automated AI pricing tracker that scrapes pricing data daily via GitHub Actions and publishes as a PyPI package.

## Project Structure
```
ai-pricing-tracker/
├── .github/
│   └── workflows/
│       ├── update-pricing.yml      # Artifact: ai-pricing-github-action
│       └── publish.yml             # From PYPI_SETUP.md
├── src/
│   └── ai_pricing_tracker/
│       ├── __init__.py            # From PYPI_PACKAGE.md
│       ├── manager.py             # From PYPI_PACKAGE.md
│       ├── models.py              # New file (see MODELS.md)
│       ├── exceptions.py          # New file (see MODELS.md)
│       ├── cli.py                 # From PYPI_PACKAGE.md
│       └── data/
│           └── default_pricing.json
├── scripts/
│   ├── scrape_pricing.py         # Artifact: pricing-scraper-script
│   └── validate_pricing.py       # From pricing-utilities artifact
├── data/
│   └── pricing/
│       └── .gitkeep
├── tests/
│   ├── __init__.py
│   ├── test_manager.py
│   └── test_scraper.py
├── docs/
│   └── pricing-dashboard.html    # Artifact: pricing-dashboard
├── setup.py                       # From PYPI_PACKAGE.md
├── pyproject.toml                 # From PYPI_PACKAGE.md
├── README.md                      # See README_TEMPLATE.md
├── LICENSE                        # MIT License
├── MANIFEST.in
├── requirements.txt
├── requirements-dev.txt
└── .gitignore
```

## Implementation Steps

### Phase 1: Repository Setup (10 minutes)

1. **Create GitHub repository**
   - Name: `ai-pricing-tracker`
   - Description: "Auto-updating AI API pricing data for Python developers"
   - Public repository
   - Add MIT license

2. **Clone and initial setup**
   ```bash
   git clone https://github.com/YOUR_USERNAME/ai-pricing-tracker.git
   cd ai-pricing-tracker
   ```

3. **Create directory structure**
   ```bash
   mkdir -p .github/workflows src/ai_pricing_tracker/data scripts data/pricing tests docs
   touch src/ai_pricing_tracker/__init__.py tests/__init__.py
   ```

4. **Create .gitignore**
   ```
   __pycache__/
   *.py[cod]
   *$py.class
   *.so
   .Python
   build/
   develop-eggs/
   dist/
   downloads/
   eggs/
   .eggs/
   lib/
   lib64/
   parts/
   sdist/
   var/
   wheels/
   *.egg-info/
   .installed.cfg
   *.egg
   MANIFEST
   .env
   venv/
   ENV/
   .vscode/
   .idea/
   *.log
   .DS_Store
   .coverage
   htmlcov/
   .pytest_cache/
   .mypy_cache/
   ```

### Phase 2: Core Implementation (30 minutes)

1. **Copy GitHub Actions workflow**
   - Copy content from artifact `ai-pricing-github-action` to `.github/workflows/update-pricing.yml`
   - Update YOUR_USERNAME placeholder

2. **Copy scraping script**
   - Copy content from artifact `pricing-scraper-script` to `scripts/scrape_pricing.py`
   - Copy validation script from `pricing-utilities` artifact (first part) to `scripts/validate_pricing.py`

3. **Set up Python package files**
   - Copy package structure from `PYPI_PACKAGE.md` artifact:
     - `setup.py`
     - `pyproject.toml`
     - `src/ai_pricing_tracker/__init__.py`
     - `src/ai_pricing_tracker/manager.py`
     - `src/ai_pricing_tracker/cli.py`

4. **Create missing Python files**
   - Create `src/ai_pricing_tracker/models.py` from `MODELS.md`
   - Create `src/ai_pricing_tracker/exceptions.py` from `MODELS.md`

5. **Create requirements files**
   ```
   # requirements.txt
   requests>=2.28.0
   python-dateutil>=2.8.0
   
   # requirements-dev.txt
   -r requirements.txt
   pytest>=7.0
   black>=22.0
   flake8>=4.0
   mypy>=0.990
   build>=0.7.0
   twine>=4.0.0
   playwright>=1.30.0
   beautifulsoup4>=4.11.0
   ```

### Phase 3: Configuration (15 minutes)

1. **Create MANIFEST.in**
   ```
   include README.md
   include LICENSE
   include requirements.txt
   recursive-include src/ai_pricing_tracker/data *.json
   ```

2. **Set GitHub repository permissions**
   - Go to Settings → Actions → General
   - Select "Read and write permissions"
   - Save

3. **Create initial pricing data file**
   - Copy default pricing structure from `DEFAULT_PRICING.md` to `src/ai_pricing_tracker/data/default_pricing.json`

4. **Copy dashboard**
   - Copy content from artifact `pricing-dashboard` to `docs/pricing-dashboard.html`
   - Update GitHub URL placeholder

### Phase 4: Testing (20 minutes)

1. **Create test files**
   - Create `tests/test_manager.py` from `TESTS.md`
   - Create `tests/test_scraper.py` from `TESTS.md`

2. **Local testing**
   ```bash
   # Create virtual environment
   python -m venv venv
   source venv/bin/activate  # or venv\Scripts\activate on Windows
   
   # Install in development mode
   pip install -e ".[dev,scraper]"
   
   # Run tests
   pytest
   
   # Test scraper
   python scripts/scrape_pricing.py
   
   # Test CLI
   ai-pricing-update list
   ```

3. **Run GitHub Action manually**
   - Push code to GitHub
   - Go to Actions tab
   - Select "Update AI Pricing Data"
   - Click "Run workflow"

### Phase 5: PyPI Preparation (15 minutes)

1. **Create PyPI accounts**
   - Register at https://pypi.org
   - Register at https://test.pypi.org
   - Create API tokens for both

2. **Add GitHub secrets**
   - Go to repository Settings → Secrets
   - Add `PYPI_API_TOKEN` with your PyPI token
   - Add `TEST_PYPI_API_TOKEN` with your TestPyPI token

3. **Create publish workflow**
   - Copy publish workflow from `PYPI_SETUP.md` to `.github/workflows/publish.yml`

4. **Update README**
   - Use template from `README_TEMPLATE.md`
   - Update all placeholders with your information

### Phase 6: Initial Release (10 minutes)

1. **Test on TestPyPI**
   ```bash
   # Build
   python -m build
   
   # Upload to TestPyPI
   python -m twine upload --repository testpypi dist/*
   
   # Test installation
   pip install -i https://test.pypi.org/simple/ ai-pricing-tracker
   ```

2. **Create first release**
   ```bash
   git tag -a v0.1.0 -m "Initial release"
   git push origin v0.1.0
   ```

3. **Publish to PyPI**
   - Go to GitHub releases
   - Create new release from v0.1.0 tag
   - This triggers automatic PyPI publishing

## Important Notes for Claude Code

1. **Placeholder Updates Required**
   - Replace all instances of `YOUR_USERNAME` with actual GitHub username
   - Replace `your.email@example.com` with actual email
   - Replace `Your Name` with actual name

2. **Scraper Selectors**
   - The CSS selectors in `scrape_pricing.py` may need updates
   - Test scraping locally first before pushing

3. **API Tokens**
   - Never commit API tokens
   - Use GitHub secrets for all sensitive data

4. **Testing Order**
   1. Test scraper locally
   2. Test package installation locally
   3. Test on TestPyPI
   4. Then publish to real PyPI

## File Reference

Use these artifacts in order:
1. `ai-pricing-github-action` → `.github/workflows/update-pricing.yml`
2. `pricing-scraper-script` → `scripts/scrape_pricing.py`
3. `pricing-utilities` → `scripts/validate_pricing.py` (first section only)
4. `pypi-package-structure` → Multiple files (see PYPI_PACKAGE.md)
5. `pricing-dashboard` → `docs/pricing-dashboard.html`

Additional files needed (provided separately):
- `MODELS.md` - Python model classes
- `TESTS.md` - Test files
- `DEFAULT_PRICING.md` - Default pricing data
- `README_TEMPLATE.md` - README template
- `PYPI_SETUP.md` - PyPI publishing setup

## Success Criteria

- [ ] GitHub Action runs successfully
- [ ] Pricing data updates daily
- [ ] Package installs from TestPyPI
- [ ] All tests pass
- [ ] CLI commands work correctly
- [ ] Published to PyPI successfully