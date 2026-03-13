from app.core.config import settings

# Populated in F5 - Provider Switching
from langchain_mistralai import ChatMistralAI
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_groq import ChatGroq

def get_llm(provider: str | None = None):
    """Return a LangChain chat model for the given provider name.

    Supported values: "groq", "gemini", "mistral".
    Falls back to settings.default_provider when provider is None.
    """
    provider = (provider or settings.default_provider).lower()

    if provider == "groq":
        return ChatGroq(
            model="llama-3.3-70b-versatile",
            api_key=settings.groq_api_key,
        )

    if provider == "gemini":
        return ChatGoogleGenerativeAI(
            model="gemini-2.0-flash",
            google_api_key=settings.google_api_key,
        )

    if provider == "mistral":
        return ChatMistralAI(
            model="mistral-large-latest",
            api_key=settings.mistral_api_key,
        )

    raise ValueError(f"Unsupported provider: {provider!r}. Choose groq, gemini, or mistral.")
