# AI_NOTES.md

## AI Tools Used
- **Claude (Anthropic, claude.ai)** — primary tool throughout the entire project. Used via the web chat interface at claude.ai, not via any context file or .cursorrules. All code was generated through back-and-forth conversation with Claude.
- **Cursor** — AI-assisted code editor for pasting and editing files locally.

No CLAUDE.md, AGENTS.md, or .cursorrules files were used. All AI interaction happened through the claude.ai chat interface directly. This file serves as the required AI context disclosure.

Work split: Claude generated all code files (backend, frontend, schema, Dockerfile, README). I made all deployment decisions, caught errors during testing, debugged issues, and handled every step of running commands and deploying manually.

## 3 Key Decisions I Made

**1. Single shared vector table with workspace_id column**
The spec required one shared vector store — not one table per workspace. I enforced isolation by always including `WHERE workspace_id = $1` inside the vector similarity query itself, not as a post-filter. This means the database filters before ranking by cosine similarity, so cross-workspace chunks never appear in results even by accident.

**2. Hugging Face Spaces for backend hosting**
Render's free tier (512MB RAM) couldn't handle sentence-transformers — the embedding model loads roughly 400MB into memory, which crashes Render on every request. Hugging Face Spaces CPU Basic tier gives enough headroom, already supports Docker (which matched our existing Dockerfile), and is genuinely free with no credit card. This was a deliberate trade-off: slightly more complex deployment in exchange for a working app.

**3. Two-call tool execution loop**
When the LLM decides to call a tool, the flow is: (1) LLM returns a structured tool call, (2) validate tool name against a whitelist and validate arguments before executing anything, (3) execute the tool, (4) log the call to DB with success/failure, (5) send the result back to the LLM in a second API call so it generates a natural language response. This ensures the model always acknowledges what happened, unknown tools are rejected cleanly, and every tool call is auditable in the dashboard.

## Hardest Bug: Workspace Isolation Appeared Broken

During testing, I switched to Project Alpha workspace and asked about TechCorp — information that only existed in My Workspace. The AI returned the correct TechCorp answer, which should be impossible if isolation was working.

My first instinct was that the `WHERE workspace_id = $1` query was wrong. I reviewed the code carefully — it looked correct. So I ran a SQL query directly on Neon to check what data actually existed:

```sql
SELECT d.filename, d.workspace_id, w.name 
FROM documents d 
JOIN workspaces w ON d.workspace_id = w.id;
```

The results showed both `workspace1.txt` and `workspace2.txt` in both workspaces. The bug wasn't in the code at all — I had accidentally uploaded both documents to both workspaces during testing. The UI auto-selects the first workspace on login, and I uploaded without checking which workspace was active.

I deleted the duplicate records directly in Neon, retested, and isolation worked perfectly. Project Alpha correctly said "I don't know based on the uploaded documents" when asked about TechCorp.

This was an important lesson: when security-critical behaviour seems broken, verify the data before assuming the code is wrong. The isolation logic was correct from the start.

## What I'd Improve With More Time
- Streaming responses token by token (currently waits for full LLM response before displaying)
- PDF upload support (currently only .txt, .md, .csv)
- Hybrid search (keyword + vector) for better retrieval on short or exact-match queries
- A retrieval debug view showing exactly which chunks were used per answer — proving isolation visually
- Multi-step tool use (model calls a tool, sees the result, decides to call another before answering)
- Rate limiting on the API endpoints to prevent abuse
- Better chunking strategy — current fixed-size chunking can split sentences mid-thought; sentence-aware chunking would improve retrieval quality