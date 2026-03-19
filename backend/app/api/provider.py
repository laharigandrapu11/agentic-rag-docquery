# Populated in F5 - Provider Switching

from fastapi import APIRouter, HTTPException, Request
from app.security.rate_limiter import enforce_rate_limit
from pydantic import BaseModel
from app.core.config import settings
from app.core.llm_factory import MODELS

router = APIRouter()

# In-memory active provider — starts from the value in .env
active = settings.default_provider


@router.get("/providers")
def get_providers(request: Request):
    enforce_rate_limit(request=request, key_suffix=None, limit=30, window_seconds=60)
    return {
        "available": list(MODELS.keys()),
        "active": active,
    }


class SwitchRequest(BaseModel):
    provider: str


@router.post("/switch-provider")
def switch_provider(http_req: Request, req: SwitchRequest):
    enforce_rate_limit(request=http_req, key_suffix=None, limit=20, window_seconds=60)
    global active
    if req.provider not in MODELS:
        raise HTTPException(status_code=400, detail=f"Unknown provider: {req.provider!r}. Choose from {list(MODELS.keys())}")
    active = req.provider
    return {"active": active}

    