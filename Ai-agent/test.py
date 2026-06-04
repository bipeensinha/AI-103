from azure.ai.projects import AIProjectClient
from azure.identity import AzureCliCredential

project = AIProjectClient(
    credential=AzureCliCredential(),
    endpoint="https://project61143095-resource.services.ai.azure.com/api/projects/project61143095"
)

agents = project.agents.list()

print("Agents:", [a.id for a in agents])