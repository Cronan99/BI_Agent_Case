# Sales Insights — AI-Native Sales Analytics

Sales Insights is a small AI-native analytics application that allows users to explore retail sales data using natural language.

Users can sign in, ask questions such as:

* "How much did we sell during 2025?"
* "What were our top 5 products during 2025?"
* "How were sales distributed across regions in 2025?"
* "How did sales develop month by month during 2025?"

The application uses an LLM to interpret the user's intent, but all numerical sales results are retrieved from PostgreSQL through predefined backend tools. The LLM does not calculate or invent sales figures.

Access to sales data is also restricted by the brands assigned to the authenticated user.

---

## Tech Stack

### Frontend

* React
* Vite
* JavaScript

### Backend

* Python
* FastAPI
* SQLAlchemy
* JWT authentication
* Argon2 password hashing
* Google Gemini API

### Data

* PostgreSQL
* Pandas for initial CSV import

### Infrastructure

* Docker
* Docker Compose

---

# Running the Application

## Requirements

You need:

* Docker
* Docker Compose
* A Google Gemini API key

No local Python, Node.js or PostgreSQL installation is required when running the application through Docker.

---

## 1. Configure environment variables

Create a `.env` file in the project root.

You can use `.env.example` as a template:

```env
POSTGRES_PASSWORD=your-database-password
JWT_SECRET_KEY=your-long-random-secret
GEMINI_API_KEY=your-gemini-api-key
```

A secure JWT secret can for example be generated with:

```bash
openssl rand -hex 32
```

The `.env` file is excluded from Git and should not be committed.

---

## 2. Start the application

Run:

```bash
docker compose up --build
```

Docker Compose will automatically:

1. Start PostgreSQL
2. Create the database schema
3. Import the provided sales dataset
4. Seed demo user passwords
5. Start the FastAPI backend
6. Start the React frontend

No manual database setup is required.

Once the containers are running:

Frontend:

```text
http://localhost:5173
```

FastAPI API documentation:

```text
http://localhost:8000/docs
```

Backend:

```text
http://localhost:8000
```

---

# Demo Login

The users originate from the provided dataset.

For this case, all demo users use the same password:

```text
demo123
```

Example:

```text
Email: johan.berg@ncg.example.se
Password: demo123
```

Passwords are not stored in plaintext in PostgreSQL. The demo password is hashed using Argon2 during initial application setup.

Different users have access to different brands, making it possible to test the authorization model by asking the same question while signed in as different users.

---

# Architecture

The application consists of three main services:

```text
┌──────────────────────┐
│    React Frontend    │
│    localhost:5173    │
└──────────┬───────────┘
           │
           │ JWT + HTTP
           ▼
┌──────────────────────┐
│    FastAPI Backend   │
│    localhost:8000    │
│                      │
│  Authentication      │
│  Authorization       │
│  AI Agent            │
│  Business Tools      │
└───────┬────────┬─────┘
        │        │
        │        │ Tool results
        │        ▼
        │   ┌──────────────┐
        │   │ Google Gemini│
        │   └──────────────┘
        │
        │ SQLAlchemy
        ▼
┌──────────────────────┐
│      PostgreSQL      │
│                      │
│ Sales / Products     │
│ Brands / Stores      │
│ Users / Access       │
└──────────────────────┘
```

The browser communicates only with the FastAPI backend.

The backend is responsible for authentication, authorization, database access and communication with the LLM.

PostgreSQL is not exposed directly to the browser.

---

# AI and Grounding Strategy

A central design goal of the application is to prevent the language model from inventing numerical sales results.

The LLM is therefore **not given unrestricted database access** and does not generate arbitrary SQL.

Instead, the model receives a small set of predefined business-level tools.

Currently implemented tools include:

### Sales Summary

Returns aggregated:

* Revenue
* Units sold
* Number of orders

Supports optional filters such as date and location.

### Top Products

Returns the best-performing products based on actual sales data.

### Sales Breakdown

Groups sales by:

* Brand
* Category
* Region
* City

### Sales Trend

Returns sales over time using:

* Weekly granularity
* Monthly granularity

---

## Request Flow

A typical request follows this flow:

```text
User question
      │
      ▼
FastAPI /chat
      │
      ▼
Authenticated user
      │
      ▼
Gemini interprets intent
      │
      ▼
Gemini selects a predefined tool
      │
      ▼
Backend injects authenticated user
      │
      ▼
SQLAlchemy queries PostgreSQL
      │
      ▼
Structured factual result
      │
      ▼
Gemini formulates the answer
      │
      ▼
User
```

For example:

```text
"What were our top 5 products during 2025?"
```

The LLM may translate this into a tool call conceptually equivalent to:

```text
get_top_products(
    start_date="2025-01-01",
    end_date="2025-12-31",
    limit=5
)
```

The authenticated `user_id` is **not provided by the LLM**.

It is injected by the backend before the database query is executed.

This means the model cannot request another user's data by changing a tool argument.

---

# Authentication and Authorization

Authentication and authorization are intentionally handled separately.

## Authentication

Users authenticate using email and password.

After successful login, the backend issues a signed JWT containing the user's identity.

The frontend stores the token in `sessionStorage`, allowing the login session to survive a page refresh while still ending when the browser session ends.

Protected API endpoints validate the JWT before processing the request.

## Authorization

Authorization is based on the provided `user_brand_access` data.

The relationship is:

```text
User
  │
  ▼
User Brand Access
  │
  ▼
Brand
  │
  ▼
Product
  │
  ▼
Order
```

Every sales query retrieves the authenticated user's allowed brand IDs and applies them as part of the database query.

Authorization is therefore enforced in the backend/data layer rather than relying on instructions to the language model.

Even if the LLM attempted to request inaccessible data, the database query would still be restricted to the authenticated user's brands.

---

# Database

The provided CSV dataset is imported into PostgreSQL.

Main tables:

```text
users
brands
products
stores
orders
user_brand_access
```

The dataset contains sales between January 2025 and June 2026.

Historical revenue calculations use the actual transaction values stored on each order line rather than the current product list price.

---

# Database Initialization

The PostgreSQL container automatically executes:

```text
scripts/schema.sql
```

when a new database volume is created.

After PostgreSQL becomes healthy, the backend startup process runs the data import and demo password seed scripts.

The import process is idempotent for the purposes of this case. If data already exists, the import is skipped.

For example, restarting the application does not duplicate the sales dataset.

To completely reset the database:

```bash
docker compose down -v
docker compose up --build
```

---

# Multi-User Design

The application is designed so multiple users can use the system independently.

The user identity flows through the complete request path:

```text
JWT
 ↓
FastAPI authentication
 ↓
current_user
 ↓
Business tool
 ↓
Sales service
 ↓
Authorized brand IDs
 ↓
Database query
```

The LLM never controls the identity used for authorization.

As a result, two users asking the exact same question may receive different answers depending on which brands they are authorized to access.

---

# Handling Unsupported Questions

The assistant is instructed not to invent sales numbers or time periods.

If a question cannot be answered from the available dataset or supported tools, the intended behavior is to explain that limitation rather than fabricate an answer.

The current dataset covers:

```text
January 2025 – June 2026
```

The suggested questions in the frontend are also designed to help users understand the types of analysis currently supported.

---

# Security Considerations

Several security principles are included despite the application being a limited case implementation:

* Passwords are hashed using Argon2.
* Authentication uses signed JWTs.
* JWT secrets and API keys are supplied through environment variables.
* `.env` is excluded from Git.
* PostgreSQL is not exposed as a public host port in Docker Compose.
* Authorization is enforced server-side.
* User identity is never accepted as an LLM tool argument.
* The LLM cannot execute arbitrary SQL.
* Database queries use SQLAlchemy rather than LLM-generated SQL.

---

# Project Structure

```text
solvigo_ai_case/
│
├── backend/
│   ├── Dockerfile
│   ├── entrypoint.sh
│   ├── requirements.txt
│   │
│   └── app/
│       ├── main.py
│       ├── database.py
│       ├── models.py
│       │
│       ├── agent/
│       │   ├── agent.py
│       │   └── tools.py
│       │
│       └── services/
│           ├── access_service.py
│           ├── auth_service.py
│           └── sales_service.py
│
├── frontend/
│   ├── Dockerfile
│   ├── package.json
│   └── src/
│       ├── App.jsx
│       ├── App.css
│       └── main.jsx
│
├── data/
│   ├── brands.csv
│   ├── orders.csv
│   ├── products.csv
│   ├── stores.csv
│   ├── users.csv
│   └── user_brand_access.csv
│
├── scripts/
│   ├── schema.sql
│   ├── import_data.py
│   └── seed_passwords.py
│
├── docker-compose.yml
├── .env.example
├── .dockerignore
└── README.md
```

---

# Design Decisions and Trade-offs

## Constrained tools instead of text-to-SQL

A general text-to-SQL implementation would provide more flexibility, but would also increase the risk of incorrect queries, authorization mistakes and unpredictable behavior.

For this case I chose a small set of explicit business tools instead.

This makes the system easier to reason about, test and secure while still allowing the LLM to interpret flexible natural-language questions.

## Database performs numerical calculations

Revenue, units, order counts, grouping and sorting are calculated by PostgreSQL.

The LLM's responsibility is primarily to:

1. Understand the user's question
2. Select the appropriate tool and arguments
3. Explain the factual result

This reduces the risk of arithmetic hallucinations.

## Authorization below the AI layer

Authorization is intentionally implemented below the agent.

The LLM knows what analysis should be performed, but it does not decide which brands the user can access.

This keeps access control deterministic.

## Session storage for the case

The frontend stores the JWT in `sessionStorage` to preserve authentication across page refreshes while keeping the implementation simple.

For a production system with stricter security requirements, I would prefer server-managed `HttpOnly`, `Secure` cookies and an appropriate refresh/session strategy.

## Local frontend server

The frontend currently runs through the Vite development server inside Docker because the goal of this case is a locally runnable application.

For a production deployment, the React application would normally be built into static assets and served through a production web server/CDN rather than the Vite development server.

---

# Further Development

With more time, useful next steps would include:

* Persistent conversation history
* Visualization of trends and breakdowns
* Additional analytical tools and filters
* More detailed product and brand comparisons
* Automated tests for authorization boundaries
* Rate limiting
* Production cookie-based authentication
* Structured observability and logging
* Production frontend build
* CI/CD

The current implementation intentionally prioritizes a reliable core flow:

```text
Login
  ↓
Natural-language question
  ↓
Authorized database analysis
  ↓
Grounded AI response
```

over adding a larger number of partially implemented features.
