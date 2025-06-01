# PyPI Publishing Setup

## File: .github/workflows/publish.yml

```yaml
name: Publish to PyPI

on:
  release:
    types: [published]
  workflow_dispatch:
    inputs:
      test_pypi:
        description: 'Publish to TestPyPI instead of PyPI'
        required: false
        type: boolean
        default: false

jobs:
  build:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v4
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install build twine
    
    - name: Build package
      run: python -m build
    
    - name: Check package
      run: twine check dist/*
    
    - name: Upload artifacts
      uses: actions/upload-artifact@v4
      with:
        name: dist
        path: dist/

  publish-testpypi:
    needs: build
    runs-on: ubuntu-latest
    if: github.event_name == 'workflow_dispatch' && github.event.inputs.test_pypi == 'true'
    
    steps:
    - name: Download artifacts
      uses: actions/download-artifact@v4
      with:
        name: dist
        path: dist/
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'
    
    - name: Install twine
      run: pip install twine
    
    - name: Publish to TestPyPI
      env:
        TWINE_USERNAME: __token__
        TWINE_PASSWORD: ${{ secrets.TEST_PYPI_API_TOKEN }}
      run: |
        twine upload --repository testpypi dist/*
        echo "Package published to TestPyPI!"
        echo "Install with: pip install -i https://test.pypi.org/simple/ ai-pricing-tracker"

  publish-pypi:
    needs: build
    runs-on: ubuntu-latest
    if: github.event_name == 'release'
    
    steps:
    - name: Download artifacts
      uses: actions/download-artifact@v4
      with:
        name: dist
        path: dist/
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'
    
    - name: Install twine
      run: pip install twine
    
    - name: Publish to PyPI
      env:
        TWINE_USERNAME: __token__
        TWINE_PASSWORD: ${{ secrets.PYPI_API_TOKEN }}
      run: |
        twine upload dist/*
        echo "Package published to PyPI!"
        echo "Install with: pip install ai-pricing-tracker"
```

## PyPI Account Setup Instructions

### 1. Create PyPI Accounts

1. **Production PyPI**
   - Go to https://pypi.org/account/register/
   - Create account with strong password
   - Enable 2FA (highly recommended)

2. **Test PyPI**
   - Go to https://test.pypi.org/account/register/
   - Can use same credentials as PyPI
   - Enable 2FA

### 2. Generate API Tokens

1. **PyPI Token** (for production releases)
   - Log in to https://pypi.org
   - Go to Account Settings → API tokens
   - Click "Add API token"
   - Name: `ai-pricing-tracker-github`
   - Scope: "Project: ai-pricing-tracker" (after first manual upload)
   - Copy token immediately (shown only once)

2. **TestPyPI Token** (for testing)
   - Log in to https://test.pypi.org
   - Same process as above
   - Name: `ai-pricing-tracker-test`

### 3. Add Tokens to GitHub Secrets

1. Go to your repository on GitHub
2. Settings → Secrets and variables → Actions
3. Click "New repository secret"
4. Add two secrets:
   - Name: `PYPI_API_TOKEN`, Value: (your PyPI token)
   - Name: `TEST_PYPI_API_TOKEN`, Value: (your TestPyPI token)

## Manual Publishing Process

### First Time Setup

```bash
# Install tools
pip install build twine

# Create .pypirc file (optional, for local publishing)
cat > ~/.pypirc << EOF
[distutils]
index-servers =
    pypi
    testpypi

[pypi]
username = __token__
password = pypi-XXXX...

[testpypi]
username = __token__
password = pypi-XXXX...
EOF

# Secure the file
chmod 600 ~/.pypirc
```

### Build Package

```bash
# Clean previous builds
rm -rf dist/ build/ *.egg-info

# Build source distribution and wheel
python -m build

# Check the package
twine check dist/*
```

### Test on TestPyPI

```bash
# Upload to TestPyPI
twine upload --repository testpypi dist/*

# Test installation
pip install -i https://test.pypi.org/simple/ ai-pricing-tracker

# Test the package
python -c "from ai_pricing_tracker import PricingManager; print(PricingManager())"
```

### Publish to PyPI

```bash
# Upload to PyPI
twine upload dist/*

# Verify installation
pip install ai-pricing-tracker
```

## Version Management

### Bumping Versions

1. Update version in `setup.py`
2. Update version in `pyproject.toml`
3. Update version in `src/ai_pricing_tracker/__init__.py`
4. Update CHANGELOG.md

### Creating a Release

```bash
# Commit version changes
git add -A
git commit -m "Bump version to 0.2.0"

# Create and push tag
git tag -a v0.2.0 -m "Release version 0.2.0"
git push origin main
git push origin v0.2.0

# Create GitHub release
# Go to GitHub → Releases → Draft a new release
# Choose the tag you just created
# This triggers the publish workflow
```

## Troubleshooting

### Common Issues

1. **"Invalid or non-existent authentication"**
   - Check API token is correct
   - Ensure using `__token__` as username
   - Token might be scoped to wrong project

2. **"Package already exists"**
   - Version already published (bump version)
   - Package name taken (use different name)

3. **TestPyPI installation fails**
   - Dependencies might not exist on TestPyPI
   - Use: `pip install -i https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple/ ai-pricing-tracker`

### Pre-release Testing

```bash
# Install in development mode
pip install -e .

# Run tests
pytest

# Test CLI
ai-pricing-update --help

# Test imports
python -c "import ai_pricing_tracker; print(ai_pricing_tracker.__version__)"
```

## Release Checklist

- [ ] All tests passing
- [ ] Version bumped appropriately
- [ ] CHANGELOG.md updated
- [ ] Documentation updated
- [ ] Tested on TestPyPI
- [ ] Git tag created
- [ ] GitHub release created
- [ ] Announcement prepared