# Real-Time Financial Intelligence with GraphRAG

A Graph-based Retrieval-Augmented Generation (GraphRAG) system for explainable, real-time financial market analysis.

## Overview

This system combines:
- **Dynamic Knowledge Graphs** (Neo4j) for structured financial entity relationships
- **Large Language Models** (GPT-4/Claude) for natural language understanding
- **Real-time Data Ingestion** from multiple financial APIs
- **GraphRAG Architecture** for fact-grounded, explainable insights

## Architecture

```
Data Sources (APIs) → Entity Extraction (FinBERT/spaCy) → Knowledge Graph (Neo4j)
                                                                ↓
User Query → Query Understanding → Graph Retrieval (Cypher) → Context Serialization
                                                                ↓
                                            LLM Grounded Generation → Answer + Explanation
```

## Features

- Real-time financial data ingestion from Yahoo Finance, Finnhub, NewsAPI, Reddit
- NLP-powered entity and event extraction using FinBERT
- Dynamic knowledge graph with companies, events, sectors, and relationships
- GraphRAG query engine with multi-hop graph traversal
- Explainable AI with visual graph path tracing
- Interactive Streamlit web interface

## Prerequisites

- Python 3.11+
- Neo4j Desktop or Docker
- 16GB RAM minimum
- API Keys (see Configuration)

## Installation

### Step 1: Install Neo4j

**Option A: Neo4j Desktop (Recommended for beginners)**
1. Download from: https://neo4j.com/download/
2. Install and create a new project
3. Create a database with password
4. Start the database

**Option B: Docker**
```bash
docker run -d --name neo4j \
  -p 7474:7474 -p 7687:7687 \
  -e NEO4J_AUTH=neo4j/your_password \
  neo4j:latest
```

### Step 2: Install Python Dependencies

```bash
pip install -r requirements.txt
python -m spacy download en_core_web_sm
```

### Step 3: Configure Environment

Copy `.env.example` to `.env` and add your API keys:

```bash
cp config/.env.example .env
```

Edit `.env` with your API keys.

## Configuration

Required API Keys:
- **OpenAI**: Get from https://platform.openai.com/api-keys (OR)
- **Anthropic**: Get from https://console.anthropic.com/
- **Finnhub**: Get from https://finnhub.io/register
- **NewsAPI**: Get from https://newsapi.org/register
- **Reddit** (Optional): Create app at https://www.reddit.com/prefs/apps

## Usage

### 1. Ingest Initial Data

```bash
python src/data_ingestion/ingest_all.py
```

### 2. Start the Web Interface

```bash
streamlit run src/ui/app.py
```

Access at: http://localhost:8501

### 3. Example Queries

- "How is Apple's stock performing today?"
- "What are the latest events affecting Tesla?"
- "Show me companies in the tech sector with recent negative sentiment"
- "Explain the relationship between Microsoft and OpenAI"

## Project Structure

```
financial-graphrag/
├── src/
│   ├── data_ingestion/      # API data collectors
│   ├── entity_extraction/   # NLP entity/event extraction
│   ├── graph_db/            # Neo4j schema and operations
│   ├── graphrag_engine/     # Query understanding and graph retrieval
│   ├── llm_integration/     # LLM grounding and generation
│   └── ui/                  # Streamlit interface
├── config/                  # Configuration files
├── data/                    # Raw data storage
├── logs/                    # Application logs
├── notebooks/               # Jupyter notebooks
└── tests/                   # Unit tests
```

## Development

Run tests:
```bash
pytest tests/
```

Format code:
```bash
black src/
```

## Troubleshooting

**Neo4j Connection Issues:**
- Verify Neo4j is running: Check http://localhost:7474
- Check credentials in .env file
- Ensure ports 7474 and 7687 are not blocked

**API Rate Limits:**
- Use free tier limits responsibly
- Implement caching in config
- Upgrade to paid tiers for production

**Memory Issues:**
- Reduce batch sizes in config
- Use smaller transformer models
- Increase system swap space

## References

Based on research paper: "Real-Time Financial Intelligence through Graph-Augmented Retrieval"

## License

MIT License
