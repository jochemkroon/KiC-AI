# Nexar API Setup Guide for KiCad AI Assistant

## Quick Start - Free Tier Available!

Nexar API (formerly Octopart) provides comprehensive component pricing from multiple distributors in a single API call. **Much simpler than managing individual distributor APIs!**

### Free Tier: Welcome 1K Plan
- **1,000 API calls per month** - completely free
- Access to all major distributors (Digi-Key, Mouser, Farnell, Newark, Arrow, etc.)
- Multi-distributor pricing comparison in single request
- No credit card required for free tier

## Setup Steps

### 1. Create Nexar Account
1. Visit: https://portal.nexar.com
2. Sign up with your email
3. Verify your email (check spam folder if needed)
4. Log into the Nexar portal

### 2. Create Application
1. In Nexar portal, click "Create Application"
2. Choose application type: "Supply Chain" 
3. Give it a name like "KiCad AI Assistant"
4. Description: "Component pricing for PCB design"

### 3. Get API Token
1. After creating the app, you'll get an API token
2. Copy this token - you'll need it for the environment variable

### 4. Configure KiCad AI Assistant
Set the environment variable:
```bash
export NEXAR_TOKEN="your_token_here"
```

Or add to your shell profile (`~/.zshrc` for zsh):
```bash
echo 'export NEXAR_TOKEN="your_token_here"' >> ~/.zshrc
source ~/.zshrc
```

## Testing the Setup

Run the test script to verify everything works:
```bash
cd /Users/jochem/Project/KIC-AI
python test_octopart_setup.py
```

## What You Get

### Multi-Distributor Pricing
One API call returns pricing from:
- Digi-Key
- Mouser Electronics  
- Farnell/element14
- Newark
- Arrow Electronics
- Future Electronics
- And many more...

### Example Response
For a 10kΩ resistor query, you'll get:
```json
{
  "parts": [
    {
      "mpn": "CF14JT10K0",
      "manufacturer": "Stackpole Electronics Inc",
      "pricing": {
        "digikey": {"price": 0.10, "stock": 50000},
        "mouser": {"price": 0.09, "stock": 25000},
        "farnell": {"price": 0.11, "stock": 15000}
      },
      "best_price": {"distributor": "mouser", "price": 0.09}
    }
  ]
}
```

### KiCad Integration
The AI assistant can now:
- Find real component pricing for your BOM
- Compare prices across all distributors
- Suggest cost optimizations
- Find alternative parts with better pricing
- Calculate total BOM costs with real data

## No More Complex API Setup!

Unlike Digi-Key V4 API which requires:
- ❌ Client ID + Client Secret
- ❌ OAuth flow management  
- ❌ Sandbox vs Production URLs
- ❌ Complex authentication

Nexar API only needs:
- ✅ Single API token
- ✅ Simple GraphQL queries
- ✅ All distributors in one call
- ✅ Free tier with 1K calls/month

## API Limits & Costs

### Free Tier (Welcome 1K)
- 1,000 calls/month
- All distributor access
- Real-time pricing
- No credit card required

### Paid Tiers (if you need more)
- Contact Nexar for enterprise pricing
- Higher call limits available

## Demo Mode
Even without an API token, the MCP server works in demo mode with realistic pricing data, so you can test the integration immediately!

## Troubleshooting

### No Email Confirmation?
- Check spam/junk folder
- Try different email address
- Contact Nexar support if needed

### Token Not Working?
- Verify token is set correctly: `echo $NEXAR_TOKEN`
- Check token hasn't expired in portal
- Ensure no extra spaces in environment variable

### Rate Limiting?
- Free tier: 1,000 calls/month
- Check usage in Nexar portal
- Consider caching results for development

## Support
- Nexar Documentation: https://docs.nexar.com
- Support: support@nexar.com
- KiCad AI Assistant: Check GitHub issues
