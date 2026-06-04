from dotenv import load_dotenv
import os

from utils.text_analysis import get_client, analyze_sentiment, extract_entities, extract_key_phrases
from utils.document_ai import get_doc_client, analyze_invoice

load_dotenv()

# Load ENV
TEXT_KEY = os.getenv("TEXT_ANALYTICS_KEY")
TEXT_ENDPOINT = os.getenv("TEXT_ANALYTICS_ENDPOINT")

FORM_KEY = os.getenv("FORM_RECOGNIZER_KEY")
FORM_ENDPOINT = os.getenv("FORM_RECOGNIZER_ENDPOINT")

# Initialize clients
text_client = get_client(TEXT_ENDPOINT, TEXT_KEY)
doc_client = get_doc_client(FORM_ENDPOINT, FORM_KEY)

# Sample text
text = "Microsoft shipped an invoice of $5000 to Bangalore. Great service!"

# NLP Tasks
sentiment, score = analyze_sentiment(text_client, text)
entities = extract_entities(text_client, text)
phrases = extract_key_phrases(text_client, text)

print("\n--- NLP OUTPUT ---")
print("Sentiment:", sentiment)
print("Entities:", entities)
print("Key Phrases:", phrases)

# Document AI
invoice_url = "https://example.com/sample-invoice.pdf"

invoice_data = analyze_invoice(doc_client, invoice_url)

print("\n--- DOCUMENT AI OUTPUT ---")
for k, v in invoice_data.items():
    print(f"{k}: {v}")