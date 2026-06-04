from azure.ai.textanalytics import TextAnalyticsClient
from azure.core.credentials import AzureKeyCredential

def get_client(endpoint, key):
    return TextAnalyticsClient(endpoint=endpoint, credential=AzureKeyCredential(key))


def analyze_sentiment(client, text):
    result = client.analyze_sentiment([text])[0]
    return result.sentiment, result.confidence_scores


def extract_entities(client, text):
    result = client.recognize_entities([text])[0]
    return [(e.text, e.category) for e in result.entities]


def extract_key_phrases(client, text):
    result = client.extract_key_phrases([text])[0]
    return result.key_phrases