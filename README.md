# Multi-Workspace Document Assistant

A RAG-powered document assistant with tool calling, real auth, and Discord notifications.

## Tech Stack
- **Backend**: FastAPI (Python)
- **Database**: Neon (Postgres + pgvector)
- **LLM**: Groq (llama3-70b)
- **Embeddings**: sentence-transformers (all-MiniLM-L6-v2, 384 dims)
- **Frontend**: Plain HTML/CSS/JS
- **Backend hosting**: Fly.io
- **Frontend hosting**: Vercel

## Features
- Real JWT auth (signup / login)
- Multiple workspaces per user, strict isolation at query level
- Document upload → chunking → embedding → pgvector storage
- RAG chat with citations on every answer
- Honest "I don't know" when docs don't contain the answer
- Tool calling: AI detects tasks in chat → saves to DB → notifies Discord
- Prompt injection resistance

---

## Local Development

### 1. Backend setup

```bash
cd backend
pip install -r requirements.txt
```

Copy `.env.example` to `.env` and fill in your values:
```bash
cp .env.example .env
```

Run the schema on Neon (paste `schema.sql` into the Neon SQL editor).

Start the backend:
```bash
uvicorn main:app --reload
```

Backend runs at `http://localhost:8000`

### 2. Frontend setup

Open `frontend/index.html` directly in your browser.
The `API` variable at the top of the script is set to `http://localhost:8000` by default.

---

## Deployment

### Backend → Fly.io

```bash
# Install flyctl if you haven't: https://fly.io/docs/hands-on/install-flyctl/
cd backend
fly auth login
fly launch   # follow prompts, use existing fly.toml
fly secrets set DATABASE_URL="..." GROQ_API_KEY="..." DISCORD_WEBHOOK_URL="..." JWT_SECRET="..."
fly deploy
```

### Frontend → Vercel

1. Push this repo to GitHub
2. Go to vercel.com → New Project → import your repo
3. Set **Root Directory** to `frontend`
4. Deploy
5. After deploy, update the `API` variable in `frontend/index.html` to your Fly.io backend URL, then redeploy

---

## Environment Variables

| Variable | Description |
|---|---|
| `DATABASE_URL` | Neon Postgres connection string |
| `GROQ_API_KEY` | From console.groq.com |
| `DISCORD_WEBHOOK_URL` | From your Discord server settings |
| `JWT_SECRET` | Any long random string (keep secret) |

---

## Project Structure

```
workspace-assistant/
├── backend/
│   ├── main.py              # FastAPI app, all routes
│   ├── database.py          # Connection pool
│   ├── auth.py              # JWT + password hashing
│   ├── embeddings.py        # Sentence-transformers + chunking
│   ├── discord_notify.py    # Discord webhook helper
│   ├── schema.sql           # Run this on Neon once
│   ├── requirements.txt
│   ├── Dockerfile
│   ├── fly.toml
│   └── .env.example
└── frontend/
    ├── index.html           # Full single-page app
    └── vercel.json
```

---

## AI Notes

- Workspace isolation: every vector search query includes `WHERE workspace_id = $1` — no cross-workspace data leakage possible
- Prompt injection: user text and document text are sanitized with regex before being sent to the LLM
- Tool calling: single tool `save_task` — Groq detects when user mentions tasks, calls the tool, saves to DB, fires Discord webhook, then generates a natural follow-up response
- "I don't know": system prompt explicitly instructs the model to say this when context doesn't contain the answer
- Citations: chunk sources are returned with every response and shown in the UI
