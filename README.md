# Workspace Document Assistant

A RAG-powered document assistant with tool calling, real auth, and Discord notifications.

## What the App Does
- Sign up / log in with real JWT auth
- Create multiple workspaces and switch between them
- Upload documents (.txt, .md, .csv) — they get chunked, embedded, and stored
- Chat with an AI that answers only from your workspace's documents, with citations
- AI says "I don't know" when documents don't contain the answer
- AI can save tasks (via tool calling) and summarize all documents
- Every tool call is logged in the Tool Call Log dashboard tab
- Discord notification sent when a task is saved

## How to Run Locally

### 1. Clone the repo
```bash
git clone https://github.com/Here-Nikhil/workspace-assistant.git
cd workspace-assistant
```

### 2. Set up the backend
```bash
cd backend
pip install -r requirements.txt
cp .env.example .env
# Fill in your real values in .env
```

Run the schema on your Neon database (paste `schema.sql` into the Neon SQL editor).

Also run this to add the tool call log table:
```sql
CREATE TABLE tool_call_logs (
    id           SERIAL PRIMARY KEY,
    workspace_id INTEGER NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE,
    tool_name    TEXT NOT NULL,
    arguments    TEXT,
    result       TEXT,
    success      BOOLEAN NOT NULL DEFAULT true,
    created_at   TIMESTAMPTZ NOT NULL DEFAULT now()
);
```

Start the backend:
```bash
python -m uvicorn main:app --reload
```

### 3. Run the frontend
Open `frontend/index.html` in your browser. Change the `API` variable at the top of the script from the production URL to `http://127.0.0.1:8000`.

## Environment Variables

See `.env.example` for all required variables:

| Variable | Description |
|---|---|
| `DATABASE_URL` | Neon Postgres connection string |
| `GROQ_API_KEY` | From console.groq.com |
| `DISCORD_WEBHOOK_URL` | From your Discord server settings |
| `JWT_SECRET` | Any long random string |

## Deployment
- **Backend:** Hugging Face Spaces (Docker, CPU Basic free tier) — chosen because sentence-transformers needs ~400MB RAM, which exceeds Render's free tier limit
- **Frontend:** Vercel (static HTML, auto-deploys from GitHub)

## How to Test the Live App

**Live URL:** https://workspace-assist.vercel.app

**Throwaway account:**
- Email: `test@demo.com`
- Password: `Demo1234`

### Two preloaded workspaces:
- **My Workspace** — contains TechCorp company information
- **Project Alpha** — contains Project Alpha confidential details

### Good questions to ask:

In **My Workspace:**
- "Who founded TechCorp and when?"
- "What is TechCorp's revenue?"
- "Please save a task to review the financials next week"
- "Can you summarize all documents in this workspace?"

In **Project Alpha:**
- "Who is the project lead and what is the deadline?"
- "What tech stack is being used?"

### Testing isolation (most important):
1. Switch to **Project Alpha**
2. Ask: "Who founded TechCorp and what is their revenue?"
3. The AI should say: "I don't know based on the uploaded documents."
4. This proves workspace isolation is working — Project Alpha cannot see My Workspace's data even though they share the same vector table.

## Project Structure
```
workspace-assistant/
├── backend/
│   ├── main.py              # FastAPI app — all routes
│   ├── database.py          # Connection pool
│   ├── auth.py              # JWT + bcrypt
│   ├── embeddings.py        # Sentence-transformers + chunking
│   ├── discord_notify.py    # Discord webhook
│   ├── schema.sql           # Run once on Neon
│   ├── requirements.txt
│   ├── Dockerfile
│   └── .env.example
└── frontend/
    ├── index.html           # Full single-page app
    └── vercel.json
```