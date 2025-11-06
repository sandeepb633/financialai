# 📦 Complete Installation Guide

This guide will walk you through every step needed to install and run the Financial GraphRAG system.

## Table of Contents
1. [System Requirements](#system-requirements)
2. [Installing Python](#installing-python)
3. [Installing Neo4j](#installing-neo4j)
4. [Getting API Keys](#getting-api-keys)
5. [Installing the Application](#installing-the-application)
6. [Running the Application](#running-the-application)
7. [Verification](#verification)

---

## System Requirements

### Minimum Requirements
- **OS**: Windows 10/11, macOS 10.15+, or Linux
- **CPU**: 4 cores
- **RAM**: 16 GB
- **Storage**: 100 GB free space
- **Internet**: Broadband connection

### Recommended Requirements
- **CPU**: 8+ cores
- **RAM**: 32 GB
- **Storage**: 250 GB SSD
- **Internet**: High-speed connection

---

## Installing Python

### Windows

1. **Download Python 3.11**
   - Go to https://www.python.org/downloads/
   - Download Python 3.11.x (latest version)

2. **Run the Installer**
   - ✅ Check "Add Python to PATH"
   - Click "Install Now"
   - Wait for installation to complete

3. **Verify Installation**
   ```cmd
   python --version
   ```
   Should show: `Python 3.11.x`

### macOS

1. **Using Homebrew** (Recommended)
   ```bash
   brew install python@3.11
   ```

2. **Or Download from Python.org**
   - Go to https://www.python.org/downloads/
   - Download macOS installer
   - Run the .pkg file

3. **Verify Installation**
   ```bash
   python3 --version
   ```

### Linux (Ubuntu/Debian)

```bash
sudo apt update
sudo apt install python3.11 python3.11-venv python3-pip
```

---

## Installing Neo4j

### Option 1: Neo4j Desktop (Recommended for Beginners)

#### Windows & macOS

1. **Download Neo4j Desktop**
   - Go to https://neo4j.com/download/
   - Click "Download Neo4j Desktop"
   - Fill out the form (use any email)
   - Download the installer

2. **Install Neo4j Desktop**
   - **Windows**: Run the .exe file
   - **macOS**: Open the .dmg and drag to Applications

3. **Set Up Database**
   - Launch Neo4j Desktop
   - Click "New" → "Create Project"
   - Name your project (e.g., "Financial GraphRAG")
   - Click "Add" → "Local DBMS"
   - Set database name: `financial-graph`
   - Set password: `yourpassword` (remember this!)
   - Version: Select latest (5.x)
   - Click "Create"

4. **Start the Database**
   - Click "Start" on your database
   - Wait for status to show "Active"
   - Click "Open" to verify at http://localhost:7474

### Option 2: Docker (For Advanced Users)

#### All Platforms

1. **Install Docker**
   - Windows: Download from https://www.docker.com/products/docker-desktop
   - macOS: Download from https://www.docker.com/products/docker-desktop
   - Linux: `sudo apt install docker.io`

2. **Run Neo4j Container**
   ```bash
   docker run -d \
     --name neo4j-financial \
     -p 7474:7474 \
     -p 7687:7687 \
     -e NEO4J_AUTH=neo4j/yourpassword \
     -v neo4j-data:/data \
     neo4j:latest
   ```

3. **Verify Neo4j is Running**
   - Open browser: http://localhost:7474
   - Login: username=`neo4j`, password=`yourpassword`

---

## Getting API Keys

### 1. LLM API Key (REQUIRED - Choose ONE)

#### Option A: OpenAI GPT-4

1. **Create Account**
   - Go to https://platform.openai.com/signup
   - Sign up with email or Google

2. **Add Payment Method**
   - Go to Settings → Billing
   - Add credit card ($5-10 recommended to start)

3. **Create API Key**
   - Go to https://platform.openai.com/api-keys
   - Click "Create new secret key"
   - Name it: "Financial GraphRAG"
   - **IMPORTANT**: Copy the key immediately (you won't see it again!)
   - Save it somewhere safe

**Example key format**: `sk-proj-abc123...`

#### Option B: Anthropic Claude

1. **Create Account**
   - Go to https://console.anthropic.com/
   - Sign up with email

2. **Add Payment Method**
   - Go to Settings → Billing
   - Add credit card ($5-10 recommended)

3. **Create API Key**
   - Go to Settings → API Keys
   - Click "Create Key"
   - Name it: "Financial GraphRAG"
   - **Copy the key immediately!**

**Example key format**: `sk-ant-api03-abc123...`

### 2. Financial Data APIs (OPTIONAL but Recommended)

#### Finnhub API

1. Go to https://finnhub.io/register
2. Sign up (free tier available)
3. Verify email
4. Go to Dashboard
5. Copy your API key

**Example key format**: `c123abc...`

#### NewsAPI

1. Go to https://newsapi.org/register
2. Sign up (free tier: 100 requests/day)
3. Verify email
4. Copy your API key from dashboard

**Example key format**: `abc123def...`

#### Reddit API (Optional)

1. Go to https://www.reddit.com/prefs/apps
2. Scroll down, click "create another app"
3. Fill in:
   - Name: "Financial GraphRAG"
   - Type: "script"
   - Redirect URI: http://localhost
4. Click "create app"
5. Copy:
   - Client ID (under app name)
   - Client Secret (shown as "secret")

---

## Installing the Application

### 1. Download the Project

```bash
cd C:\Users\sande\downloads
cd financial-graphrag
```

### 2. Run Setup Script

```bash
python setup.py
```

This will:
- Install all Python dependencies
- Download language models
- Create configuration file

### 3. Configure Environment

Edit the `.env` file:

```bash
# Windows: Use Notepad
notepad .env

# macOS/Linux: Use any text editor
nano .env
```

**Fill in your information:**

```ini
# Neo4j Configuration
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=yourpassword  # ← Your Neo4j password

# LLM Configuration (Choose ONE)
LLM_PROVIDER=openai  # or anthropic

# If using OpenAI:
OPENAI_API_KEY=sk-proj-your-key-here  # ← Your OpenAI key
OPENAI_MODEL=gpt-4

# If using Anthropic:
ANTHROPIC_API_KEY=sk-ant-your-key-here  # ← Your Anthropic key
ANTHROPIC_MODEL=claude-3-sonnet-20240229

# Financial APIs (Optional)
FINNHUB_API_KEY=your-finnhub-key  # ← Your Finnhub key
NEWSAPI_KEY=your-newsapi-key       # ← Your NewsAPI key

# Reddit (Optional)
REDDIT_CLIENT_ID=your-client-id
REDDIT_CLIENT_SECRET=your-client-secret
REDDIT_USER_AGENT=FinancialGraphRAG/1.0
```

**Save and close the file**

### 4. Initialize Data

```bash
python initialize_data.py
```

This will:
- Connect to Neo4j
- Create graph schema
- Fetch initial market data
- Populate knowledge graph

**Expected time**: 5-10 minutes

---

## Running the Application

### Start the Application

```bash
streamlit run src/ui/app.py
```

**You should see:**
```
You can now view your Streamlit app in your browser.

Local URL: http://localhost:8501
Network URL: http://192.168.x.x:8501
```

### Access the Application

1. Open your web browser
2. Go to: **http://localhost:8501**
3. The Financial GraphRAG dashboard should load!

---

## Verification

### 1. Check System Status

In the sidebar, verify:
- ✅ **Neo4j Connected**
- ✅ **LLM Ready** (shows OpenAI or Anthropic)
- Metrics show numbers (Companies, News, Events)

### 2. Test AI Assistant

1. Click "💬 AI Assistant" in the sidebar
2. Ask: "What's the latest news about Apple?"
3. You should get a detailed, data-grounded response!

### 3. Check Market Dashboard

1. Click "📊 Market Dashboard"
2. Verify stock prices are showing
3. Check that companies are listed

### 4. View News Feed

1. Click "📰 News Feed"
2. Browse recent financial news articles
3. Filter by sentiment

---

## Troubleshooting Common Issues

### Issue: "Neo4j Disconnected"

**Solution 1**: Verify Neo4j is running
- Neo4j Desktop: Check database shows "Active"
- Docker: `docker ps` should show neo4j container
- Browser test: http://localhost:7474 should work

**Solution 2**: Check credentials
- Verify password in .env matches Neo4j password
- Try logging into http://localhost:7474 manually

**Solution 3**: Check ports
- Ensure nothing else uses ports 7474 and 7687
- Windows: Check Windows Firewall
- macOS: Check System Preferences → Security

### Issue: "LLM Not Initialized"

**Solution 1**: Verify API key
- Check key is in .env file
- Remove any extra spaces or quotes
- Verify key works on provider website

**Solution 2**: Check provider setting
```ini
LLM_PROVIDER=openai  # lowercase, no quotes
```

**Solution 3**: Test API key manually
```bash
# Test OpenAI
curl https://api.openai.com/v1/models \
  -H "Authorization: Bearer YOUR_API_KEY"

# Test Anthropic
curl https://api.anthropic.com/v1/messages \
  -H "x-api-key: YOUR_API_KEY"
```

### Issue: "Module not found" Errors

**Solution**: Reinstall dependencies
```bash
pip install -r requirements.txt --force-reinstall
python -m spacy download en_core_web_sm
```

### Issue: Data Not Loading

**Solution 1**: Refresh data manually
- Click "Settings" → "Refresh Now"
- Or run: `python initialize_data.py`

**Solution 2**: Check API keys
- Verify Finnhub and NewsAPI keys are valid
- Check API rate limits haven't been exceeded

**Solution 3**: Check logs
```bash
# View logs
cat logs/app.log  # Linux/macOS
type logs\app.log  # Windows
```

---

## Next Steps

Now that your system is running:

1. 📖 **Read**: [QUICKSTART.md](QUICKSTART.md) for usage tips
2. 💬 **Explore**: Try different questions in AI Assistant
3. 📊 **Customize**: Add your favorite stocks in Settings
4. 🔄 **Automate**: Set up periodic data refresh
5. 📚 **Learn**: Study the code and graph structure

---

## Getting Help

If you encounter issues:

1. **Check Documentation**
   - README.md - Project overview
   - QUICKSTART.md - Usage guide
   - This file - Installation help

2. **Review Logs**
   ```bash
   # Application logs
   cat logs/app.log

   # Neo4j logs (if using Docker)
   docker logs neo4j-financial
   ```

3. **Common Resources**
   - Neo4j Documentation: https://neo4j.com/docs/
   - OpenAI API Docs: https://platform.openai.com/docs
   - Anthropic Docs: https://docs.anthropic.com/
   - Streamlit Docs: https://docs.streamlit.io/

4. **Community Support**
   - Open an issue on GitHub
   - Check existing issues for solutions
   - Join discussions

---

## Congratulations! 🎉

You've successfully installed the Financial GraphRAG system!

You now have access to:
- ✅ Real-time financial data
- ✅ AI-powered market intelligence
- ✅ Explainable graph-based insights
- ✅ Interactive dashboard
- ✅ Natural language querying

**Start exploring and make informed financial decisions with confidence!**
