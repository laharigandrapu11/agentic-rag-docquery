from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.documents import router as documents_router
from app.api.query import router as query_router
from app.api.provider import router as provider_router
from app.core.config import settings
from app.core.llm_factory import MODELS

from fastapi import Request
from app.security.rate_limiter import enforce_rate_limit

app = FastAPI(
    title="Agentic RAG DocQuery",
    description="Agentic RAG-based document query system with multi-hop reasoning.",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(documents_router, prefix="/api", tags=["Documents"])
app.include_router(provider_router, prefix="/api", tags=["Provider"])
app.include_router(query_router, prefix="/api", tags=["Query"])


@app.get("/health", tags=["Health"])
async def health(request: Request):
        # Rate limit: 30 requests per minute per IP
    enforce_rate_limit(request=request, key_suffix=None, limit=30, window_seconds=60)
    return {
        "status": "ok",
        "version": "0.1.0",
        "available_providers": list(MODELS.keys()),
        "default_provider": settings.default_provider,
    }