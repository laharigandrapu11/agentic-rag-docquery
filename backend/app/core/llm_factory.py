from app.core.config import settings

from langchain_mistralai import ChatMistralAI
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_groq import ChatGroq

# Model tiers per provider
# small_model=True  → small/fast model (used by router node only)
# small_model=False → full model (used by decomposer + synthesizer)
_MODELS = {
    "groq":    ("llama-3.1-8b-instant",   "llama-3.3-70b-versatile"),
    "gemini":  ("gemini-2.0-flash",        "gemini-2.0-flash"),
    "mistral": ("mistral-small-latest",    "mistral-large-latest"),
}


def get_llm(provider: str | None = None, small_model: bool = False):
    """Return a LangChain chat model for the given provider.

    small_model=True  → smaller, faster model for simple/complex classification.
    small_model=False → full model for decomposition and synthesis.
    """
    provider = (provider or settings.default_provider).lower()

    if provider not in _MODELS:
        raise ValueError(f"Unsupported provider: {provider!r}. Choose groq, gemini, or mistral.")

    small, full = _MODELS[provider]
    model = small if small_model else full

    if provider == "groq":
        return ChatGroq(model=model, api_key=settings.groq_api_key)

    if provider == "gemini":
        return ChatGoogleGenerativeAI(model=model, google_api_key=settings.google_api_key)

    if provider == "mistral":
        return ChatMistralAI(model=model, api_key=settings.mistral_api_key)