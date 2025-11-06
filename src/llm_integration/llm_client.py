"""LLM client for grounded generation using OpenAI or Anthropic."""

import logging
from typing import Dict, List, Optional
from config.config import settings
import json

logger = logging.getLogger(__name__)


class LLMClient:
    """Client for interacting with LLMs (OpenAI or Anthropic)."""

    def __init__(self, provider: Optional[str] = None):
        """
        Initialize LLM client.

        Args:
            provider: LLM provider ('openai' or 'anthropic', uses config if not provided)
        """
        self.provider = provider or settings.LLM_PROVIDER

        if self.provider == 'openai':
            self._init_openai()
        elif self.provider == 'anthropic':
            self._init_anthropic()
        else:
            raise ValueError(f"Unsupported LLM provider: {self.provider}")

    def _init_openai(self):
        """Initialize OpenAI client."""
        try:
            from openai import OpenAI
            self.client = OpenAI(api_key=settings.OPENAI_API_KEY)
            self.model = settings.OPENAI_MODEL
            logger.info(f"Initialized OpenAI client with model {self.model}")
        except Exception as e:
            logger.error(f"Failed to initialize OpenAI: {str(e)}")
            raise

    def _init_anthropic(self):
        """Initialize Anthropic client."""
        try:
            from anthropic import Anthropic
            self.client = Anthropic(api_key=settings.ANTHROPIC_API_KEY)
            self.model = settings.ANTHROPIC_MODEL
            logger.info(f"Initialized Anthropic client with model {self.model}")
        except Exception as e:
            logger.error(f"Failed to initialize Anthropic: {str(e)}")
            raise

    def generate_response(self, prompt: str, system_prompt: Optional[str] = None, temperature: float = 0.7) -> str:
        """
        Generate response from LLM.

        Args:
            prompt: User prompt
            system_prompt: System prompt (optional)
            temperature: Temperature for generation

        Returns:
            Generated text response
        """
        try:
            if self.provider == 'openai':
                return self._generate_openai(prompt, system_prompt, temperature)
            else:
                return self._generate_anthropic(prompt, system_prompt, temperature)

        except Exception as e:
            logger.error(f"Error generating response: {str(e)}")
            return f"Error: Unable to generate response - {str(e)}"

    def _generate_openai(self, prompt: str, system_prompt: Optional[str], temperature: float) -> str:
        """Generate response using OpenAI."""
        messages = []

        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})

        messages.append({"role": "user", "content": prompt})

        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=temperature,
            max_tokens=1500
        )

        return response.choices[0].message.content

    def _generate_anthropic(self, prompt: str, system_prompt: Optional[str], temperature: float) -> str:
        """Generate response using Anthropic."""
        kwargs = {
            "model": self.model,
            "max_tokens": 1500,
            "temperature": temperature,
            "messages": [{"role": "user", "content": prompt}]
        }

        if system_prompt:
            kwargs["system"] = system_prompt

        response = self.client.messages.create(**kwargs)

        return response.content[0].text


class GraphRAGGenerator:
    """Generates grounded responses using graph context and LLM."""

    def __init__(self, llm_client: LLMClient):
        """
        Initialize GraphRAG generator.

        Args:
            llm_client: LLM client instance
        """
        self.llm_client = llm_client

    def serialize_graph_context(self, query_result: Dict) -> str:
        """
        Serialize graph query results into context for LLM.

        Args:
            query_result: Query result from GraphRAG engine

        Returns:
            Serialized context string
        """
        intent = query_result.get('intent', 'unknown')
        results = query_result.get('results', [])

        if not results:
            return "No relevant data found in the knowledge graph."

        context_parts = [f"Query Intent: {intent}", f"Retrieved {len(results)} results from the knowledge graph:\n"]

        # Serialize results based on intent
        if intent == 'company_info':
            for item in results:
                context_parts.append(f"Company: {item.get('name', 'N/A')} ({item.get('symbol', 'N/A')})")
                context_parts.append(f"  Sector: {item.get('sector', 'N/A')}")
                context_parts.append(f"  Industry: {item.get('industry', 'N/A')}")
                if item.get('price'):
                    context_parts.append(f"  Current Price: ${item['price']:.2f}")
                if item.get('price_change_pct'):
                    context_parts.append(f"  Price Change: {item['price_change_pct']:.2f}%")
                if item.get('market_cap'):
                    context_parts.append(f"  Market Cap: ${item['market_cap']:,.0f}")

        elif intent == 'company_news':
            for item in results:
                context_parts.append(f"\nHeadline: {item.get('headline', 'N/A')}")
                context_parts.append(f"  Source: {item.get('source', 'N/A')}")
                context_parts.append(f"  Published: {item.get('published_at', 'N/A')}")
                context_parts.append(f"  Sentiment: {item.get('sentiment', 'neutral')}")
                if item.get('summary'):
                    context_parts.append(f"  Summary: {item['summary']}")

        elif intent == 'company_events':
            for item in results:
                context_parts.append(f"\nEvent Type: {item.get('event_type', 'N/A')}")
                context_parts.append(f"  Description: {item.get('description', 'N/A')}")
                context_parts.append(f"  Timestamp: {item.get('timestamp', 'N/A')}")
                context_parts.append(f"  Impact: {item.get('impact', 'N/A')}")

        elif intent == 'sentiment_analysis':
            for item in results:
                context_parts.append(f"\nCompany: {item.get('company_name', 'N/A')}")
                context_parts.append(f"  Sentiment: {item.get('sentiment', 'N/A')}")
                context_parts.append(f"  Article Count: {item.get('count', 0)}")
                if item.get('avg_score'):
                    context_parts.append(f"  Average Score: {item['avg_score']:.2f}")

        elif intent == 'market_overview':
            for item in results:
                context_parts.append(f"\nSector: {item.get('sector', 'N/A')}")
                context_parts.append(f"  Companies: {item.get('company_count', 0)}")
                if item.get('avg_change'):
                    context_parts.append(f"  Average Change: {item['avg_change']:.2f}%")
                if item.get('total_market_cap'):
                    context_parts.append(f"  Total Market Cap: ${item['total_market_cap']:,.0f}")

        else:
            # Generic serialization
            context_parts.append(json.dumps(results, indent=2, default=str))

        return "\n".join(context_parts)

    def generate_grounded_response(self, query: str, query_result: Dict) -> Dict:
        """
        Generate a grounded response based on graph query results.

        Args:
            query: Original user query
            query_result: Query result from GraphRAG engine

        Returns:
            Dictionary with response and metadata
        """
        # Serialize graph context
        graph_context = self.serialize_graph_context(query_result)

        # Create system prompt
        system_prompt = """You are a financial intelligence assistant powered by a knowledge graph.
Your responses must be grounded in the provided graph data. Follow these guidelines:

1. ONLY use information from the provided graph context
2. If the data is insufficient, acknowledge the limitation
3. Provide clear, concise, and actionable insights
4. Always cite specific data points (prices, percentages, dates)
5. Explain your reasoning transparently
6. Highlight important trends or patterns
7. Use professional financial terminology
8. Format numbers appropriately (e.g., $1.5B, 3.2%)

DO NOT hallucinate or make up information not present in the graph context."""

        # Create user prompt
        user_prompt = f"""User Query: {query}

Graph Context (Retrieved from Knowledge Graph):
{graph_context}

Based ONLY on the above graph context, provide a comprehensive and accurate answer to the user's query.
If the graph context doesn't contain enough information, clearly state what's missing."""

        # Generate response with fallback
        try:
            response_text = self.llm_client.generate_response(
                prompt=user_prompt,
                system_prompt=system_prompt,
                temperature=0.3  # Lower temperature for more factual responses
            )

            # Check if response contains error
            if response_text.startswith("Error:"):
                raise Exception("LLM unavailable")

        except Exception as e:
            # Fallback: Return formatted graph context without LLM
            logger.warning(f"LLM unavailable, using fallback formatting: {str(e)}")
            response_text = f"**⚠️ AI Assistant Unavailable - Showing Raw Graph Data**\n\n{graph_context}\n\n*Note: The Claude API key appears to be invalid. To enable AI-powered responses, please obtain a valid Anthropic API key from https://console.anthropic.com/*"

        return {
            'query': query,
            'intent': query_result.get('intent'),
            'response': response_text,
            'graph_context': graph_context,
            'num_results': query_result.get('num_results', 0),
            'cypher_query': query_result.get('cypher_query', '')
        }


if __name__ == "__main__":
    # Test the LLM integration
    logging.basicConfig(level=logging.INFO)

    try:
        llm_client = LLMClient()
        generator = GraphRAGGenerator(llm_client)

        # Test with mock data
        mock_query_result = {
            'intent': 'company_info',
            'results': [{
                'symbol': 'AAPL',
                'name': 'Apple Inc.',
                'sector': 'Technology',
                'price': 175.43,
                'price_change_pct': 2.3,
                'market_cap': 2700000000000
            }],
            'num_results': 1
        }

        print("Testing LLM Integration...")
        response = generator.generate_grounded_response(
            "Tell me about Apple's stock",
            mock_query_result
        )

        print(f"\nQuery: {response['query']}")
        print(f"\nResponse:\n{response['response']}")

    except Exception as e:
        print(f"Error: {e}")
        print("\nMake sure you have set up your LLM API keys in .env file")
