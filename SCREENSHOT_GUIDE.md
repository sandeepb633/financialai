# Screenshot Guide for Interim Report

## Required Screenshots (6 Total - 2 per page)

### Page 1: Home & AI Assistant

**Screenshot 1: Home Page Dashboard**
1. Open: http://localhost:8501
2. Make sure you're on Home page
3. Screenshot should show:
   - Welcome banner with gradient
   - 4 stat cards (Companies, News, Events, Relationships)
   - Key Features, Quick Start, Data Sources sections
4. Tool: Windows Snipping Tool (Win + Shift + S)
5. Save as: `screenshot_1_home_page.png`

**Screenshot 2: AI Assistant with Query**
1. Click "💬 AI Assistant" in sidebar
2. Type query: "What is the current stock price of Apple?"
3. Wait for response showing $262.82
4. Screenshot should show:
   - Chat interface
   - User query
   - AI response with price
   - "View Query Details" section
5. Save as: `screenshot_2_ai_assistant.png`

---

### Page 2: Market Dashboard - Charts

**Screenshot 3: Market Cap & Sector Charts**
1. Click "📊 Market Dashboard" in sidebar
2. Scroll to see both charts:
   - Left: Market Cap bar chart
   - Right: Sector Distribution pie chart
3. Screenshot should show:
   - Both interactive charts
   - Color-coded visualization
   - Legends and labels
4. Save as: `screenshot_3_market_charts.png`

**Screenshot 4: Price Changes Chart & Data Table**
1. Still on Market Dashboard
2. Scroll down to show:
   - Daily Price Changes bar chart (green/red)
   - Detailed Company Data table below
3. Screenshot should show:
   - Price performance chart
   - Data table with all columns
4. Save as: `screenshot_4_market_data.png`

---

### Page 3: News Feed & Graph Stats

**Screenshot 5: News Feed with Sentiment**
1. Click "📰 News Feed" in sidebar
2. Screenshot should show:
   - At least 3 news cards
   - Sentiment badges (Positive/Negative/Neutral)
   - Headlines and summaries
   - Company tags
   - Source and date
5. Save as: `screenshot_5_news_feed.png`

**Screenshot 6: Graph Explorer Statistics**
1. Click "🔍 Graph Explorer" in sidebar
2. Screenshot should show:
   - Graph statistics (Companies, News, Events, Sectors, Relationships)
   - Custom Cypher query interface
   - Example query or results
3. Save as: `screenshot_6_graph_explorer.png`

---

## Tips for Good Screenshots

### Before Taking Screenshots:

1. **Clear Browser Cache & Refresh**
   - Press F5 to refresh
   - Ensure latest data is visible

2. **Zoom Level**
   - Set browser zoom to 100% (Ctrl + 0)
   - Makes text readable in report

3. **Window Size**
   - Maximize browser window
   - Or use consistent size for all screenshots

4. **Remove Clutter**
   - Close unnecessary browser tabs
   - Hide taskbar notifications
   - Clean desktop background

### Taking the Screenshot:

1. **Windows Snipping Tool:**
   - Press: `Win + Shift + S`
   - Select area to capture
   - Paste in Paint and save

2. **Full Browser Window:**
   - Press: `Alt + PrtScn` (captures active window)
   - Paste in Paint and save

3. **Crop and Edit:**
   - Remove unnecessary toolbars
   - Highlight important areas (optional)
   - Add arrows or labels if needed

### Screenshot Quality:

- **Format:** PNG (better quality than JPG)
- **Resolution:** At least 1920x1080
- **File Size:** Keep under 2MB per image
- **Naming:** Use descriptive names

---

## Inserting Screenshots into Report

### In Microsoft Word:

1. Create new section after Progress Summary
2. Insert heading: "3.4 Screenshots"
3. Insert images (2 per page):
   ```
   Insert → Pictures → Choose screenshot
   ```
4. Format:
   - Width: 6.5 inches (fits page)
   - Wrap text: Top and Bottom
   - Add caption below each:
     - "Figure 1: Home Page Dashboard"
     - "Figure 2: AI Assistant Query Interface"
     - etc.

### Layout Suggestion:

```
Page 1 (after section 3.3):
┌─────────────────────────────────┐
│   Screenshot 1: Home Page       │
│   [Image]                       │
│   Figure 1: Home Page Dashboard │
│                                 │
│   Screenshot 2: AI Assistant    │
│   [Image]                       │
│   Figure 2: AI Assistant Query  │
└─────────────────────────────────┘

Page 2:
┌─────────────────────────────────┐
│   Screenshot 3: Market Charts   │
│   [Image]                       │
│   Figure 3: Interactive Charts  │
│                                 │
│   Screenshot 4: Data Table      │
│   [Image]                       │
│   Figure 4: Market Data Table   │
└─────────────────────────────────┘

Page 3:
┌─────────────────────────────────┐
│   Screenshot 5: News Feed       │
│   [Image]                       │
│   Figure 5: News with Sentiment │
│                                 │
│   Screenshot 6: Graph Explorer  │
│   [Image]                       │
│   Figure 6: Database Statistics │
└─────────────────────────────────┘
```

---

## Converting Markdown to Word/PDF

### Option 1: Copy-Paste (Quick)
1. Open: `COMP_8977_Interim_Report.md`
2. Copy content
3. Paste into Microsoft Word
4. Format:
   - Font: Times New Roman, Size 12
   - Headers: Bold, appropriate sizes
   - Lists: Bullets and numbering
   - Page numbers
   - Table of contents (optional)

### Option 2: Pandoc (Professional)
```bash
pandoc COMP_8977_Interim_Report.md -o interim_report.docx
```
Then edit formatting in Word.

### Option 3: Online Converter
- Use: https://www.markdowntopdf.com/
- Upload markdown file
- Download PDF
- Edit if needed

---

## Final Checklist Before Submission

### Content:
- [ ] Cover page complete (name, ID, supervisor, date)
- [ ] All sections present (1-5)
- [ ] 6 screenshots inserted (2 per page max)
- [ ] Screenshots have captions
- [ ] All text is clear and readable
- [ ] No lorem ipsum or placeholder text

### Formatting:
- [ ] Font: Times New Roman, Size 12
- [ ] Page numbers added
- [ ] Headers formatted properly
- [ ] Lists formatted (bullets/numbers)
- [ ] Images properly sized
- [ ] No weird spacing

### File:
- [ ] Filename: `group#_interim_report.pdf`
- [ ] File size: < 10MB
- [ ] All pages present
- [ ] PDF opens correctly
- [ ] Screenshots visible in PDF

### Submission:
- [ ] Only one person submitting (if group)
- [ ] Submitted before Oct 30, 2025 deadline
- [ ] Confirmation email received
- [ ] Backup copy saved

---

## Quick Start Commands

**To take screenshots of running system:**

1. **Start services:**
   ```bash
   # Terminal 1 - Streamlit
   cd C:\Users\sande\Downloads\financial-graphrag
   ".venv\Scripts\python.exe" -m streamlit run src/ui/app.py

   # Terminal 2 - Auto-refresh (optional, for live data)
   cd C:\Users\sande\Downloads\financial-graphrag
   ".venv\Scripts\python.exe" auto_refresh_service.py
   ```

2. **Open browser:** http://localhost:8501

3. **Take 6 screenshots** following guide above

4. **Stop services:**
   - Press Ctrl+C in both terminals

---

Good luck with your report! 🎓📊
