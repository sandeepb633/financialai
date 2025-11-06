"""Main Streamlit application for Financial GraphRAG system."""

import streamlit as st
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.graph_db.neo4j_connector import Neo4jConnector
from src.graphrag_engine.query_engine import GraphRAGQueryEngine
from src.llm_integration.llm_client import LLMClient, GraphRAGGenerator
from src.graph_db.graph_populator import GraphPopulator
from config.config import settings
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Page configuration
st.set_page_config(
    page_title="Financial Intelligence GraphRAG",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    /* Main Header Styling */
    .main-header {
        font-size: 2.8rem;
        font-weight: 800;
        background: linear-gradient(120deg, #1f77b4, #2ecc71);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin-bottom: 2rem;
        padding: 1rem 0;
    }

    /* Sub Headers */
    .sub-header {
        font-size: 1.6rem;
        font-weight: 700;
        color: #2c3e50;
        margin-top: 1.5rem;
        margin-bottom: 1rem;
        border-bottom: 3px solid #1f77b4;
        padding-bottom: 0.5rem;
    }

    /* Enhanced Metric Cards */
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 15px;
        padding: 2rem;
        box-shadow: 0 10px 25px rgba(0,0,0,0.15);
        color: white;
        transition: transform 0.3s ease;
    }

    .metric-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 15px 35px rgba(0,0,0,0.25);
    }

    /* Stock Cards */
    .stock-card {
        background: white;
        border-radius: 12px;
        padding: 1.5rem;
        margin: 0.5rem 0;
        box-shadow: 0 4px 6px rgba(0,0,0,0.07);
        border-left: 4px solid #1f77b4;
        transition: all 0.3s ease;
    }

    .stock-card:hover {
        box-shadow: 0 8px 15px rgba(0,0,0,0.15);
        transform: translateX(5px);
    }

    /* Price Indicators */
    .positive {
        color: #28a745;
        font-weight: bold;
        font-size: 1.1rem;
    }

    .negative {
        color: #dc3545;
        font-weight: bold;
        font-size: 1.1rem;
    }

    .neutral {
        color: #6c757d;
        font-weight: 600;
    }

    /* News Card */
    .news-card {
        background: white;
        border-radius: 10px;
        padding: 1.5rem;
        margin: 1rem 0;
        box-shadow: 0 3px 10px rgba(0,0,0,0.1);
        border-left: 4px solid #3498db;
        transition: all 0.3s ease;
    }

    .news-card:hover {
        box-shadow: 0 5px 20px rgba(0,0,0,0.2);
        border-left-width: 6px;
    }

    /* Info Boxes */
    .info-box {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 10px;
        padding: 1.5rem;
        margin: 1rem 0;
        color: white;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
    }

    .success-box {
        background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
        border-radius: 10px;
        padding: 1.5rem;
        margin: 1rem 0;
        color: white;
        box-shadow: 0 4px 15px rgba(17, 153, 142, 0.4);
    }

    .warning-box {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        border-radius: 10px;
        padding: 1.5rem;
        margin: 1rem 0;
        color: white;
        box-shadow: 0 4px 15px rgba(240, 147, 251, 0.4);
    }

    /* Sentiment Badges */
    .sentiment-positive {
        background: #d4edda;
        color: #155724;
        padding: 0.5rem 1rem;
        border-radius: 20px;
        font-weight: 600;
        display: inline-block;
    }

    .sentiment-negative {
        background: #f8d7da;
        color: #721c24;
        padding: 0.5rem 1rem;
        border-radius: 20px;
        font-weight: 600;
        display: inline-block;
    }

    .sentiment-neutral {
        background: #d1ecf1;
        color: #0c5460;
        padding: 0.5rem 1rem;
        border-radius: 20px;
        font-weight: 600;
        display: inline-block;
    }

    /* Sidebar Enhancement */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1e3c72 0%, #2a5298 100%);
    }

    /* Button Styling */
    .stButton>button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-radius: 25px;
        padding: 0.75rem 2rem;
        font-weight: 600;
        border: none;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
        transition: all 0.3s ease;
    }

    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(102, 126, 234, 0.6);
    }
</style>
""", unsafe_allow_html=True)


# Initialize session state
def init_session_state():
    """Initialize session state variables."""
    if 'initialized' not in st.session_state:
        st.session_state.initialized = False
        st.session_state.neo4j_connected = False
        st.session_state.llm_initialized = False
        st.session_state.chat_history = []


@st.cache_resource
def get_neo4j_connector():
    """Get cached Neo4j connector."""
    try:
        connector = Neo4jConnector()
        st.session_state.neo4j_connected = True
        return connector
    except Exception as e:
        logger.error(f"Failed to connect to Neo4j: {e}")
        st.session_state.neo4j_connected = False
        return None


@st.cache_resource
def get_llm_client():
    """Get cached LLM client."""
    try:
        client = LLMClient()
        st.session_state.llm_initialized = True
        return client
    except Exception as e:
        logger.error(f"Failed to initialize LLM: {e}")
        st.session_state.llm_initialized = False
        return None


def main():
    """Main application."""
    init_session_state()

    # Sidebar
    with st.sidebar:
        st.image("https://via.placeholder.com/300x100/1f77b4/ffffff?text=Financial+GraphRAG", use_column_width=True)
        st.markdown("---")

        # Navigation
        page = st.radio(
            "Navigation",
            ["Home", "AI Assistant", "Market Dashboard", "News Feed",
             "Graph Explorer", "Settings", "Help"],
            label_visibility="collapsed"
        )

        st.markdown("---")

        # System Status
        st.subheader("System Status")

        # Neo4j Status
        connector = get_neo4j_connector()
        if connector:
            st.success("Neo4j Connected")
            try:
                stats = connector.get_database_stats()
                st.metric("Companies", stats.get('companies', 0))
                st.metric("News Articles", stats.get('news', 0))
                st.metric("Events", stats.get('events', 0))
            except:
                pass
        else:
            st.error("Neo4j Disconnected")

        # LLM Status
        llm_client = get_llm_client()
        if llm_client:
            st.success(f"LLM Ready ({settings.LLM_PROVIDER})")
        else:
            st.error("LLM Not Initialized")

        st.markdown("---")
        st.caption("Real-Time Financial Intelligence")
        st.caption("Powered by GraphRAG")

    # Main content based on selected page
    if page == "Home":
        show_home_page(connector)
    elif page == "AI Assistant":
        show_ai_assistant_page(connector, llm_client)
    elif page == "Market Dashboard":
        show_market_dashboard_page(connector)
    elif page == "News Feed":
        show_news_feed_page(connector)
    elif page == "Graph Explorer":
        show_graph_explorer_page(connector)
    elif page == "Settings":
        show_settings_page(connector)
    elif page == "Help":
        show_help_page()


def show_home_page(connector):
    """Show home page."""
    st.markdown('<div class="main-header">Financial Intelligence GraphRAG</div>', unsafe_allow_html=True)

    # Welcome Box with gradient
    st.markdown("""
    <div class="info-box">
    <h2 style="margin-top: 0; color: white;">Welcome to Real-Time Financial Intelligence</h2>
    <p style="font-size: 1.1rem; margin-bottom: 0;">
    Harness the power of Graph-based Retrieval-Augmented Generation (GraphRAG) for
    explainable, fact-grounded financial insights powered by live market data and AI.
    </p>
    </div>
    """, unsafe_allow_html=True)

    # Quick Stats
    if connector:
        try:
            stats = connector.get_database_stats()
            col1, col2, col3, col4 = st.columns(4)

            with col1:
                st.markdown("""
                <div class="stock-card" style="text-align: center;">
                    <h1 style="color: #667eea; margin: 0;">{}</h1>
                    <p style="color: #888; margin: 0.5rem 0 0 0;">Companies Tracked</p>
                </div>
                """.format(stats.get('companies', 0)), unsafe_allow_html=True)

            with col2:
                st.markdown("""
                <div class="stock-card" style="text-align: center;">
                    <h1 style="color: #3498db; margin: 0;">{}</h1>
                    <p style="color: #888; margin: 0.5rem 0 0 0;">News Articles</p>
                </div>
                """.format(stats.get('news', 0)), unsafe_allow_html=True)

            with col3:
                st.markdown("""
                <div class="stock-card" style="text-align: center;">
                    <h1 style="color: #e74c3c; margin: 0;">{}</h1>
                    <p style="color: #888; margin: 0.5rem 0 0 0;">Market Events</p>
                </div>
                """.format(stats.get('events', 0)), unsafe_allow_html=True)

            with col4:
                st.markdown("""
                <div class="stock-card" style="text-align: center;">
                    <h1 style="color: #2ecc71; margin: 0;">{}</h1>
                    <p style="color: #888; margin: 0.5rem 0 0 0;">Relationships</p>
                </div>
                """.format(stats.get('relationships', 0)), unsafe_allow_html=True)
        except:
            pass

    st.markdown("<br>", unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("### Key Features")
        st.markdown("""
        - **Real-time Data**: Live market data from multiple sources
        - **Knowledge Graph**: Dynamic Neo4j graph database
        - **AI-Powered**: GPT-4/Claude for natural language understanding
        - **Explainable**: Transparent reasoning with graph evidence
        - **Multi-hop Queries**: Complex relationship traversal
        """)

    with col2:
        st.markdown("### Quick Start")
        st.markdown("""
        1. **AI Assistant**: Ask questions in natural language
        2. **Market Dashboard**: View real-time market overview
        3. **News Feed**: Browse latest financial news
        4. **Graph Explorer**: Explore knowledge graph visually
        5. **Settings**: Configure data refresh and API keys
        """)

    with col3:
        st.markdown("### Data Sources")
        st.markdown("""
        - **Yahoo Finance**: Stock prices & company info
        - **Finnhub**: Real-time news & events
        - **NewsAPI**: Market news & headlines
        - **Financial NLP**: Entity & sentiment extraction
        - **Neo4j Graph**: Relationship mapping
        """)

    st.markdown("---")

    # Quick Actions
    st.markdown("### Quick Actions")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        if st.button("Refresh Data"):
            if connector:
                with st.spinner("Refreshing market data..."):
                    populator = GraphPopulator(connector)
                    stats = populator.refresh_all_data(settings.DEFAULT_COMPANIES)
                    st.success(f"Updated {stats['companies_updated']} companies!")
            else:
                st.error("Neo4j not connected")

    with col2:
        st.info("Use sidebar navigation to access AI Assistant")

    with col3:
        st.info("Use sidebar to view Market Dashboard")

    with col4:
        st.info("Use sidebar to explore the Graph")

    # Recent Activity
    if connector:
        st.markdown("---")
        st.markdown("### Recent News")

        try:
            query_engine = GraphRAGQueryEngine(connector)
            result = query_engine.execute_query("Show me trending news")

            if result['results']:
                for item in result['results'][:5]:
                    with st.container():
                        cols = st.columns([3, 1])
                        with cols[0]:
                            st.markdown(f"**{item.get('headline', 'No headline')}**")
                            st.caption(f"{item.get('company_name', 'Market')} • {item.get('published_at', '')}")
                        with cols[1]:
                            sentiment = item.get('sentiment', 'neutral')
                            if sentiment == 'positive':
                                st.success(f"{sentiment.upper()}")
                            elif sentiment == 'negative':
                                st.error(f"{sentiment.upper()}")
                            else:
                                st.info(f"{sentiment.upper()}")
                        st.markdown("---")
        except Exception as e:
            st.info("No recent news available yet. Click 'Refresh Data' to load market data.")


def show_ai_assistant_page(connector, llm_client):
    """Show AI assistant chat interface."""
    st.markdown('<div class="main-header">AI Financial Assistant</div>', unsafe_allow_html=True)

    st.markdown("""
    <div class="info-box">
    Ask me anything about financial markets, companies, news, or events!
    All responses are grounded in real-time knowledge graph data.
    </div>
    """, unsafe_allow_html=True)

    if not connector or not llm_client:
        st.error("System not fully initialized. Check Neo4j connection and LLM configuration.")
        return

    # Initialize query engine and generator
    query_engine = GraphRAGQueryEngine(connector)
    generator = GraphRAGGenerator(llm_client)

    # Example queries
    st.markdown("### Example Queries")
    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("Tell me about Apple"):
            st.session_state['user_input'] = "Tell me about Apple's stock performance"

    with col2:
        if st.button("Latest tech news"):
            st.session_state['user_input'] = "What's the latest news in technology sector?"

    with col3:
        if st.button("Market sentiment"):
            st.session_state['user_input'] = "What's the overall market sentiment?"

    # Chat interface
    st.markdown("---")

    # Display chat history
    for message in st.session_state.chat_history:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Chat input
    user_query = st.chat_input("Ask me about financial markets...")

    # Process from button click
    if 'user_input' in st.session_state:
        user_query = st.session_state['user_input']
        del st.session_state['user_input']

    if user_query:
        # Add user message to history
        st.session_state.chat_history.append({"role": "user", "content": user_query})

        with st.chat_message("user"):
            st.markdown(user_query)

        with st.chat_message("assistant"):
            with st.spinner("Analyzing knowledge graph..."):
                try:
                    # Execute graph query
                    query_result = query_engine.execute_query(user_query)

                    # Generate grounded response
                    response = generator.generate_grounded_response(user_query, query_result)

                    # Display response
                    st.markdown(response['response'])

                    # Show metadata in expander
                    with st.expander("View Query Details"):
                        st.markdown(f"**Intent:** {response['intent']}")
                        st.markdown(f"**Results Found:** {response['num_results']}")
                        st.markdown("**Cypher Query:**")
                        st.code(response['cypher_query'], language='cypher')

                    # Add assistant response to history
                    st.session_state.chat_history.append({
                        "role": "assistant",
                        "content": response['response']
                    })

                except Exception as e:
                    error_msg = f"Error processing query: {str(e)}"
                    st.error(error_msg)
                    st.session_state.chat_history.append({
                        "role": "assistant",
                        "content": error_msg
                    })

    # Clear chat button
    if st.button("Clear Chat History"):
        st.session_state.chat_history = []
        st.rerun()


def show_market_dashboard_page(connector):
    """Show market dashboard page."""
    st.markdown('<div class="main-header">Real-Time Market Dashboard</div>', unsafe_allow_html=True)

    if not connector:
        st.error("Neo4j not connected. Please check your configuration.")
        return

    # Refresh button
    col1, col2, col3 = st.columns([1, 1, 2])
    with col1:
        if st.button("Refresh Data"):
            with st.spinner("Refreshing..."):
                populator = GraphPopulator(connector)
                populator.refresh_all_data(settings.DEFAULT_COMPANIES)
                st.success("Data refreshed!")
                st.rerun()

    st.markdown("---")

    # Market Overview
    try:
        query = """
        MATCH (c:Company)
        OPTIONAL MATCH (c)-[:BELONGS_TO]->(s:Sector)
        RETURN c.symbol as symbol, c.name as name, c.sector as sector,
               c.price as price, c.price_change_pct as change,
               c.market_cap as market_cap, c.volume as volume
        ORDER BY c.market_cap DESC
        LIMIT 20
        """

        results = connector.execute_query(query)

        if results:
            import pandas as pd
            import plotly.express as px
            import plotly.graph_objects as go

            df = pd.DataFrame(results)

            # Summary metrics with enhanced styling
            st.markdown("### Market Summary")
            col1, col2, col3, col4 = st.columns(4)

            total_companies = len(results)
            gainers = sum(1 for r in results if r.get('change') is not None and r.get('change') > 0)
            losers = sum(1 for r in results if r.get('change') is not None and r.get('change') < 0)
            neutral = total_companies - gainers - losers

            col1.metric("Total Companies", total_companies, help="Total tracked companies")
            col2.metric("Gainers", gainers, delta=f"{(gainers/total_companies*100):.1f}%", delta_color="normal")
            col3.metric("Losers", losers, delta=f"-{(losers/total_companies*100):.1f}%", delta_color="inverse")
            col4.metric("Neutral", neutral)

            st.markdown("---")

            # Interactive Charts
            col1, col2 = st.columns(2)

            with col1:
                # Top Companies by Market Cap
                st.markdown("#### Top Companies by Market Cap")
                df_sorted = df.nlargest(10, 'market_cap')
                fig = px.bar(
                    df_sorted,
                    x='symbol',
                    y='market_cap',
                    color='change',
                    color_continuous_scale=['red', 'yellow', 'green'],
                    labels={'market_cap': 'Market Cap ($)', 'symbol': 'Company'},
                    height=400
                )
                fig.update_layout(
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    font=dict(size=12)
                )
                st.plotly_chart(fig, use_container_width=True)

            with col2:
                # Sector Distribution
                st.markdown("#### Sector Distribution")
                sector_counts = df['sector'].value_counts()
                fig = px.pie(
                    values=sector_counts.values,
                    names=sector_counts.index,
                    hole=0.4,
                    height=400
                )
                fig.update_traces(textposition='inside', textinfo='percent+label')
                fig.update_layout(
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    font=dict(size=12)
                )
                st.plotly_chart(fig, use_container_width=True)

            st.markdown("---")

            # Stock Performance Chart
            st.markdown("#### Stock Performance Overview")
            df_chart = df[df['change'].notna()].copy()
            df_chart['color'] = df_chart['change'].apply(lambda x: 'green' if x > 0 else 'red')

            fig = go.Figure()
            fig.add_trace(go.Bar(
                x=df_chart['symbol'],
                y=df_chart['change'],
                marker_color=df_chart['color'],
                text=df_chart['change'].apply(lambda x: f"{x:+.2f}%"),
                textposition='outside',
                hovertemplate='<b>%{x}</b><br>Change: %{y:.2f}%<extra></extra>'
            ))
            fig.update_layout(
                title="Daily Price Changes (%)",
                xaxis_title="Company",
                yaxis_title="Change (%)",
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                height=400,
                showlegend=False
            )
            st.plotly_chart(fig, use_container_width=True)

            st.markdown("---")

            # Enhanced Company Table
            st.markdown("### Detailed Company Data")

            # Format the dataframe
            df_display = df.copy()
            df_display['price_formatted'] = df_display['price'].apply(lambda x: f"${x:.2f}" if pd.notna(x) else "N/A")
            df_display['change_formatted'] = df_display['change'].apply(lambda x: f"{x:+.2f}%" if pd.notna(x) else "N/A")
            df_display['market_cap_formatted'] = df_display['market_cap'].apply(
                lambda x: f"${x/1e9:.2f}B" if pd.notna(x) and x > 0 else "N/A"
            )
            df_display['volume_formatted'] = df_display['volume'].apply(
                lambda x: f"{x:,.0f}" if pd.notna(x) else "N/A"
            )

            # Display interactive dataframe
            st.dataframe(
                df_display[['symbol', 'name', 'sector', 'price_formatted', 'change_formatted', 'market_cap_formatted', 'volume_formatted']].rename(columns={
                    'price_formatted': 'Price',
                    'change_formatted': 'Change',
                    'market_cap_formatted': 'Market Cap',
                    'volume_formatted': 'Volume'
                }),
                use_container_width=True,
                height=400
            )

        else:
            st.info("No market data available. Click 'Refresh Data' to load data.")

    except Exception as e:
        st.error(f"Error loading market data: {str(e)}")


def show_news_feed_page(connector):
    """Show news feed page."""
    st.markdown('<div class="main-header">Financial News Feed</div>', unsafe_allow_html=True)

    if not connector:
        st.error("Neo4j not connected.")
        return

    # Filter options
    col1, col2 = st.columns([2, 1])
    with col1:
        search_query = st.text_input("Search news", placeholder="Enter company name or topic...")
    with col2:
        sentiment_filter = st.selectbox("Sentiment Filter", ["All", "Positive", "Negative", "Neutral"])

    st.markdown("---")

    try:
        # Build query based on filters
        cypher = """
        MATCH (n:News)
        OPTIONAL MATCH (n)-[:MENTIONS]->(c:Company)
        """

        conditions = []
        params = {}

        if search_query:
            conditions.append("(n.headline CONTAINS $search OR c.name CONTAINS $search)")
            params['search'] = search_query

        if sentiment_filter != "All":
            conditions.append("n.sentiment_label = $sentiment")
            params['sentiment'] = sentiment_filter.lower()

        if conditions:
            cypher += "WHERE " + " AND ".join(conditions) + "\n"

        cypher += """
        RETURN n.headline as headline, n.summary as summary, n.source as source,
               n.published_at as published_at, n.sentiment_label as sentiment,
               n.url as url, c.name as company
        ORDER BY n.published_at DESC
        LIMIT 30
        """

        results = connector.execute_query(cypher, params)

        if results:
            st.markdown(f"### Found {len(results)} articles")
            st.markdown("")

            for article in results:
                sentiment = article.get('sentiment', 'neutral')

                # Determine sentiment badge class
                if sentiment == 'positive':
                    sentiment_class = 'sentiment-positive'
                    sentiment_text = 'Positive'
                elif sentiment == 'negative':
                    sentiment_class = 'sentiment-negative'
                    sentiment_text = 'Negative'
                else:
                    sentiment_class = 'sentiment-neutral'
                    sentiment_text = 'Neutral'

                # Create news card with custom HTML
                st.markdown(f"""
                <div class="news-card">
                    <div style="display: flex; justify-content: space-between; align-items: start; margin-bottom: 1rem;">
                        <h3 style="margin: 0; color: #2c3e50; font-size: 1.3rem;">{article['headline']}</h3>
                        <span class="{sentiment_class}">{sentiment_text}</span>
                    </div>
                    <p style="color: #555; margin: 0.5rem 0;">{article.get('summary', '')[:250]}{'...' if len(article.get('summary', '')) > 250 else ''}</p>
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-top: 1rem; color: #888; font-size: 0.9rem;">
                        <span>{article.get('source', 'Unknown')} • {article.get('published_at', 'N/A')}</span>
                        {'<span>' + article['company'] + '</span>' if article.get('company') else ''}
                    </div>
                </div>
                """, unsafe_allow_html=True)

                if article.get('url'):
                    st.markdown(f"[Read Full Article →]({article['url']})")

                st.markdown("")
        else:
            st.info("No news articles found. Try refreshing the data.")

    except Exception as e:
        st.error(f"Error loading news: {str(e)}")


def show_graph_explorer_page(connector):
    """Show graph explorer page."""
    st.markdown('<div class="main-header">Knowledge Graph Explorer</div>', unsafe_allow_html=True)

    if not connector:
        st.error("Neo4j not connected.")
        return

    st.markdown("""
    <div class="info-box">
    Explore the financial knowledge graph structure and relationships.
    </div>
    """, unsafe_allow_html=True)

    # Graph statistics
    st.markdown("### Graph Statistics")

    try:
        stats = connector.get_database_stats()

        col1, col2, col3, col4, col5 = st.columns(5)
        col1.metric("Companies", stats.get('companies', 0))
        col2.metric("News", stats.get('news', 0))
        col3.metric("Events", stats.get('events', 0))
        col4.metric("Sectors", stats.get('sectors', 0))
        col5.metric("Relationships", stats.get('relationships', 0))

        st.markdown("---")

        # Custom Cypher Query
        st.markdown("### Custom Cypher Query")

        query = st.text_area(
            "Enter Cypher query",
            value="MATCH (c:Company) RETURN c.symbol, c.name, c.sector LIMIT 10",
            height=100
        )

        if st.button("Execute Query"):
            try:
                results = connector.execute_query(query)
                st.success(f"Query returned {len(results)} results")

                if results:
                    import pandas as pd
                    df = pd.DataFrame(results)
                    st.dataframe(df)
            except Exception as e:
                st.error(f"Query error: {str(e)}")

    except Exception as e:
        st.error(f"Error loading graph data: {str(e)}")


def show_settings_page(connector):
    """Show settings page."""
    st.markdown('<div class="main-header">System Settings</div>', unsafe_allow_html=True)

    st.markdown("### Data Management")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("#### Tracked Companies")
        companies_text = st.text_area(
            "Companies to track (comma-separated ticker symbols)",
            value=", ".join(settings.DEFAULT_COMPANIES),
            height=150
        )

        if st.button("Save Companies"):
            st.success("Companies saved! (Note: Requires app restart)")

    with col2:
        st.markdown("#### Data Refresh")
        refresh_interval = st.number_input(
            "Auto-refresh interval (seconds)",
            min_value=60,
            max_value=3600,
            value=settings.DATA_REFRESH_INTERVAL,
            step=60
        )

        if st.button("Refresh Now"):
            if connector:
                with st.spinner("Refreshing..."):
                    populator = GraphPopulator(connector)
                    symbols = [s.strip() for s in companies_text.split(',')]
                    stats = populator.refresh_all_data(symbols)
                    st.success(f"Refreshed {stats['companies_updated']} companies!")

    st.markdown("---")

    st.markdown("### Database Management")

    st.warning("Warning: These actions cannot be undone!")

    col1, col2 = st.columns(2)

    with col1:
        if st.button("Rebuild Graph Schema", type="secondary"):
            if connector:
                connector.create_constraints()
                st.success("Schema rebuilt!")

    with col2:
        clear_confirm = st.checkbox("I understand this will delete all data")
        if st.button("Clear Database", type="primary", disabled=not clear_confirm):
            if connector and clear_confirm:
                connector.clear_database()
                st.success("Database cleared!")
                st.rerun()


def show_help_page():
    """Show help page."""
    st.markdown('<div class="main-header">Help & Documentation</div>', unsafe_allow_html=True)

    st.markdown("""
    ## Overview

    **Financial Intelligence GraphRAG** is a real-time financial analysis system that combines:
    - **Knowledge Graphs** (Neo4j) for structured data representation
    - **Large Language Models** (GPT-4/Claude) for natural language understanding
    - **GraphRAG Architecture** for explainable, fact-grounded insights

    ---

    ## Getting Started

    ### 1. Set Up Neo4j
    Download and install Neo4j Desktop or use Docker:
    ```bash
    docker run -d --name neo4j \\
      -p 7474:7474 -p 7687:7687 \\
      -e NEO4J_AUTH=neo4j/your_password \\
      neo4j:latest
    ```

    ### 2. Configure API Keys
    Create a `.env` file with:
    ```
    NEO4J_PASSWORD=your_password
    OPENAI_API_KEY=your_key  # or ANTHROPIC_API_KEY
    FINNHUB_API_KEY=your_key
    NEWSAPI_KEY=your_key
    ```

    ### 3. Install Dependencies
    ```bash
    pip install -r requirements.txt
    python -m spacy download en_core_web_sm
    ```

    ### 4. Run the Application
    ```bash
    streamlit run src/ui/app.py
    ```

    ---

    ## Using the AI Assistant

    The AI Assistant understands natural language queries such as:
    - "What's the latest news about Apple?"
    - "Show me companies in the technology sector"
    - "What's the sentiment for Tesla?"
    - "Explain the relationship between Microsoft and OpenAI"

    All responses are grounded in graph data - no hallucinations!

    ---

    ## Troubleshooting

    **Neo4j Connection Error:**
    - Verify Neo4j is running at http://localhost:7474
    - Check credentials in .env file
    - Ensure ports 7474 and 7687 are not blocked

    **LLM Not Initialized:**
    - Verify API key is set in .env
    - Check API key validity
    - Ensure internet connection

    **No Data Available:**
    - Click "Refresh Data" in Settings
    - Check API rate limits
    - Verify API keys are valid

    ---

    ## Resources

    - [Neo4j Documentation](https://neo4j.com/docs/)
    - [OpenAI API](https://platform.openai.com/docs)
    - [Anthropic Claude](https://docs.anthropic.com/)
    - [Project GitHub](https://github.com/yourusername/financial-graphrag)

    ---

    ## Support

    For issues and questions:
    - Open an issue on GitHub
    - Check the documentation
    - Review logs in the `logs/` directory
    """)


if __name__ == "__main__":
    main()
