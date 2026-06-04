import os
from openai import AzureOpenAI
from dotenv import load_dotenv

# Load env
load_dotenv()

client = AzureOpenAI(
    api_version="2024-12-01-preview",
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
    api_key=os.getenv("AZURE_OPENAI_KEY")
)

# Conversation memory
messages = [
    {"role": "system", "content": "You are a helpful assistant."}
]

print("💬 Chat started! Type 'exit' to quit.\n")

while True:
    user_input = input("You: ")

    if user_input.lower() == "exit":
        print("👋 Goodbye!")
        break

    messages.append({"role": "user", "content": user_input})

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=messages,
        max_tokens=200
    )

    reply = response.choices[0].message.content
    print("AI:", reply, "\n")

    messages.append({"role": "assistant", "content": reply})