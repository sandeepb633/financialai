"""Entity extraction using spaCy and FinBERT for financial text."""

import spacy
from transformers import AutoTokenizer, AutoModelForSequenceClassification, pipeline
import torch
from typing import Dict, List, Tuple
import logging
import re

logger = logging.getLogger(__name__)


class EntityExtractor:
    """Extracts entities and performs sentiment analysis on financial text."""

    def __init__(self, llm_client=None):
        """Initialize entity extractor with spaCy and FinBERT.

        Args:
            llm_client: Optional LLM client for enhanced entity extraction
        """
        self.llm_client = llm_client

        # Load spaCy model for NER
        try:
            self.nlp = spacy.load("en_core_web_sm")
        except OSError:
            logger.warning("spaCy model not found. Run: python -m spacy download en_core_web_sm")
            self.nlp = None

        # Load FinBERT for sentiment analysis
        try:
            self.sentiment_model = pipeline(
                "sentiment-analysis",
                model="ProsusAI/finbert",
                tokenizer="ProsusAI/finbert"
            )
        except Exception as e:
            logger.warning(f"FinBERT not loaded: {e}. Sentiment analysis will be disabled.")
            self.sentiment_model = None

    def extract_entities(self, text: str) -> List[Dict]:
        """
        Extract named entities from text.

        Args:
            text: Input text

        Returns:
            List of entity dictionaries with text, label, and position
        """
        if not self.nlp:
            return []

        doc = self.nlp(text)
        entities = []

        for ent in doc.ents:
            entities.append({
                'text': ent.text,
                'label': ent.label_,
                'start': ent.start_char,
                'end': ent.end_char
            })

        return entities

    def extract_organizations(self, text: str) -> List[str]:
        """
        Extract organization names from text.

        Args:
            text: Input text

        Returns:
            List of organization names
        """
        entities = self.extract_entities(text)
        orgs = [e['text'] for e in entities if e['label'] == 'ORG']
        return list(set(orgs))  # Remove duplicates

    def extract_financial_entities(self, text: str) -> Dict[str, List[str]]:
        """
        Extract financial-specific entities with LLM enhancement.

        Args:
            text: Input text

        Returns:
            Dictionary with categorized entities
        """
        # Common company name to ticker mapping (expanded)
        company_mappings = {
            'apple': 'AAPL',
            'microsoft': 'MSFT',
            'google': 'GOOGL',
            'alphabet': 'GOOGL',
            'amazon': 'AMZN',
            'tesla': 'TSLA',
            'meta': 'META',
            'facebook': 'META',
            'nvidia': 'NVDA',
            'jpmorgan': 'JPM',
            'jp morgan': 'JPM',
            'chase': 'JPM',
            'visa': 'V',
            'walmart': 'WMT',
            'netflix': 'NFLX',
            'paypal': 'PYPL',
            'adobe': 'ADBE',
            'salesforce': 'CRM',
            'oracle': 'ORCL',
            'intel': 'INTC',
            'amd': 'AMD',
            'qualcomm': 'QCOM',
            'cisco': 'CSCO',
            'ibm': 'IBM',
            'twitter': 'TWTR',
            'uber': 'UBER',
            'lyft': 'LYFT',
            'airbnb': 'ABNB',
            'spotify': 'SPOT',
            'zoom': 'ZM',
            'slack': 'WORK',
            'docusign': 'DOCU',
            'snowflake': 'SNOW',
            'palantir': 'PLTR',
            'robinhood': 'HOOD',
            'coinbase': 'COIN',
        }

        # Try LLM-based extraction first if available
        if self.llm_client:
            try:
                llm_result = self._llm_extract_entities(text, company_mappings)
                if llm_result:
                    return llm_result
            except Exception as e:
                logger.warning(f"LLM entity extraction failed: {e}, falling back to rule-based")

        # Fall back to rule-based extraction
        return self._rule_based_extract_entities(text, company_mappings)

    def _llm_extract_entities(self, text: str, company_mappings: Dict) -> Dict[str, List[str]]:
        """
        Use LLM to extract entities with financial context understanding.

        Args:
            text: Input text
            company_mappings: Dictionary of company names to tickers

        Returns:
            Dictionary with categorized entities
        """
        if not self.llm_client:
            return None

        entity_prompt = f"""Extract financial entities from this query. Respond with ONLY a JSON object.

Query: "{text}"

Extract:
1. Company names and stock tickers (if mentioned)
2. Sector/industry names
3. Financial metrics or concepts mentioned

Return JSON format:
{{
    "tickers": ["AAPL", "MSFT"],
    "companies": ["Apple", "Microsoft"],
    "sectors": ["Technology"],
    "concepts": ["sentiment", "market cap", "price"]
}}

Known companies: {', '.join(company_mappings.keys())}

JSON:"""

        try:
            response = self.llm_client.generate_response(
                prompt=entity_prompt,
                temperature=0.1
            ).strip()

            # Extract JSON from response
            import json
            # Try to find JSON in the response
            json_start = response.find('{')
            json_end = response.rfind('}') + 1
            if json_start >= 0 and json_end > json_start:
                json_str = response[json_start:json_end]
                llm_entities = json.loads(json_str)

                # Merge with rule-based extraction for robustness
                rule_based = self._rule_based_extract_entities(text, company_mappings)

                # Combine results
                result = {
                    'tickers': list(set(llm_entities.get('tickers', []) + rule_based.get('tickers', []))),
                    'companies': list(set(llm_entities.get('companies', []) + rule_based.get('companies', []))),
                    'sectors': llm_entities.get('sectors', []),
                    'concepts': llm_entities.get('concepts', []),
                    'people': rule_based.get('people', []),
                    'locations': rule_based.get('locations', []),
                    'money': rule_based.get('money', []),
                    'percentages': rule_based.get('percentages', []),
                    'dates': rule_based.get('dates', [])
                }

                return result

        except Exception as e:
            logger.warning(f"Error in LLM entity extraction: {e}")

        return None

    def _rule_based_extract_entities(self, text: str, company_mappings: Dict) -> Dict[str, List[str]]:
        """
        Rule-based entity extraction (original method).

        Args:
            text: Input text
            company_mappings: Dictionary of company names to tickers

        Returns:
            Dictionary with categorized entities
        """
        entities = self.extract_entities(text)

        result = {
            'companies': [],
            'people': [],
            'locations': [],
            'money': [],
            'percentages': [],
            'dates': [],
            'sectors': [],
            'concepts': []
        }

        for ent in entities:
            if ent['label'] == 'ORG':
                result['companies'].append(ent['text'])
            elif ent['label'] == 'PERSON':
                result['people'].append(ent['text'])
            elif ent['label'] in ['GPE', 'LOC']:
                result['locations'].append(ent['text'])
            elif ent['label'] == 'MONEY':
                result['money'].append(ent['text'])
            elif ent['label'] == 'PERCENT':
                result['percentages'].append(ent['text'])
            elif ent['label'] == 'DATE':
                result['dates'].append(ent['text'])

        # Remove duplicates
        for key in result:
            result[key] = list(set(result[key]))

        # Extract stock tickers (e.g., $AAPL, AAPL)
        ticker_pattern = r'\$?[A-Z]{1,5}\b'
        tickers = re.findall(ticker_pattern, text)
        result['tickers'] = list(set([t.replace('$', '') for t in tickers]))

        # Extract company names from text using our mapping
        text_lower = text.lower()
        for company_name, ticker in company_mappings.items():
            if company_name in text_lower:
                if ticker not in result['tickers']:
                    result['tickers'].append(ticker)
                if company_name.title() not in result['companies']:
                    result['companies'].append(company_name.title())

        return result

    def analyze_sentiment(self, text: str) -> Dict:
        """
        Analyze sentiment of financial text using FinBERT.

        Args:
            text: Input text

        Returns:
            Dictionary with sentiment label and score
        """
        if not self.sentiment_model:
            return {'label': 'neutral', 'score': 0.0}

        try:
            # Truncate text if too long (FinBERT has 512 token limit)
            if len(text) > 512:
                text = text[:512]

            result = self.sentiment_model(text)[0]

            # Map FinBERT labels to simplified labels
            label_map = {
                'positive': 'positive',
                'negative': 'negative',
                'neutral': 'neutral'
            }

            return {
                'label': label_map.get(result['label'].lower(), 'neutral'),
                'score': float(result['score'])
            }

        except Exception as e:
            logger.error(f"Error analyzing sentiment: {str(e)}")
            return {'label': 'neutral', 'score': 0.0}

    def extract_events(self, text: str) -> List[Dict]:
        """
        Extract financial events from text.

        Args:
            text: Input text

        Returns:
            List of event dictionaries
        """
        # Event keywords
        event_keywords = {
            'earnings': ['earnings', 'profit', 'revenue', 'quarterly results', 'eps'],
            'merger': ['merger', 'acquisition', 'acquires', 'buys', 'takeover'],
            'ipo': ['ipo', 'initial public offering', 'goes public'],
            'dividend': ['dividend', 'payout', 'distribution'],
            'partnership': ['partnership', 'collaboration', 'alliance', 'joint venture'],
            'product_launch': ['launches', 'introduces', 'unveils', 'announces new'],
            'layoff': ['layoff', 'job cuts', 'workforce reduction'],
            'executive_change': ['ceo', 'cfo', 'resigns', 'appointed', 'steps down']
        }

        events = []
        text_lower = text.lower()

        for event_type, keywords in event_keywords.items():
            for keyword in keywords:
                if keyword in text_lower:
                    events.append({
                        'type': event_type,
                        'keyword': keyword,
                        'confidence': 0.8  # Basic confidence score
                    })
                    break  # Only add one event per type

        return events

    def process_news_article(self, article: Dict) -> Dict:
        """
        Process a news article to extract entities and sentiment.

        Args:
            article: Article dictionary with 'headline' and 'summary' or 'content'

        Returns:
            Enhanced article dictionary with extracted information
        """
        text = article.get('headline', '') + ' ' + article.get('summary', '') + ' ' + article.get('content', '')

        # Extract entities
        entities = self.extract_financial_entities(text)

        # Analyze sentiment
        sentiment = self.analyze_sentiment(text)

        # Extract events
        events = self.extract_events(text)

        # Add extracted information to article
        article['extracted'] = {
            'entities': entities,
            'sentiment': sentiment,
            'events': events
        }

        return article


if __name__ == "__main__":
    # Test the entity extractor
    logging.basicConfig(level=logging.INFO)

    extractor = EntityExtractor()

    test_text = """
    Apple Inc. (AAPL) reported strong quarterly earnings of $1.52 per share,
    beating analyst expectations. CEO Tim Cook announced a new partnership
    with Microsoft. The stock rose 5.2% to $175.43 in after-hours trading.
    """

    print("Testing Entity Extractor...")
    print(f"\nTest text: {test_text}\n")

    print("1. Extracted Entities:")
    entities = extractor.extract_financial_entities(test_text)
    for key, values in entities.items():
        if values:
            print(f"  {key}: {values}")

    print("\n2. Sentiment Analysis:")
    sentiment = extractor.analyze_sentiment(test_text)
    print(f"  Label: {sentiment['label']}")
    print(f"  Score: {sentiment['score']:.2f}")

    print("\n3. Extracted Events:")
    events = extractor.extract_events(test_text)
    for event in events:
        print(f"  Type: {event['type']}, Keyword: {event['keyword']}")
