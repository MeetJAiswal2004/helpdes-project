from backend.db_connection import get_connection

# Read-only function: returns every order that belongs to this customer
def get_my_orders(customer_id: int):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)   
    cursor.execute(
        "SELECT id, product, status, order_date FROM orders WHERE customer_id = %s",
        (customer_id,)
    )
    results = cursor.fetchall()
    cursor.close()
    conn.close()
    if not results:
        return {"message": "No orders found for this customer."}
    return results

# Read-only function: returns this customer's own profile details
def get_my_profile(customer_id: int):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute(
        "SELECT id, name, email, phone FROM customers WHERE id = %s",
        (customer_id,)
    )
    result = cursor.fetchone()
    cursor.close()
    conn.close()
    if not result:
        return {"message": "Customer profile not found."}
    return result


# The only write operation in the whole project: raising a support ticket
def create_support_ticket(customer_id: int, issue: str):
    # Reject anything that looks like an attempt to inject raw SQL before it touches the DB
    if contains_harmful_keywords(issue):
        return {"error": "Your message contains restricted keywords. Please redescribe your query"}

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO support_tickets (customer_id, issue, status) VALUES (%s, %s, 'open')",
        (customer_id, issue)
    )
    conn.commit()
    ticket_id = cursor.lastrowid
    cursor.close()
    conn.close()
    return {"ticket_id": ticket_id, "message": "Ticket created successfully"}

# Basic keyword blocklist, catches obvious attempts to slip SQL commands through free text
BLOCKED_KEYWORDS = ["delete", "drop", "truncate", "alter", "update", "insert into", "exec", "--", ";"]
def contains_harmful_keywords(text: str) -> bool:
    lowered = text.lower()
    return any(keyword in lowered for keyword in BLOCKED_KEYWORDS)
