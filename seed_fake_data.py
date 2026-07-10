from dotenv import load_dotenv
from faker import Faker
import mysql.connector
import os
import random

load_dotenv()
fake = Faker()

conn = mysql.connector.connect(
    host=os.getenv("DB_HOST"),
    port=os.getenv("DB_PORT"),
    user=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD"),
    database=os.getenv("DB_NAME")
)
cursor = conn.cursor()

# 1. Customers table
customer_ids = []
for _ in range(50):
    cursor.execute(
        "INSERT INTO customers (name, email, phone) VALUES (%s, %s, %s)",
        (fake.name(), fake.email(), fake.phone_number())
    )
    customer_ids.append(cursor.lastrowid)   

conn.commit()
print(f"{len(customer_ids)} customers inserted!")

# 2. Orders table 
products = ["Laptop", "Headphones", "Keyboard", "Monitor", "Mouse", "Webcam", "Charger"]
statuses = ["pending", "shipped", "delivered", "cancelled"]

for _ in range(100):
    cursor.execute(
        "INSERT INTO orders (customer_id, product, status, order_date) VALUES (%s, %s, %s, %s)",
        (
            random.choice(customer_ids),      
            random.choice(products),
            random.choice(statuses),
            fake.date_between(start_date="-1y", end_date="today")
        )
    )

conn.commit()
print("100 orders inserted!")

# 3. Support tickets table 
issues = [
    "Product not working",
    "Wrong item delivered",
    "Refund not received",
    "Delivery delayed",
    "Need installation help",
    "Item damaged in transit"
]
ticket_statuses = ["open", "in_progress", "closed"]

for _ in range(40):
    cursor.execute(
        "INSERT INTO support_tickets (customer_id, issue, status) VALUES (%s, %s, %s)",
        (
            random.choice(customer_ids),
            random.choice(issues),
            random.choice(ticket_statuses)
        )
    )

conn.commit()
print("40 support tickets inserted!")

cursor.close()
conn.close()
print("All fake data inserted successfully!")