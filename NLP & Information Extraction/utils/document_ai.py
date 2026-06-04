from azure.ai.formrecognizer import DocumentAnalysisClient
from azure.core.credentials import AzureKeyCredential

def get_doc_client(endpoint, key):
    return DocumentAnalysisClient(endpoint=endpoint, credential=AzureKeyCredential(key))


def analyze_invoice(client, file_url):
    poller = client.begin_analyze_document("prebuilt-invoice", document_url=file_url)
    result = poller.result()

    extracted_data = {}

    for doc in result.documents:
        for name, field in doc.fields.items():
            extracted_data[name] = field.value

    return extracted_data