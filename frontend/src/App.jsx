import { useState, useRef, useEffect } from "react";
import ReactMarkdown from "react-markdown";
import "./App.css";

const API_URL = "http://localhost:8000";

export default function App() {
  const [customerId, setCustomerId] = useState(null);
  const [name, setName] = useState("");
  const [checkingSession, setCheckingSession] = useState(true);

  // Check for an existing session in localStorage on first load
  useEffect(() => {
    const savedId = localStorage.getItem("customer_id");
    const savedName = localStorage.getItem("customer_name");
    if (savedId && savedName) {
      setCustomerId(Number(savedId));
      setName(savedName);
    }
    setCheckingSession(false);
  }, []);

  const handleLoginSuccess = (id, customerName) => {
    localStorage.setItem("customer_id", id);
    localStorage.setItem("customer_name", customerName);
    setCustomerId(id);
    setName(customerName);
  };

  const handleLogout = () => {
    localStorage.removeItem("customer_id");
    localStorage.removeItem("customer_name");
    setCustomerId(null);
    setName("");
  };

  if (checkingSession) {
    return null; // avoid a flash of the login screen while checking localStorage
  }

  if (!customerId) {
    return <LoginScreen onSuccess={handleLoginSuccess} />;
  }

  return <ChatScreen name={name} customerId={customerId} onLogout={handleLogout} />;
}

// ---------- Login screen ----------
function LoginScreen({ onSuccess }) {
  const [email, setEmail] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault(); // Prevent form submission from reloading the page
    if (!email.trim()) return;
    setLoading(true);
    setError("");

    try {
      const res = await fetch(`${API_URL}/login`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email }),
      });
      const data = await res.json();
      if (data.success) {
        onSuccess(data.customer_id, data.name);
      } else {
        setError(data.message || "Email not found. Please try again.");
      }
    } catch (err) {
      setError("Failed to connect to the server. Please try again later.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="page">
      <div className="login-box">
        <div className="login-header">
          <svg xmlns="http://www.w3.org/2000/svg" width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="login-icon"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"></path></svg>
          <h2>TechMart Support</h2>
        </div>
        <p className="subtitle">Sign in with your registered email</p>
        <form onSubmit={handleSubmit}>
          <input value={email} onChange={(e) => setEmail(e.target.value)} placeholder="you@example.com" className="input" type="email" required />
          {error && <p className="error-text">{error}</p>}
          <button type="submit" disabled={loading} className="button full-width">
            {loading ? "Signing In..." : "Sign In"}
          </button>
        </form>
      </div>
    </div>
  );
}

// ---------- Chat screen ----------
function ChatScreen({ name, customerId, onLogout }) {
  const [messages, setMessages] = useState([
    { role: "bot", text: `Hello ${name}! How can I help you today?` },
  ]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const bottomRef = useRef(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const addMessage = (role, text) => {
    setMessages((prev) => [...prev, { role, text }]);
  };

  const handleSend = async () => {
    if (!input.trim() || loading) return;
    const text = input.trim();
    addMessage("user", text);
    setInput("");
    setLoading(true);

    const res = await fetch(`${API_URL}/chat`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ customer_id: customerId, message: text }),
    });
    const data = await res.json();
    setLoading(false);
    addMessage("bot", data.reply);
  };

  return (
    <div className="page">
      <div className="chat-box">
        <div className="header">
          <button onClick={onLogout} className="logout-button">Logout</button>
          <span>TechMart Support</span>
          <span className="spacer" />
        </div>

        <div className="messages">
          {messages.map((m, i) => (
            <div key={i} className={`row ${m.role === "user" ? "row-user" : "row-bot"}`}>
              <div className={m.role === "user" ? "bubble bubble-user" : "bubble bubble-bot"}>
                {m.role === "bot" ? <ReactMarkdown>{m.text}</ReactMarkdown> : m.text}
              </div>
            </div>
          ))}
          {loading && (
            <div className="row row-bot">
              <div className="bubble bubble-bot">Typing...</div>
            </div>
          )}
          <div ref={bottomRef} />
        </div>

        <div className="input-row">
          <input
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && handleSend()}
            placeholder="Type your message..."
            className="input"
          />
          <button onClick={handleSend} className="button">Send</button>
        </div>
      </div>
    </div>
  );
}