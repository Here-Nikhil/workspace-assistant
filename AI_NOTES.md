# AI_NOTES.md — Design Decisions

## Workspace Isolation
The `document_chunks` table has a `workspace_id` column directly on it (not inherited via joins).
Every vector similarity query filters on `workspace_id` *before* ranking by cosine distance.
This means a user in Workspace A can never receive chunks from Workspace B, even by accident.

## RAG Architecture
1. User sends a message
2. Message is embedded using `all-MiniLM-L6-v2` (384 dims, fast, runs locally)
3. Top 5 semantically similar chunks are retrieved from the user's workspace only
4. Chunks are injected into the system prompt as numbered sources
5. LLM generates an answer citing sources, or says "I don't know"

## Tool Calling
Uses Groq's native tool calling API with a single tool: `save_task`.
The LLM decides when to call it based on conversation context.
After the tool runs (DB insert + Discord notify), a second LLM call generates the final reply.

## Prompt Injection Resistance
Both user messages and document text are sanitized with regex before reaching the LLM.
Patterns like "ignore previous instructions", "act as", "you are now" are stripped.
The system prompt also explicitly instructs the model to ignore instructions found in document text.

## Auth
Passwords are hashed with bcrypt (salt rounds auto-managed).
JWTs expire after 24 hours and are signed with a secret key.
Every protected endpoint validates the token via a FastAPI dependency.

## "I Don't Know" Behaviour
The system prompt contains an explicit rule:
> "If the context does NOT contain the answer, say exactly: 'I don't know based on the uploaded documents.'"
This prevents hallucination when the uploaded docs don't cover the question.
