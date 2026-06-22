import os
import asyncio
import json

from dotenv import load_dotenv
from contextlib import AsyncExitStack

from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient
from azure.ai.projects.models import (
    PromptAgentDefinition,
    FunctionTool,
)

from openai.types.responses.response_input_param import (
    FunctionCallOutput,
    ResponseInputParam,
)

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


# Clear console
os.system("cls" if os.name == "nt" else "clear")

# Load environment variables
load_dotenv()

project_endpoint = os.getenv("PROJECT_ENDPOINT")
model_deployment = os.getenv("MODEL_DEPLOYMENT_NAME")


async def connect_to_server(exit_stack: AsyncExitStack):

    server_params = StdioServerParameters(
        command="python",
        args=["server.py"],
        env=None,
    )

    # Start MCP server
    stdio_transport = await exit_stack.enter_async_context(
        stdio_client(server_params)
    )

    stdio, write = stdio_transport

    # Create session
    session = await exit_stack.enter_async_context(
        ClientSession(stdio, write)
    )

    await session.initialize()

    response = await session.list_tools()

    print(
        "\nConnected to server with tools:",
        [tool.name for tool in response.tools],
    )

    return session


def make_tool_func(session, tool_name):

    async def tool_func(**kwargs):
        result = await session.call_tool(tool_name, kwargs)
        return result

    tool_func.__name__ = tool_name
    return tool_func


async def chat_loop(session):

    with (
        DefaultAzureCredential() as credential,
        AIProjectClient(
            endpoint=project_endpoint,
            credential=credential,
        ) as project_client,
        project_client.get_openai_client() as openai_client,
    ):

        # Get MCP tools
        response = await session.list_tools()
        tools = response.tools

        # Build tool dictionary
        functions_dict = {
            tool.name: make_tool_func(session, tool.name)
            for tool in tools
        }

        # Convert MCP tools to FunctionTool definitions
        mcp_function_tools = []

        for tool in tools:

            function_tool = FunctionTool(
                name=tool.name,
                description=tool.description,
                parameters={
                    "type": "object",
                    "properties": {},
                    "additionalProperties": False,
                },
                strict=True,
            )

            mcp_function_tools.append(function_tool)

        # Create Agent
        agent = project_client.agents.create_version(
            agent_name="inventory-agent",
            definition=PromptAgentDefinition(
                model=model_deployment,
                instructions="""
You are an inventory assistant.

Guidelines:
- Recommend restock if inventory < 10 and weekly sales > 15
- Recommend clearance if inventory > 20 and weekly sales < 5
""",
                tools=mcp_function_tools,
            ),
        )

        print(
            f"Agent created: {agent.name} "
            f"(version {agent.version})"
        )

        # Create conversation
        conversation = openai_client.conversations.create()

        while True:

            user_input = input(
                "\nEnter a prompt "
                "(type 'quit' to exit)\nUSER: "
            ).strip()

            if user_input.lower() == "quit":
                break

            input_list: ResponseInputParam = []

            # Send user message
            openai_client.conversations.items.create(
                conversation_id=conversation.id,
                items=[
                    {
                        "type": "message",
                        "role": "user",
                        "content": user_input,
                    }
                ],
            )

            # Ask Agent
            response = openai_client.responses.create(
                conversation=conversation.id,
                input=input_list,
                extra_body={
                    "agent_reference": {
                        "name": agent.name,
                        "type": "agent_reference",
                    }
                },
            )

            if response.status == "failed":
                print(f"Failed: {response.error}")
                continue

            # Handle function calls
            for item in response.output:

                if item.type == "function_call":

                    function_name = item.name

                    kwargs = json.loads(item.arguments)

                    required_function = functions_dict.get(
                        function_name
                    )

                    if required_function:

                        output = await required_function(
                            **kwargs
                        )

                        input_list.append(
                            FunctionCallOutput(
                                type="function_call_output",
                                call_id=item.call_id,
                                output=output.content[0].text,
                            )
                        )

            # Send tool results back
            if input_list:

                response = openai_client.responses.create(
                    input=input_list,
                    previous_response_id=response.id,
                    extra_body={
                        "agent_reference": {
                            "name": agent.name,
                            "type": "agent_reference",
                        }
                    },
                )

            print(
                "\nAgent Response:\n",
                response.output_text,
            )

        # Cleanup
        print("\nCleaning up...")

        project_client.agents.delete_version(
            agent_name=agent.name,
            agent_version=agent.version,
        )

        print("Inventory agent deleted.")


async def main():

    exit_stack = AsyncExitStack()

    try:
        session = await connect_to_server(exit_stack)
        await chat_loop(session)

    finally:
        await exit_stack.aclose()


if __name__ == "__main__":
    asyncio.run(main())