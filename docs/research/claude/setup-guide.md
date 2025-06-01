# AI Pricing Auto-Update Setup Guide

## Quick Start (5 minutes)

### 1. Create Repository Structure
```bash
mkdir ai-metrics-framework
cd ai-metrics-framework
git init

# Create directories
mkdir -p .github/workflows scripts data/pricing

# Copy the workflow file
# Copy the YAML from the first artifact to:
# .github/workflows/update-ai-pricing.yml

# Copy the scraper script
# Copy the Python script to:
# scripts/scrape_pricing.py

# Copy validation script
# Copy to: scripts/validate_pricing.py
```

### 2. Set Repository Permissions
Go to your GitHub repository:
- Settings → Actions → General
- Under "Workflow permissions", select "Read and write permissions"
- Check "Allow GitHub Actions to create and approve pull requests"
- Save

### 3. Test Locally First
```bash
# Install dependencies
pip install beautifulsoup4 requests playwright pandas

# Install Playwright browsers
playwright install chromium

# Test the scraper
python scripts/scrape_pricing.py

# Check the output
cat data/pricing/current_pricing.json
```

### 4. Deploy to GitHub
```bash
git add .
git commit -m "Add AI pricing auto-update workflow"
git push origin main
```

### 5. Manual Test
- Go to Actions tab in your GitHub repository
- Click on "Update AI Pricing Data"
- Click "Run workflow" → "Run workflow"
- Watch it execute and check for green checkmark

## Integration with Your Metrics Framework

### Option 1: Direct GitHub URL Access
```python
from src.pricing.ai_pricing_manager import AIPricingManager

# Use raw GitHub content URL
pricing = AIPricingManager(
    github_url="https://raw.githubusercontent.com/YOUR_USERNAME/ai-metrics-framework/main/data/pricing/pricing_simple.json"
)

# Automatically fetches latest pricing
cost = pricing.calculate_cost("anthropic", "claude-opus-4", 
                            input_tokens=1000, output_tokens=500)
```

### Option 2: Git Submodule (Recommended for larger projects)
```bash
# In your main project
git submodule add https://github.com/YOUR_USERNAME/ai-metrics-framework.git pricing-data
git submodule update --init --remote
```

### Option 3: Python Package Installation
```bash
# Install directly from GitHub
pip install git+https://github.com/YOUR_USERNAME/ai-metrics-framework.git
```

## Monitoring & Alerts

### Email Notifications on Pricing Changes
Add to your workflow:
```yaml
- name: Check for significant price changes
  run: |
    python scripts/check_price_changes.py
    
- name: Send notification if prices changed
  if: steps.check.outputs.changed == 'true'
  uses: dawidd6/action-send-mail@v3
  with:
    server_address: smtp.gmail.com
    username: ${{ secrets.EMAIL_USERNAME }}
    password: ${{ secrets.EMAIL_PASSWORD }}
    subject: AI Pricing Update Alert
    body: Pricing has changed! Check the latest updates.
    to: your-email@example.com
```

### Slack Integration
```yaml
- name: Notify Slack on pricing update
  if: steps.check.outputs.changed == 'true'
  uses: 8398a7/action-slack@v3
  with:
    status: ${{ job.status }}
    text: 'AI Pricing Updated! Check latest changes.'
    webhook_url: ${{ secrets.SLACK_WEBHOOK }}
```

## Advanced Features

### 1. Historical Pricing Analysis
The git-based approach automatically maintains pricing history. Analyze trends:

```python
import subprocess
import json
from datetime import datetime

def get_pricing_history(model_key):
    """Get historical pricing for a model using git history"""
    cmd = ["git", "log", "--pretty=format:%H %ai", "--", "data/pricing/current_pricing.json"]
    commits = subprocess.check_output(cmd).decode().strip().split('\n')
    
    history = []
    for commit_line in commits:
        commit_hash = commit_line.split()[0]
        timestamp = ' '.join(commit_line.split()[1:3])
        
        # Get file content at that commit
        cmd = ["git", "show", f"{commit_hash}:data/pricing/current_pricing.json"]
        try:
            content = subprocess.check_output(cmd).decode()
            data = json.loads(content)
            # Extract pricing for specific model
            # ... parsing logic ...
            history.append({
                "date": timestamp,
                "pricing": extracted_pricing
            })
        except:
            continue
    
    return history
```

### 2. Multi-Provider Support
Easily extend to more providers:

```python
def scrape_google_vertex_pricing(self) -> Dict[str, Any]:
    """Add Google Vertex AI pricing"""
    # Similar structure to existing scrapers
    pass

def scrape_aws_bedrock_pricing(self) -> Dict[str, Any]:
    """Add AWS Bedrock pricing"""
    pass
```

### 3. API Endpoint
Serve pricing data via a simple API:

```python
# api_server.py
from flask import Flask, jsonify
import json

app = Flask(__name__)

@app.route('/pricing/<provider>/<model>')
def get_pricing(provider, model):
    with open('data/pricing/pricing_simple.json') as f:
        data = json.load(f)
    
    key = f"{provider}/{model}"
    if key in data['pricing']:
        return jsonify(data['pricing'][key])
    return jsonify({"error": "Model not found"}), 404

@app.route('/pricing/all')
def get_all_pricing():
    with open('data/pricing/current_pricing.json') as f:
        return jsonify(json.load(f))
```

## Troubleshooting

### Common Issues

1. **Scraping fails with timeout**
   - Increase timeout in Playwright: `page.goto(url, timeout=30000)`
   - Check if sites have anti-bot protection

2. **Pricing not updating**
   - Check GitHub Actions logs
   - Verify repository write permissions
   - Ensure workflow file is in correct location

3. **Wrong pricing extracted**
   - Update CSS selectors in scraper
   - Add more fallback patterns
   - Consider using different scraping approach (API if available)

### Debugging Commands
```bash
# Check workflow runs
gh run list --workflow=update-ai-pricing.yml

# View specific run logs
gh run view <run-id>

# Test scraper with verbose logging
python scripts/scrape_pricing.py --verbose

# Validate data structure
python scripts/validate_pricing.py
```

## Best Practices

1. **Version Control**: Tag releases when pricing structure changes
   ```bash
   git tag -a v1.0.0 -m "Initial pricing structure"
   git push origin v1.0.0
   ```

2. **Data Validation**: Always validate scraped data before committing
   - Check for reasonable price ranges
   - Ensure all required models are present
   - Compare with previous values for anomalies

3. **Caching Strategy**: 
   - Cache pricing data for 24 hours in production
   - Force refresh on deployment
   - Provide manual refresh option

4. **Error Handling**:
   - Always include fallback pricing
   - Log scraping errors but don't fail the workflow
   - Send alerts only for critical issues

## Security Considerations

1. **No API Keys in Code**: This approach doesn't require API keys
2. **Public Repository**: Pricing data is public information
3. **Rate Limiting**: GitHub Actions respects robots.txt
4. **Minimal Permissions**: Only needs repository write access

## Maintenance Schedule

- **Daily**: Automated scraping runs
- **Weekly**: Review logs for any issues
- **Monthly**: Update fallback pricing manually
- **Quarterly**: Review and update selectors if needed

## Cost Analysis

This solution is completely free:
- GitHub Actions: Free for public repositories
- Storage: Git storage is free
- Bandwidth: Minimal data transfer
- No API costs: Direct scraping instead of APIs

Compare to alternatives:
- Manual updates: 1-2 hours/month developer time
- Paid APIs: $50-200/month for pricing data
- Database hosting: $10-50/month

## Next Steps

1. Set up the basic workflow
2. Customize for your specific needs
3. Add monitoring and alerts
4. Integrate with your metrics framework
5. Consider contributing improvements back to the community

## Support & Contributions

Feel free to:
- Open issues for bugs or features
- Submit PRs with improvements
- Share your adaptations
- Star the repository if helpful

This approach gives you automated, version-controlled, free pricing updates that integrate seamlessly with your AI metrics framework!