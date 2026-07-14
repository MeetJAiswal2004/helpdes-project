from mcp.server.fastmcp import FastMCP
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from .sql_tools import get_my_orders, get_my_profile, create_support_ticket, contains_harmful_keywords

# Load the same embedding model used in rag_setup.py, and point to the saved vector store
embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
vectorstore = Chroma(
    persist_directory="backend/chroma_db",
    embedding_function=embeddings
)

# This server exposes all our RAG and SQL functions as MCP tools
mcp = FastMCP("helpdesk-server", host="127.0.0.1", port=8001)

# RAG tool: lets the agent search across all three policy PDFs
@mcp.tool()
def search_policy_docs(query: str) -> str:
    """
    Searches TechMart's return policy, warranty guide, and FAQ documents.
    Use this when the user asks a policy, warranty, or general support
    related question (e.g., 'how many days for a return').
    """
    if contains_harmful_keywords(query):
        return "Your query contains restricted keywords. Please rephrase your query."

    results = vectorstore.similarity_search(query, k=3)
    combined_text = "\n\n---\n\n".join([doc.page_content for doc in results])
    return combined_text


# Read tool: wraps get_my_orders so the agent can call it as a tool
@mcp.tool()
def get_orders(customer_id: int) -> list:
    """
    Returns all orders (product, status, date) belonging to the customer.
    Only returns the customer's own data — customer_id comes from the
    active session, never from user-provided text.
    """
    return get_my_orders(customer_id)


# Read tool: wraps get_my_profile so the agent can call it as a tool
@mcp.tool()
def get_profile(customer_id: int) -> dict:
    """
    Returns the customer's own profile details (name, email, phone).
    """
    return get_my_profile(customer_id)


# Write tool: the only tool in the whole server that can add data to the database
@mcp.tool()
def raise_ticket(customer_id: int, issue: str) -> dict:
    """
    Creates a new support ticket when the customer reports a complaint
    or issue. This is the only WRITE operation available — there is no
    tool to modify or delete orders or profile data.
    """
    return create_support_ticket(customer_id, issue)

# Starts the server and listens for a client (our LangChain agent) over stdio
if __name__ == "__main__":
    mcp.run(transport="streamable-http")