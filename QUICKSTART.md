# 🚀 Quick Start Guide

Get your Financial GraphRAG system up and running in minutes!

## Prerequisites

- Python 3.11 or higher
- 16GB RAM minimum
- 100GB free disk space
- Internet connection

## Step-by-Step Setup

### 1. Install Dependencies

```bash
cd financial-graphrag
python setup.py
```

This will automatically:
- Install Python packages
- Download spaCy language model
- Create .env configuration file

### 2. Set Up Neo4j Database

#### Option A: Neo4j Desktop (Recommended for Beginners)

1. Download Neo4j Desktop from https://neo4j.com/download/
2. Install and launch Neo4j Desktop
3. Click "New" → "Create Project"
4. Click "Add" → "Local DBMS"
5. Set a password (remember this!)
6. Click "Start"
7. Verify it's running at http://localhost:7474

#### Option B: Docker (For Advanced Users)

```bash
docker run -d --name neo4j \
  -p 7474:7474 -p 7687:7687 \
  -e NEO4J_AUTH=neo4j/yourpassword \
  neo4j:latest
```

### 3. Get API Keys

#### Required: LLM API Key (Choose ONE)

**Option 1: OpenAI GPT-4**
1. Go to https://platform.openai.com/api-keys
2. Sign up or log in
3. Create a new API key
4. Copy the key

**Option 2: Anthropic Claude**
1. Go to https://console.anthropic.com/
2. Sign up or log in
3. Generate API key
4. Copy the key

#### Optional: Financial Data APIs (For Full Functionality)

**Finnhub (Recommended)**
1. Go to https://finnhub.io/register
2. Sign up for free tier
3. Copy API key

**NewsAPI**
1. Go to https://newsapi.org/register
2. Sign up for free tier
3. Copy API key

### 4. Configure Environment Variables

Edit the `.env` file in your project directory:

```bash
# Neo4j Configuration
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=your_neo4j_password_here

# Choose ONE LLM provider
LLM_PROVIDER=openai  # or anthropic

# If using OpenAI:
OPENAI_API_KEY=sk-your-key-here
OPENAI_MODEL=gpt-4

# If using Anthropic:
ANTHROPIC_API_KEY=your-key-here
ANTHROPIC_MODEL=claude-3-sonnet-20240229

# Financial APIs (Optional but recommended)
FINNHUB_API_KEY=your-finnhub-key-here
NEWSAPI_KEY=your-newsapi-key-here
```

**Important:** Replace `your_*_here` with your actual keys!

### 5. Initialize the Knowledge Graph

```bash
python initialize_data.py
```

This will:
- Connect to Neo4j
- Create the graph schema
- Fetch data for default companies (AAPL, MSFT, GOOGL, etc.)
- Populate the knowledge graph

**Note:** This may take 5-10 minutes depending on API rate limits.

### 6. Launch the Application

```bash
streamlit run src/ui/app.py
```

The application will open in your browser at: **http://localhost:8501**

## Using the Application

### 1. Home Page
- View system status
- See recent news
- Quick actions for data refresh

### 2. AI Assistant 💬
Ask questions like:
- "What's the latest news about Apple?"
- "Show me companies in the technology sector"
- "What's the sentiment for Tesla?"
- "Explain Microsoft's recent performance"

All answers are grounded in real graph data!

### 3. Market Dashboard 📊
- View real-time stock prices
- See market gainers and losers
- Track top companies by market cap

### 4. News Feed 📰
- Browse latest financial news
- Filter by sentiment (positive/negative/neutral)
- Search for specific companies or topics

### 5. Graph Explorer 🔍
- View knowledge graph statistics
- Execute custom Cypher queries
- Explore entity relationships

### 6. Settings ⚙️
- Configure tracked companies
- Set data refresh intervals
- Manage database

## Quick Tips

### Refresh Data Regularly
- Click "Refresh Data" in Settings or Home page
- Recommended: Every 5-15 minutes during market hours
- Data includes: stock prices, news, events

### Ask Natural Questions
The AI understands:
- Company names: "Tell me about Apple"
- Ticker symbols: "What's TSLA doing?"
- Sectors: "Show me tech companies"
- Events: "Recent Microsoft events"
- Sentiment: "Is Tesla news positive?"

### Explore Relationships
Try queries like:
- "What companies are similar to Apple?"
- "Show me companies in the same sector as Microsoft"
- "How are Google and OpenAI related?"

## Troubleshooting

### Neo4j Won't Connect
```
❌ Neo4j Disconnected
```

**Solutions:**
1. Verify Neo4j is running: http://localhost:7474
2. Check password in .env matches Neo4j password
3. Restart Neo4j database
4. Check firewall settings for ports 7474 and 7687

### LLM Not Initialized
```
❌ LLM Not Initialized
```

**Solutions:**
1. Check API key is in .env file
2. Verify API key is valid (test on provider website)
3. Check LLM_PROVIDER setting (openai or anthropic)
4. Ensure internet connection

### No Data Available
```
ℹ️ No data available
```

**Solutions:**
1. Click "Refresh Data" button
2. Run `python initialize_data.py`
3. Check API keys for Finnhub and NewsAPI
4. Wait a moment for data to load

### API Rate Limits
```
Error: Rate limit exceeded
```

**Solutions:**
1. Wait a few minutes before retrying
2. Reduce refresh frequency
3. Upgrade to paid API tiers
4. Reduce number of tracked companies

## What's Next?

### Customize Tracked Companies
1. Go to Settings page
2. Edit company list (comma-separated tickers)
3. Click "Refresh Now"

### Schedule Auto-Refresh
Set up a cron job or scheduled task:

```bash
# Every 15 minutes during market hours (9:30 AM - 4:00 PM ET)
*/15 9-16 * * 1-5 cd /path/to/financial-graphrag && python initialize_data.py
```

### Explore Advanced Features
- Write custom Cypher queries in Graph Explorer
- Analyze sentiment trends over time
- Track specific events (earnings, mergers, etc.)
- Build custom dashboards

## Need Help?

- 📖 Read full documentation: `README.md`
- 🐛 Report issues: GitHub Issues
- 💬 Ask questions: Discussions
- 📧 Contact: Your support email

## Success Checklist

- [ ] Python 3.11+ installed
- [ ] Dependencies installed (`python setup.py`)
- [ ] Neo4j running and accessible
- [ ] .env file configured with API keys
- [ ] Data initialized (`python initialize_data.py`)
- [ ] Application running (`streamlit run src/ui/app.py`)
- [ ] Successfully asked first question in AI Assistant
- [ ] Explored Market Dashboard
- [ ] Refreshed data successfully

**Congratulations!** You're now running a state-of-the-art financial intelligence system! 🎉

---

**Pro Tip:** Bookmark this guide for quick reference. The system becomes more valuable as you accumulate more data over time!
