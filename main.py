import asyncio
from db_connection import get_connection
from agent import build_agent


# Looks up a customer by email, this is our simple stand-in for a real login system
def identify_customer(email: str):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT id, name FROM customers WHERE email = %s", (email,))
    result = cursor.fetchone()
    cursor.close()
    conn.close()
    return result

async def main():
    print("=== Welcome to TechMart customer Support ===\n")

    # Keep asking for an email until it matches a real customer
    customer = None
    while not customer:
        email = input("Please enter your registered email: ")
        customer = identify_customer(email)
        if not customer:
            print("Email not found. Please try again.\n")

    # Lock the customer_id for the rest of this session, this is what keeps
    # every tool call scoped to this one customer's data
    customer_id = customer["id"]
    customer_name = customer["name"]

    print(f"\nHello {customer_name}! How can I help you today?")
    print("(Type 'exit' to quit)\n")

    agent = await build_agent()

    while True:
        user_input = input("You: ")
        if user_input.lower() == "exit":
            print("Thank you for contacting TechMart Support!")
            break
        
        # Inject customer_id into every message so the agent never has to ask for it, and the user can never override whose data it queries
        full_query = f"[customer_id={customer_id}] {user_input}"
        response = await agent.ainvoke({"messages": [{"role": "user", "content": full_query}]})
        final_message = response["messages"][-1].content
        print(f"Bot: {final_message}\n")

if __name__ == "__main__":
    asyncio.run(main()) # asyncio.run() starts the event loop needed to run our async main() function.