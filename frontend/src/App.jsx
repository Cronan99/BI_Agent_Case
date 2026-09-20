import { useEffect, useState } from "react";
import "./App.css";

const API_URL = "http://localhost:8000";

const suggestedQuestions = [
  "How much did we sell during 2025?",
  "What were our top 5 products during 2025?",
  "How were sales distributed across regions in 2025?",
  "How did sales develop month by month during 2025?",
];

function App() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");

  const [token, setToken] = useState(() =>
    sessionStorage.getItem("access_token")
  );

  const [user, setUser] = useState(null);
  const [message, setMessage] = useState("");
  const [messages, setMessages] = useState([]);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const [loadingUser, setLoadingUser] = useState(Boolean(token));

  // Restore the logged-in user after a page refresh.
  useEffect(() => {
    if (!token) {
      setLoadingUser(false);
      return;
    }

    async function loadUser() {
      try {
        const response = await fetch(`${API_URL}/auth/me`, {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        });

        if (!response.ok) {
          throw new Error("Session expired");
        }

        const userData = await response.json();
        setUser(userData);
      } catch {
        sessionStorage.removeItem("access_token");
        setToken(null);
        setUser(null);
      } finally {
        setLoadingUser(false);
      }
    }

    loadUser();
  }, [token]);

  async function handleLogin(event) {
    event.preventDefault();

    setError("");
    setLoading(true);

    try {
      const response = await fetch(`${API_URL}/auth/login`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          email,
          password,
        }),
      });

      if (!response.ok) {
        throw new Error("Invalid email or password");
      }

      const data = await response.json();

      sessionStorage.setItem("access_token", data.access_token);
      setToken(data.access_token);

      const userResponse = await fetch(`${API_URL}/auth/me`, {
        headers: {
          Authorization: `Bearer ${data.access_token}`,
        },
      });

      if (!userResponse.ok) {
        throw new Error("Could not load user");
      }

      const userData = await userResponse.json();

      setUser(userData);
      setPassword("");
    } catch (err) {
      sessionStorage.removeItem("access_token");
      setToken(null);
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  async function sendMessage(text = message) {
    const trimmedMessage = text.trim();

    if (!trimmedMessage || loading) {
      return;
    }

    setMessages((current) => [
      ...current,
      {
        role: "user",
        content: trimmedMessage,
      },
    ]);

    setMessage("");
    setLoading(true);

    try {
      const response = await fetch(`${API_URL}/chat`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({
          message: trimmedMessage,
        }),
      });

      if (!response.ok) {
        throw new Error("Could not get an answer");
      }

      const data = await response.json();

      setMessages((current) => [
        ...current,
        {
          role: "assistant",
          content: data.answer,
        },
      ]);
    } catch {
      setMessages((current) => [
        ...current,
        {
          role: "assistant",
          content:
            "Something went wrong while retrieving the sales data. Please try again.",
        },
      ]);
    } finally {
      setLoading(false);
    }
  }

  function handleSubmit(event) {
    event.preventDefault();
    sendMessage();
  }

  function handleLogout() {
    sessionStorage.removeItem("access_token");

    setToken(null);
    setUser(null);
    setMessages([]);
    setEmail("");
    setPassword("");
    setError("");
  }

  if (loadingUser) {
    return (
      <main className="loading-page">
        <div className="loading-card">
          <div className="brand-mark">S</div>
          <p>Loading Sales Insights...</p>
        </div>
      </main>
    );
  }

  if (!user) {
    return (
      <main className="login-page">
        <section className="login-card">
          <div className="brand-mark">S</div>

          <h1>Sales Insights</h1>

          <p className="subtitle">
            AI-powered insights grounded in your sales data.
          </p>

          <form onSubmit={handleLogin}>
            <label>
              Email
              <input
                type="email"
                value={email}
                onChange={(event) => setEmail(event.target.value)}
                placeholder="name@company.com"
                autoComplete="email"
                required
              />
            </label>

            <label>
              Password
              <input
                type="password"
                value={password}
                onChange={(event) => setPassword(event.target.value)}
                placeholder="Password"
                autoComplete="current-password"
                required
              />
            </label>

            {error && <p className="error">{error}</p>}

            <button
              className="primary-button login-button"
              type="submit"
              disabled={loading}
            >
              {loading ? "Signing in..." : "Sign in"}
            </button>
          </form>

          <div className="demo-hint">
            <span>Demo environment</span>
            <p>
              Password: <strong>demo123</strong>
            </p>
          </div>
        </section>
      </main>
    );
  }

  return (
    <div className="app">
      <header className="header">
        <div className="header-brand">
          <div className="small-brand-mark">S</div>

          <div>
            <h1>Sales Insights</h1>
            <p>AI-powered sales intelligence</p>
          </div>
        </div>

        <div className="user-area">
          <div className="user-details">
            <strong>{user.full_name}</strong>
            <span>{user.role}</span>
          </div>

          <button
            className="secondary-button"
            type="button"
            onClick={handleLogout}
          >
            Sign out
          </button>
        </div>
      </header>

      <main className="workspace">
        <section className="chat-panel">
          {messages.length === 0 ? (
            <div className="welcome">
              <span className="eyebrow">SALES ASSISTANT</span>

              <h2>What would you like to know?</h2>

              <p>
                Ask questions about revenue, products, regions, categories
                and sales trends. Results are limited to the brands available
                to your account.
              </p>

              <div className="suggestions">
                {suggestedQuestions.map((question) => (
                  <button
                    type="button"
                    key={question}
                    onClick={() => sendMessage(question)}
                    disabled={loading}
                  >
                    <span>{question}</span>
                    <span className="suggestion-arrow">→</span>
                  </button>
                ))}
              </div>
            </div>
          ) : (
            <div className="messages">
              {messages.map((item, index) => (
                <div
                  key={`${item.role}-${index}`}
                  className={`message ${item.role}`}
                >
                  <span className="message-role">
                    {item.role === "user" ? "You" : "Sales Assistant"}
                  </span>

                  <div className="message-content">
                    {item.content}
                  </div>
                </div>
              ))}

              {loading && (
                <div className="message assistant">
                  <span className="message-role">
                    Sales Assistant
                  </span>

                  <div className="message-content loading-message">
                    <span className="loading-dot"></span>
                    Analyzing sales data...
                  </div>
                </div>
              )}
            </div>
          )}

          <form className="chat-input" onSubmit={handleSubmit}>
            <input
              value={message}
              onChange={(event) => setMessage(event.target.value)}
              placeholder="Ask a question about your sales..."
              disabled={loading}
            />

            <button
              className="primary-button send-button"
              type="submit"
              disabled={loading || !message.trim()}
            >
              Send
            </button>
          </form>

          <div className="chat-footer">
            Answers are generated from the sales data available to your account.
          </div>
        </section>
      </main>
    </div>
  );
}

export default App;