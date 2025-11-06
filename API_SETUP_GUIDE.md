# 🔑 API Keys Setup Guide

Complete guide to obtaining all API keys needed for the Financial GraphRAG system.

---

## Overview

The system requires API keys from various providers:

| Service | Purpose | Required? | Free Tier | Cost |
|---------|---------|-----------|-----------|------|
| **Neo4j** | Knowledge Graph Database | ✅ Required | ✅ Yes | Free (self-hosted) |
| **OpenAI** | AI Language Model | ✅ One of LLM | ❌ No | ~$0.01-0.03/query |
| **Anthropic** | AI Language Model | ✅ One of LLM | ❌ No | ~$0.01-0.02/query |
| **Finnhub** | Financial News & Data | ⚠️ Recommended | ✅ Yes | Free: 60 calls/min |
| **NewsAPI** | General News | ⚠️ Recommended | ✅ Yes | Free: 100 calls/day |
| **Reddit** | Social Sentiment | ⭕ Optional | ✅ Yes | Free |

---

## 1. Neo4j Database Setup

### Method 1: Neo4j Desktop (Recommended)

#### Step-by-Step Guide

1. **Download Neo4j Desktop**
   ```
   URL: https://neo4j.com/download/
   ```
   - Click "Download Neo4j Desktop"
   - Fill registration form (any email works)
   - Receive activation key via email

2. **Install Neo4j Desktop**
   - **Windows**: Run `.exe` installer
   - **macOS**: Open `.dmg`, drag to Applications
   - **Linux**: Extract and run

3. **Launch and Activate**
   - Open Neo4j Desktop
   - Enter activation key from email
   - Click "Activate"

4. **Create Database**
   - Click "New" → "Create Project"
   - Name: `Financial GraphRAG`
   - Click "Add" → "Local DBMS"
   - Database name: `financial-graph`
   - **Password**: Create a strong password (save it!)
   - Version: Select latest (5.x)
   - Click "Create"

5. **Start Database**
   - Click "Start" button
   - Wait for status: "Active" (green dot)
   - Click "Open" to verify

6. **Verify Installation**
   - Browser opens at: http://localhost:7474
   - Login with:
     - Username: `neo4j`
     - Password: (your password from step 4)

7. **Save Configuration**
   ```ini
   NEO4J_URI=bolt://localhost:7687
   NEO4J_USER=neo4j
   NEO4J_PASSWORD=your_password_here
   ```

### Method 2: Docker

```bash
# Create and start Neo4j container
docker run -d \
  --name neo4j-financial \
  -p 7474:7474 \
  -p 7687:7687 \
  -e NEO4J_AUTH=neo4j/YourSecurePassword123 \
  -v neo4j-data:/data \
  -v neo4j-logs:/logs \
  neo4j:latest

# Verify it's running
docker ps | grep neo4j

# Access Neo4j Browser
# Open: http://localhost:7474
```

**Configuration:**
```ini
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=YourSecurePassword123
```

---

## 2. OpenAI API Key (Option 1 for LLM)

### Prerequisites
- Credit/debit card for billing
- Email address
- Phone number for verification

### Step-by-Step Guide

1. **Create Account**
   ```
   URL: https://platform.openai.com/signup
   ```
   - Click "Sign up"
   - Enter email or use Google/Microsoft
   - Verify email
   - Complete profile

2. **Add Payment Method**
   - Go to: https://platform.openai.com/settings/organization/billing
   - Click "Add payment method"
   - Enter credit card details
   - **Recommended**: Set spending limit ($5-10 for testing)

3. **Create API Key**
   - Go to: https://platform.openai.com/api-keys
   - Click "+ Create new secret key"
   - Name: `Financial GraphRAG`
   - Permissions: "All" (or custom as needed)
   - Click "Create secret key"

4. **🚨 IMPORTANT: Copy Key Immediately**
   - Key format: `sk-proj-xxxxx...`
   - **You won't see it again!**
   - Click "Copy"
   - Save in password manager or secure note

5. **Test API Key**
   ```bash
   curl https://api.openai.com/v1/models \
     -H "Authorization: Bearer YOUR_API_KEY"
   ```
   Should return list of models if key is valid.

6. **Add to Configuration**
   ```ini
   LLM_PROVIDER=openai
   OPENAI_API_KEY=sk-proj-your-key-here
   OPENAI_MODEL=gpt-4
   ```

### Pricing (as of 2024)
- **GPT-4 Turbo**: ~$0.01 per 1K tokens input, ~$0.03 per 1K output
- **Typical query**: ~$0.02-0.05
- **Estimated monthly cost** (moderate use): $20-50

---

## 3. Anthropic Claude API Key (Option 2 for LLM)

### Step-by-Step Guide

1. **Create Account**
   ```
   URL: https://console.anthropic.com/
   ```
   - Click "Sign Up"
   - Enter email
   - Verify email
   - Complete registration

2. **Add Payment Method**
   - Go to: Settings → Billing
   - Click "Add payment method"
   - Enter credit card
   - **Recommended**: Set budget alert ($10-20)

3. **Create API Key**
   - Go to: Settings → API Keys
   - Click "Create Key"
   - Name: `Financial GraphRAG`
   - Click "Create"

4. **🚨 IMPORTANT: Copy Key Immediately**
   - Key format: `sk-ant-api03-xxxxx...`
   - Copy immediately (won't be shown again)
   - Save securely

5. **Test API Key**
   ```bash
   curl https://api.anthropic.com/v1/messages \
     -H "x-api-key: YOUR_API_KEY" \
     -H "anthropic-version: 2023-06-01" \
     -H "content-type: application/json" \
     -d '{"model":"claude-3-sonnet-20240229","max_tokens":100,"messages":[{"role":"user","content":"Hello"}]}'
   ```

6. **Add to Configuration**
   ```ini
   LLM_PROVIDER=anthropic
   ANTHROPIC_API_KEY=sk-ant-your-key-here
   ANTHROPIC_MODEL=claude-3-sonnet-20240229
   ```

### Pricing (as of 2024)
- **Claude 3 Sonnet**: ~$0.003 per 1K input, ~$0.015 per 1K output
- **Typical query**: ~$0.01-0.03
- **Estimated monthly cost** (moderate use): $15-40

---

## 4. Finnhub API Key (Recommended)

### Step-by-Step Guide

1. **Create Account**
   ```
   URL: https://finnhub.io/register
   ```
   - Enter email
   - Create password
   - Click "Register"

2. **Verify Email**
   - Check inbox for verification email
   - Click verification link

3. **Get API Key**
   - Login to: https://finnhub.io/dashboard
   - Your API key is displayed immediately
   - Key format: `c1a2b3c4d5e6...`
   - Click "Copy"

4. **Test API Key**
   ```bash
   curl "https://finnhub.io/api/v1/quote?symbol=AAPL&token=YOUR_API_KEY"
   ```
   Should return Apple stock data.

5. **Add to Configuration**
   ```ini
   FINNHUB_API_KEY=your-finnhub-key-here
   ```

### Rate Limits (Free Tier)
- **60 API calls per minute**
- **Recommended for**: Real-time stock data, company news
- **Upgrade**: $60/month for 300 calls/min

---

## 5. NewsAPI Key (Recommended)

### Step-by-Step Guide

1. **Create Account**
   ```
   URL: https://newsapi.org/register
   ```
   - Enter first name, email
   - Click "Submit"

2. **Verify Email**
   - Check inbox
   - Click verification link

3. **Get API Key**
   - Login to: https://newsapi.org/account
   - API key shown at top
   - Key format: `a1b2c3d4e5f6...`
   - Click to copy

4. **Test API Key**
   ```bash
   curl "https://newsapi.org/v2/top-headlines?country=us&category=business&apiKey=YOUR_API_KEY"
   ```
   Should return business headlines.

5. **Add to Configuration**
   ```ini
   NEWSAPI_KEY=your-newsapi-key-here
   ```

### Rate Limits (Free Tier)
- **100 requests per day**
- **Recommended for**: General market news, headlines
- **Upgrade**: $449/month for 250,000 requests

---

## 6. Reddit API (Optional)

### Step-by-Step Guide

1. **Create Reddit Account**
   ```
   URL: https://www.reddit.com/register
   ```
   (Skip if you already have one)

2. **Create Application**
   ```
   URL: https://www.reddit.com/prefs/apps
   ```
   - Scroll to bottom
   - Click "create another app..."

3. **Fill Application Form**
   - **Name**: `Financial GraphRAG`
   - **Type**: Select "script"
   - **Description**: `Financial sentiment analysis`
   - **About URL**: (leave blank)
   - **Redirect URI**: `http://localhost`
   - Click "create app"

4. **Get Credentials**
   - **Client ID**: Under app name (looks like: `abc123XYZ`)
   - **Client Secret**: Shown as "secret" (click to reveal)
   - Copy both values

5. **Test Credentials**
   ```python
   import praw
   reddit = praw.Reddit(
       client_id="YOUR_CLIENT_ID",
       client_secret="YOUR_CLIENT_SECRET",
       user_agent="FinancialGraphRAG/1.0"
   )
   print(reddit.read_only)  # Should print True
   ```

6. **Add to Configuration**
   ```ini
   REDDIT_CLIENT_ID=your-client-id-here
   REDDIT_CLIENT_SECRET=your-client-secret-here
   REDDIT_USER_AGENT=FinancialGraphRAG/1.0
   ```

### Rate Limits
- **60 requests per minute**
- **Free forever**
- **Recommended for**: Sentiment analysis from r/wallstreetbets, r/stocks

---

## Complete .env File Template

```ini
# =============================================================================
# Financial GraphRAG System Configuration
# =============================================================================

# -----------------------------------------------------------------------------
# Neo4j Database (REQUIRED)
# -----------------------------------------------------------------------------
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=your_neo4j_password_here

# -----------------------------------------------------------------------------
# LLM Provider (REQUIRED - Choose ONE)
# -----------------------------------------------------------------------------
LLM_PROVIDER=openai  # Options: openai, anthropic

# OpenAI Configuration (if LLM_PROVIDER=openai)
OPENAI_API_KEY=sk-proj-your-openai-key-here
OPENAI_MODEL=gpt-4

# Anthropic Configuration (if LLM_PROVIDER=anthropic)
ANTHROPIC_API_KEY=sk-ant-your-anthropic-key-here
ANTHROPIC_MODEL=claude-3-sonnet-20240229

# -----------------------------------------------------------------------------
# Financial Data APIs (RECOMMENDED)
# -----------------------------------------------------------------------------
FINNHUB_API_KEY=your-finnhub-key-here
NEWSAPI_KEY=your-newsapi-key-here

# -----------------------------------------------------------------------------
# Social Media APIs (OPTIONAL)
# -----------------------------------------------------------------------------
REDDIT_CLIENT_ID=your-reddit-client-id
REDDIT_CLIENT_SECRET=your-reddit-client-secret
REDDIT_USER_AGENT=FinancialGraphRAG/1.0

# -----------------------------------------------------------------------------
# Application Settings
# -----------------------------------------------------------------------------
LOG_LEVEL=INFO
DATA_REFRESH_INTERVAL=300  # seconds
MAX_COMPANIES=100
ENABLE_SENTIMENT_ANALYSIS=true
```

---

## Security Best Practices

### 1. Protect Your API Keys

❌ **Never Do This:**
- Commit `.env` file to Git
- Share keys in screenshots
- Store in plaintext files
- Email or message keys

✅ **Always Do This:**
- Use environment variables
- Store in password manager
- Add `.env` to `.gitignore`
- Rotate keys regularly

### 2. Set Spending Limits

For OpenAI and Anthropic:
1. Go to billing settings
2. Set monthly budget ($10-50 recommended)
3. Enable usage alerts
4. Review usage weekly

### 3. Monitor Usage

```bash
# Check OpenAI usage
https://platform.openai.com/usage

# Check Anthropic usage
https://console.anthropic.com/settings/billing

# Check Finnhub usage
https://finnhub.io/dashboard

# Check NewsAPI usage
https://newsapi.org/account
```

### 4. Regenerate Compromised Keys

If a key is exposed:
1. Immediately delete old key
2. Create new key
3. Update .env file
4. Restart application

---

## Cost Estimation

### Minimal Setup (Testing)
- Neo4j: **Free** (self-hosted)
- LLM: **~$5-10/month**
- Finnhub: **Free**
- NewsAPI: **Free**
- **Total: $5-10/month**

### Production Setup
- Neo4j: **Free-$50/month** (self-hosted or cloud)
- LLM: **$30-100/month**
- Finnhub Pro: **$60/month**
- NewsAPI Pro: **$449/month** (optional)
- **Total: $90-600+/month**

---

## Troubleshooting

### "Invalid API Key" Error

1. **Check key format**
   - OpenAI: Starts with `sk-proj-`
   - Anthropic: Starts with `sk-ant-api`
   - Finnhub: 16-char alphanumeric
   - NewsAPI: 32-char alphanumeric

2. **Check for extra spaces**
   ```ini
   # ❌ Wrong
   OPENAI_API_KEY= sk-proj-123...

   # ✅ Correct
   OPENAI_API_KEY=sk-proj-123...
   ```

3. **Verify on provider website**
   - Test key in provider's playground/dashboard

### "Rate Limit Exceeded"

**Solutions:**
1. Wait for rate limit reset
2. Reduce refresh frequency
3. Upgrade to paid tier
4. Use multiple API keys (rotate)

### "Connection Refused"

**Neo4j not responding:**
1. Verify Neo4j is running
2. Check firewall settings
3. Verify ports 7474, 7687 are open
4. Try: http://localhost:7474

---

## Next Steps

After setting up all API keys:

1. ✅ Update `.env` file with all keys
2. ✅ Verify `.env` in project root directory
3. ✅ Never commit `.env` to version control
4. ✅ Run: `python initialize_data.py`
5. ✅ Start application: `streamlit run src/ui/app.py`

**You're all set! 🎉**

---

## Quick Reference

| Service | Dashboard URL | Key Location |
|---------|--------------|--------------|
| OpenAI | https://platform.openai.com/api-keys | API Keys |
| Anthropic | https://console.anthropic.com/settings/keys | Settings → API Keys |
| Finnhub | https://finnhub.io/dashboard | Main Dashboard |
| NewsAPI | https://newsapi.org/account | Account Page |
| Reddit | https://www.reddit.com/prefs/apps | Preferences → Apps |
| Neo4j | http://localhost:7474 | Local Instance |

---

**Need help?** Check [INSTALLATION_GUIDE.md](INSTALLATION_GUIDE.md) or [QUICKSTART.md](QUICKSTART.md)
