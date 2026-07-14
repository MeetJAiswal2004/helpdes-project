import asyncio
import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_mcp_adapters.client import MultiServerMCPClient
from langgraph.prebuilt import create_react_agent

load_dotenv()

#LLM setup with model name and API key from .env file
llm = ChatGroq(
    model="llama-3.3-70b-versatile",
    api_key=os.getenv("GROQ_API_KEY")
)

# System prompt: defines what the agent can and cannot do and behave as is
SYSTEM_PROMPT = """
You are TechMart's customer support assistant.

You can:
- Search policy documents (return policy, warranty, FAQ) to answer questions
- Show the customer their own orders
- Show the customer their own profile details
- Create a new support ticket when the customer reports an issue

You CANNOT and MUST NEVER:
- Delete, modify, or update any order, profile, or customer data
- Claim to have performed an action that no tool exists for

If the customer asks you to delete or modify their data, politely explain
that this isn't possible, and offer to raise a support ticket instead.

Always use the customer_id provided in the conversation context for any
tool that requires it. Never ask the customer for their customer_id directly.

Formatting rules for your responses:
- When listing multiple items (orders, tickets, profile fields), use a
  markdown bullet list with a line break before each item, not one long sentence.
- Use **bold** for field labels (e.g. **Order ID:**, **Status:**).
- Keep each item on its own line.
- Keep responses concise and easy to scan.
"""

# agent builder function that connects to the MCP server and retrieves the tools, then creates a React agent with the LLM and tools
async def build_agent():
    client = MultiServerMCPClient({
        "helpdesk": {
            "url": "http://127.0.0.1:8001/mcp",
            "transport": "streamable_http"
        }
    })

    tools = await client.get_tools()
    agent = create_react_agent(llm, tools, prompt=SYSTEM_PROMPT)
    return agent

