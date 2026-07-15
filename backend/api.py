from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from .db_connection import get_connection
from .agent import build_agent
import asyncio 

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)

agent = None

class LoginRequest(BaseModel):
    email: str

class ChatRequest(BaseModel):
    customer_id: int
    message: str

@app.on_event("startup")
async def startup():
    global agent
    agent = await build_agent()

def identify_customer(email: str):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT id, name FROM customers WHERE email = %s", (email,))
    result = cursor.fetchone()
    cursor.close()
    conn.close()
    return result

@app.post("/login")
def login(req: LoginRequest):
    customer = identify_customer(req.email)
    if not customer:
        return {"success": False, "message": "Email not found"}
    return {"success": True, "customer_id": customer["id"], "name": customer["name"]}

@app.post("/chat")
async def chat(req: ChatRequest):
    full_query = f"[customer_id={req.customer_id}] {req.message}"
    try:
        response = await asyncio.wait_for(
            agent.ainvoke(
                {"messages": [{"role": "user", "content": full_query}]},
                config={"recursion_limit": 6}
            ),
            timeout=30
        )
        reply = response["messages"][-1].content
    except asyncio.TimeoutError:
        reply = "Sorry, that took too long to process. Could you rephrase your question?"
    except Exception:
        reply = "Sorry, I had trouble processing that. Please try again."
    return {"reply": reply}