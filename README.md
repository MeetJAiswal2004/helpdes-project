# Customer Helpdesk Support Assistant

A customer support chatbot that combines RAG, LangChain, an LLM (Groq), a SQL database (MySQL), and MCP (Model Context Protocol) into a single working project. Customers can ask policy related questions, view their own orders and profile, and raise support tickets, all through a chat interface.

## Project Structure

```
helpdesk-project/
├── backend/
│   ├── agent.py            LangChain agent, connects to the MCP server and the LLM
│   ├── api.py               FastAPI backend, exposes /login and /chat endpoints
│   ├── db_connection.py     Reusable MySQL connection function
│   ├── rag_setup.py         One time script to build the vector store from PDFs
│   ├── seed_fake_data.py    One time script to populate MySQL with fake data
│   └── chroma_db/           Generated vector store (created by rag_setup.py)
├── mcp_server/
│   ├── server.py            MCP server, exposes RAG and SQL functions as tools
│   └── sql_tools.py         Read and write functions for orders, profile, tickets
├── data/
│   └── pdfs/                Source PDF documents used for RAG
├── frontend/                React chat interface
├── .env.example              Template for required environment variables
├── requirements.txt
└── README.md
```

## Requirements

- Python 3.10 or later
- Node.js and npm
- MySQL Server, with MySQL Workbench or a similar client
- A free Groq API key (https://console.groq.com)

## Setup

### 1. Clone the repository and create a virtual environment

```
git clone <repository-url>
cd helpdesk-project
python -m venv myenv
myenv\Scripts\activate
```

### 2. Install Python dependencies

```
pip install -r requirements.txt
```

### 3. Install frontend dependencies

```
cd frontend
npm install
cd ..
```

### 4. Set up the MySQL database

Open MySQL Workbench and run the following to create the database and tables:

```sql
CREATE DATABASE IF NOT EXISTS helpdesk_db;
USE helpdesk_db;

CREATE TABLE customers (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100) NOT NULL,
    phone VARCHAR(50)
);

CREATE TABLE orders (
    id INT AUTO_INCREMENT PRIMARY KEY,
    customer_id INT,
    product VARCHAR(100),
    status VARCHAR(50) DEFAULT 'pending',
    order_date DATE,
    FOREIGN KEY (customer_id) REFERENCES customers(id)
);

CREATE TABLE support_tickets (
    id INT AUTO_INCREMENT PRIMARY KEY,
    customer_id INT,
    issue TEXT,
    status VARCHAR(50) DEFAULT 'open',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (customer_id) REFERENCES customers(id)
);
```

### 5. Create the .env file

Copy .env.example to a new file named .env, and fill in your actual values:

```
DB_HOST=127.0.0.1
DB_PORT=3306
DB_USER=root
DB_PASSWORD=your_mysql_password
DB_NAME=helpdesk_db
GROQ_API_KEY=your_groq_api_key
```

LangSmith tracing variables are optional and only needed if you want to monitor request latency and tool calls:

```
LANGCHAIN_TRACING_V2=true
LANGCHAIN_API_KEY=your_langsmith_api_key
LANGCHAIN_PROJECT=techmart-helpdesk
```

### 6. Populate the database with sample data

```
python -m backend.seed_fake_data
```

This creates 50 customers, 100 orders, and 40 support tickets with fake data, so the project can be tested without real customer data.

### 7. Build the RAG vector store

Place the source PDF files inside data/pdfs, then run:

```
python -m backend.rag_setup
```

This reads the PDFs, splits them into chunks, generates embeddings, and saves them to backend/chroma_db. This only needs to be run once, or again if the PDFs change.

## Running the Project

The project has three parts that need to run at the same time, each in its own terminal. Start them in this order.

### Terminal 1: MCP server

```
python -m mcp_server.server
```

Wait until it shows it is running on http://127.0.0.1:8001 before starting the next step.

### Terminal 2: Backend API

```
uvicorn backend.api:app --reload --port 8000
```

### Terminal 3: Frontend

```
cd frontend
npm run dev
```

Open the URL shown in the terminal, usually http://localhost:5173.

## Using the Application

1. Enter a registered customer email on the login screen. Sample emails can be found by checking the customers table in MySQL after running the seed script.
2. Once logged in, ask questions such as return policy questions, warranty questions, or requests to view orders or profile details.
3. To report an issue, ask the assistant to raise a support ticket.
4. The session stays active across page reloads until the Logout button, in the top left of the chat window, is clicked.

