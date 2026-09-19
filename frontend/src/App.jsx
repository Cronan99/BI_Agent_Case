import { useState } from "react"

function App() {
  const [email, setEmail] = useState("")
  const [password, setPassword] = useState("")
  const [error, setError] = useState("")
  const [token, setToken] = useState(null)
  const [user, setUser] = useState(null)

  const [message, setMessage] = useState("")
  const [messages, setMessages] = useState([])
  const [loading, setLoading] = useState(false)

  async function handleLogin(event) {
    event.preventDefault()
    setError("")

    try {
      const response = await fetch(
        "http://localhost:8000/auth/login",
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            email,
            password,
          }),
        }
      )

      if (!response.ok) {
        throw new Error("Login failed")
      }

      const data = await response.json()
      setToken(data.access_token)

      const userResponse = await fetch(
        "http://localhost:8000/auth/me",
        {
          headers: {
            Authorization: `Bearer ${data.access_token}`,
          },
        }
      )

      if (!userResponse.ok) {
        throw new Error("Could not fetch user")
      }

      const userData = await userResponse.json()
      setUser(userData)

    } catch (error) {
      console.error(error)
      setError("Kunde inte logga in.")
    }
  }

  async function handleSendMessage(event) {
    event.preventDefault()

    if (!message.trim()) {
      return
    }

    const userMessage = message

    setMessages((previousMessages) => [
      ...previousMessages,
      {
        role: "user",
        text: userMessage,
      },
    ])

    setMessage("")
    setLoading(true)

    try {
      const response = await fetch(
        "http://localhost:8000/chat",
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            Authorization: `Bearer ${token}`,
          },
          body: JSON.stringify({
            message: userMessage,
          }),
        }
      )

      if (!response.ok) {
        throw new Error("Chat request failed")
      }

      const data = await response.json()

      setMessages((previousMessages) => [
        ...previousMessages,
        {
          role: "assistant",
          text: data.answer,
        },
      ])

    } catch (error) {
      console.error(error)

      setMessages((previousMessages) => [
        ...previousMessages,
        {
          role: "assistant",
          text: "Något gick fel när frågan skickades.",
        },
      ])
    } finally {
      setLoading(false)
    }
  }

  if (user) {
    return (
      <main>
        <h1>Sales Insights</h1>

        <p>Inloggad som {user.full_name}</p>
        <p>{user.role}</p>

        <h2>Chat</h2>

        <div>
          {messages.map((chatMessage, index) => (
            <div key={index}>
              <strong>
                {chatMessage.role === "user"
                  ? "Du"
                  : "Sales Assistant"}
              </strong>

              <p>{chatMessage.text}</p>
            </div>
          ))}

          {loading && (
            <p>Analyserar försäljningsdata...</p>
          )}
        </div>

        <form onSubmit={handleSendMessage}>
          <input
            type="text"
            placeholder="Fråga om din försäljning..."
            value={message}
            onChange={(event) => setMessage(event.target.value)}
            disabled={loading}
          />

          <button
            type="submit"
            disabled={loading}
          >
            Skicka
          </button>
        </form>
      </main>
    )
  }

  return (
    <main>
      <h1>Sales Insights</h1>

      <p>
        Logga in för att analysera din försäljning.
      </p>

      <form onSubmit={handleLogin}>
        <div>
          <label htmlFor="email">
            E-post
          </label>

          <input
            id="email"
            type="email"
            value={email}
            onChange={(event) =>
              setEmail(event.target.value)
            }
          />
        </div>

        <div>
          <label htmlFor="password">
            Lösenord
          </label>

          <input
            id="password"
            type="password"
            value={password}
            onChange={(event) =>
              setPassword(event.target.value)
            }
          />
        </div>

        <button type="submit">
          Logga in
        </button>

        {error && <p>{error}</p>}
      </form>
    </main>
  )
}

export default App