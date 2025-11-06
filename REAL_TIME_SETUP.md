# Real-Time Data Updates Setup Guide

## Overview

By default, the Financial GraphRAG system updates data **only when you manually refresh**. This guide shows you how to enable **automatic real-time updates**.

---

## ⚙️ Option 1: Auto-Refresh Service (Recommended)

I've created an auto-refresh service that runs in the background and updates data automatically.

### How It Works
- Runs continuously in the background
- Fetches new data every 5 minutes (configurable)
- Updates:
  - 📈 Stock prices
  - 📰 News articles
  - 📊 Market events
  - 💹 Company data

### How to Start

**Option A: Double-click the batch file**
```
start_auto_refresh.bat
```

**Option B: Run from command line**
```bash
".venv\Scripts\python.exe" auto_refresh_service.py
```

### Configuration

Edit `.env` to change refresh interval:
```bash
DATA_REFRESH_INTERVAL=300  # 300 seconds = 5 minutes
```

**Recommended intervals:**
- During market hours (9:30 AM - 4:00 PM ET): 300 seconds (5 min)
- After hours: 900 seconds (15 min)
- Overnight: 3600 seconds (1 hour)

### To Stop
Press `Ctrl+C` in the terminal running the auto-refresh service.

---

## 🔄 Option 2: Manual Refresh

### Via Web Interface
1. Go to any page
2. Click **"🔄 Refresh Data"** button
3. Wait for data to update

### Via Command Line
```bash
".venv\Scripts\python.exe" initialize_data.py
```

---

## ⏰ Option 3: Windows Task Scheduler (Set It and Forget It)

Create a scheduled task that runs automatically.

### Step-by-Step Setup

1. **Open Task Scheduler**
   - Press `Win + R`
   - Type: `taskschd.msc`
   - Press Enter

2. **Create New Task**
   - Click "Create Basic Task"
   - Name: `Financial GraphRAG Auto-Refresh`
   - Description: `Automatically refresh financial data`

3. **Set Trigger**
   - Trigger: Daily
   - Start time: 9:00 AM (before market opens)
   - Recur every: 1 day

4. **Set Action**
   - Action: Start a program
   - Program/script: `C:\Users\sande\Downloads\financial-graphrag\.venv\Scripts\python.exe`
   - Arguments: `initialize_data.py`
   - Start in: `C:\Users\sande\Downloads\financial-graphrag`

5. **Advanced Settings**
   - ✅ Run whether user is logged on or not
   - ✅ Run with highest privileges
   - Repeat task every: 5 minutes
   - For a duration of: 8 hours (during market hours)

---

## 📊 Option 4: Cron Job (Linux/Mac Alternative)

For Linux or Mac users, create a cron job:

```bash
# Edit crontab
crontab -e

# Add this line to refresh every 5 minutes during market hours (9:30 AM - 4:00 PM)
*/5 9-16 * * 1-5 cd /path/to/financial-graphrag && .venv/bin/python initialize_data.py
```

---

## 🎯 Comparison of Options

| Option | Real-Time | Setup | Resource Usage | Best For |
|--------|-----------|-------|----------------|----------|
| **Auto-Refresh Service** | ✅ Yes | Easy | Medium | Active trading |
| **Manual Refresh** | ❌ No | None | Low | Occasional use |
| **Task Scheduler** | ⚠️ Periodic | Medium | Low | Daily updates |
| **Cron Job** | ⚠️ Periodic | Medium | Low | Linux/Mac users |

---

## 💡 Recommended Setup for Real-Time Trading

For the **most real-time experience**, use this combination:

1. **Run Auto-Refresh Service:**
   ```bash
   start_auto_refresh.bat
   ```

2. **Keep it running in a separate terminal window**

3. **Access the app:**
   ```bash
   streamlit run src/ui/app.py
   ```

4. **You'll now have:**
   - ✅ News updated every 5 minutes
   - ✅ Stock prices refreshed automatically
   - ✅ Real-time market insights
   - ✅ Live AI responses with fresh data

---

## 📈 Data Freshness Indicator

To see when data was last updated, check:
- **Home Page**: Database statistics
- **Market Dashboard**: Refresh timestamp
- **Logs**: Check `logs/auto_refresh.log`

---

## 🔧 Troubleshooting

### Auto-Refresh Not Working?

1. **Check Neo4j is running:**
   ```
   http://localhost:7474
   ```

2. **Check API keys in `.env`:**
   - FINNHUB_API_KEY
   - NEWSAPI_KEY
   - ANTHROPIC_API_KEY or OPENAI_API_KEY

3. **Check logs:**
   ```
   tail -f logs/auto_refresh.log
   ```

4. **Test manually:**
   ```bash
   ".venv\Scripts\python.exe" initialize_data.py
   ```

### API Rate Limits?

If you hit rate limits:
- Increase refresh interval to 600 seconds (10 min)
- Reduce number of tracked companies
- Upgrade to paid API tiers

---

## 🚀 Quick Start (Recommended)

**For immediate real-time updates:**

1. Open **TWO** terminal windows:

**Terminal 1 - Auto-Refresh:**
```bash
cd C:\Users\sande\Downloads\financial-graphrag
start_auto_refresh.bat
```

**Terminal 2 - Streamlit App:**
```bash
cd C:\Users\sande\Downloads\financial-graphrag
".venv\Scripts\python.exe" -m streamlit run src/ui/app.py
```

2. Access: http://localhost:8501

3. **Done!** Your app now has real-time updates every 5 minutes! 🎉

---

## ⚠️ Important Notes

- **API Costs**: Free tiers have limits (be mindful of refresh frequency)
- **Resource Usage**: Auto-refresh uses more system resources
- **Market Hours**: Consider running only during trading hours (9:30 AM - 4:00 PM ET)
- **Weekend**: Stock prices won't change on weekends, but news still updates

---

**Enjoy your real-time financial intelligence platform!** 📈🚀
