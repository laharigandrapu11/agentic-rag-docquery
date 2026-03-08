# Contributing to Agentic RAG DocQuery

This document describes how the project is organized for development, the
feature roadmap, and the process for contributing changes.

---

## Table of Contents

- [Feature Roadmap](#feature-roadmap)
- [Branch Naming](#branch-naming)
- [Development Workflow](#development-workflow)
- [Local Setup](#local-setup)
- [Running Tests](#running-tests)

---

## Feature Roadmap

The project is built feature by feature in the order listed below. Each feature
is a complete vertical slice covering backend, frontend, and any infrastructure
it requires. Both contributors work on the same feature together before moving
to the next.

Track progress by checking off items as they are merged to main.

---

### F0 - Foundation

**Goal**: A running skeleton with no application logic. Verifies the full stack
starts up correctly end to end.

- [ ] Project directory structure (backend, frontend, .github)
- [ ] `docker-compose.yml` with Qdrant, backend, and frontend services
- [ ] FastAPI app skeleton with `GET /health` endpoint
- [ ] Pydantic settings loading from `.env`
- [ ] Next.js 14 shell with Tailwind CSS (no components yet)
- [ ] Backend `Dockerfile` and `requirements.txt`
- [ ] Frontend `Dockerfile` and `package.json`
- [ ] `.env.example` and `.env.local.example`
- [ ] `.gitignore`
- [ ] GitHub Actions `deploy.yml` skeleton (jobs defined, steps stubbed)

Branch: `feature/f0-foundation`

---

### F1 - Document Upload and Ingestion

**Goal**: Users can upload a document or paste a URL. The document is chunked,
embedded, and stored in Qdrant. The document list is visible in the UI.

- [ ] `POST /upload` endpoint (multipart file or JSON URL body)
- [ ] `GET /documents` endpoint
- [ ] `DELETE /documents/{doc_id}` endpoint
- [ ] LlamaIndex loaders for PDF, DOCX, Markdown, plain text, and web URLs
- [ ] `SentenceSplitter` chunker (512 tokens, 50-token overlap)
- [ ] sentence-transformers embedding (`all-MiniLM-L6-v2`)
- [ ] Qdrant upsert with chunk metadata (doc_id, page, chunk_index, source)
- [ ] `FileUpload` component (drag-and-drop and URL input)
- [ ] `DocumentList` sidebar component

Branch: `feature/f1-document-upload`

---

### F2 - Basic Question and Answer

**Goal**: Users can type a question and receive a plain text answer grounded in
the indexed documents. No streaming yet.

- [ ] `POST /query` endpoint (synchronous JSON response)
- [ ] Qdrant retrieval (top-k semantic search)
- [ ] LLM synthesis with retrieved chunks as context
- [ ] `ChatInterface` component
- [ ] `MessageBubble` component (user and assistant bubbles)

Branch: `feature/f2-basic-qa`

---

### F3 - Streaming and Citations

**Goal**: Answers stream token by token. Each answer includes inline source
references tied to specific chunks and pages.

- [ ] Convert `POST /query` to Server-Sent Events (SSE)
- [ ] `token` event type for streamed answer text
- [ ] Citation metadata attached to retrieved chunks (doc_id, page, chunk_index)
- [ ] Inline `[Source N]` markers in synthesized answers
- [ ] `SourceCitation` component (expandable source reference panel)
- [ ] Frontend SSE consumer with live token rendering

Branch: `feature/f3-streaming-citations`

---

### F4 - Agentic Multi-hop Reasoning

**Goal**: Complex questions are automatically decomposed into sub-questions.
Each sub-question is retrieved independently. The UI shows the full reasoning
chain.

- [ ] LangGraph `StateGraph` with typed state
- [ ] Router node (classifies query as simple or complex)
- [ ] Decomposer node (LLM breaks complex query into sub-questions)
- [ ] RAG retrieve node (runs retrieval per sub-question)
- [ ] Synthesize node (combines results with citations)
- [ ] `hop_trace` SSE event type (emitted at each node transition)
- [ ] `HopTrace` component (collapsible reasoning chain panel)

Branch: `feature/f4-agentic-multihop`

---

### F5 - Provider Switching

**Goal**: Users can switch between Groq, Gemini, and Mistral mid-session
without losing conversation context.

- [ ] `llm_factory.py` mapping provider name to LangChain LLM instance
- [ ] `POST /switch-provider` endpoint
- [ ] `GET /health` updated to return available providers and active provider
- [ ] `ProviderSelector` component (Groq / Gemini / Mistral switcher in UI)

Branch: `feature/f5-provider-switching`

---

### F6 - Summarize and Compare

**Goal**: Dedicated tools for summarizing a single document and comparing
content across multiple documents.

- [ ] Summarize tool node in LangGraph (map-reduce over document chunks)
- [ ] Compare tool node in LangGraph (retrieves from multiple docs, synthesizes)
- [ ] `POST /summarize` endpoint (`{ doc_id, session_id, provider }`)
- [ ] `POST /compare` endpoint (`{ doc_ids, question, provider }`)
- [ ] Summarize and Compare buttons in the UI with appropriate flows

Branch: `feature/f6-summarize-compare`

---

### F7 - Conversation Memory

**Goal**: The agent remembers previous turns within a session. Users can ask
follow-up questions without repeating context.

- [ ] SQLite session store
- [ ] `ConversationBufferMemory` injected into agent state per turn
- [ ] `session_id` generated on the frontend and sent with every request
- [ ] Conversation history persisted and retrieved by `session_id`
- [ ] New session button in the UI

Branch: `feature/f7-memory`

---

### F8 - Deployment

**Goal**: The full application is live on Google Cloud Run with a public URL.
Every push to main triggers an automated deploy.

- [ ] Backend `Dockerfile` production-hardened
- [ ] Frontend `Dockerfile` with Next.js standalone output
- [ ] GitHub Actions `deploy.yml` fully implemented (test, build, push, deploy)
- [ ] Google Container Registry image push configured
- [ ] Backend deployed to Cloud Run
- [ ] Frontend deployed to Cloud Run
- [ ] Qdrant deployed to Cloud Run (or Qdrant Cloud free tier)
- [ ] All GitHub Secrets configured
- [ ] README deployment section verified against live URLs

Branch: `feature/f8-deployment`

---

## Branch Naming

| Pattern                  | Use for                          |
|--------------------------|----------------------------------|
| `feature/f{n}-{name}`   | New feature work (see above)     |
| `fix/{short-description}`| Bug fixes                        |
| `chore/{short-description}` | Config, deps, tooling changes |

All branches are cut from `main`. Open a pull request back to `main` when the
feature checklist above is fully checked off and the app runs cleanly with
`docker-compose up`.

---

## Development Workflow

1. Pick the lowest uncompleted feature from the roadmap above.
2. Cut a branch from main using the naming convention.
3. Work through the checklist items for that feature.
4. Test locally with `docker-compose up --build`.
5. Open a pull request to main with a short description of what was built.
6. Both contributors review before merging.

One feature at a time. Do not start F{n+1} until F{n} is merged.

---

## Local Setup

```bash
git clone https://github.com/laharigandrapu11/agentic-rag-docquery.git
cd agentic-rag-docquery

cp backend/.env.example backend/.env
cp frontend/.env.local.example frontend/.env.local

# Fill in API keys in backend/.env

docker-compose up --build
```

Services after startup:

- Frontend:    http://localhost:3000
- Backend:     http://localhost:8000
- Swagger UI:  http://localhost:8000/docs
- Qdrant:      http://localhost:6333/dashboard

---

## Running Tests

Backend:

```bash
cd backend
pip install -r requirements.txt
pytest
```

Frontend:

```bash
cd frontend
npm install
npm run lint
```
