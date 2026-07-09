# AI_NOTES.md

## AI Tools Used
- **Claude (Anthropic)** — primary tool throughout. Used for architecture decisions, all code generation, debugging, and deployment guidance.
- **Cursor** — AI-assisted code editor for local development.

Work split: Claude generated all code files. I made decisions about which suggestions to use, caught errors, tested everything locally, and handled all deployment steps manually.

## 3 Key Decisions I Made

**1. Single shared vector table with workspace_id column**
The spec required one shared vector store — not one table per workspace. I enforced isolation by always including `WHERE workspace_id = $1` inside the vector similarity query itself, not as a post-filter. This means the DB engine filters before ranking, so cross-workspace chunks never even appear in results.

**2. Hugging Face Spaces for backend hosting**
Render's free tier (512MB RAM) couldn't handle sentence-transformers (the embedding model loads ~400MB into memory). Hugging Face Spaces CPU Basic tier gives enough headroom for the model to load and serve requests reliably — and already uses Docker, which matched our Dockerfile.

**3. Two-call tool execution loop**
When the LLM decides to call a tool, I don't just run it and move on. The flow is: (1) LLM returns tool call, (2) validate tool name and arguments, (3) execute, (4) log to DB, (5) send result back to LLM in a second call so it generates a natural response. This means the LLM always acknowledges what happened rather than leaving the user with a silent action.

## Hardest Bug: Workspace Isolation Appeared Broken

During testing, asking Workspace B about facts that only existed in Workspace A returned correct answers — which should be impossible if isolation was working.

The bug wasn't in the code. The isolation query was correct all along. The actual problem was that I had accidentally uploaded both documents to both workspaces during manual testing (the UI auto-selects the first workspace on login, and I uploaded without checking which workspace was active). The data was wrong, not the code.

I caught it by running a SQL query directly on Neon to check which documents belonged to which workspace, saw duplicates immediately, deleted the wrong ones, and retested. Isolation worked correctly after that.

This was a good reminder: when security-critical behaviour seems broken, check the data before assuming the code is wrong.

## What I'd Improve With More Time
- Streaming responses token by token (currently waits for full response)
- Support PDF uploads (currently only .txt, .md, .csv)
- Hybrid search (keyword + vector) for better retrieval on short queries
- A retrieval debug view showing exactly which chunks were used per answer
- Multi-step tool use (model calls tool, sees result, decides to call another)
- Rate limiting on the API to prevent abuse