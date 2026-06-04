from azure.ai.projects import AIProjectClient
from azure.identity import AzureCliCredential
from azure.ai.agents.models import ListSortOrder

# ✅ FORCE CLI AUTH (VERY IMPORTANT)
project = AIProjectClient(
    credential=AzureCliCredential(),
    endpoint="https://project61143095-resource.services.ai.azure.com/api/projects/project61143095"
)

# 🔍 DEBUG – confirm agents are visible
agents = project.agents.list()
print("AVAILABLE AGENTS:")
for a in agents:
    print(a.id)

# ✅ GET AGENT
agent = project.agents.get("asst_GmALIlkyAm6418pFRhUyzQZR")

# ✅ CREATE THREAD
thread = project.agents.threads.create()
print(f"Created thread, ID: {thread.id}")

# ✅ SEND MESSAGE
message = project.agents.messages.create(
    thread_id=thread.id,
    role="user",
    content="Hi expense-agent"
)

# ✅ RUN AGENT
run = project.agents.runs.create_and_process(
    thread_id=thread.id,
    agent_id=agent.id
)

# ✅ HANDLE RESPONSE
if run.status == "failed":
    print(f"Run failed: {run.last_error}")
else:
    messages = project.agents.messages.list(
        thread_id=thread.id,
        order=ListSortOrder.ASCENDING
    )

    for msg in messages:
        if msg.text_messages:
            print(f"{msg.role}: {msg.text_messages[-1].text.value}")