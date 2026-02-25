"""
LLM (Large Language Model) initialisation.
"""

from langchain_openai import ChatOpenAI

from src.config import get_env, MODEL_NAME


def init_llm() -> ChatOpenAI:
    """Initialise and return the ChatOpenAI instance."""
    _ = get_env("OPENAI_API_KEY")  # fail early if missing
    llm = ChatOpenAI(model=MODEL_NAME, temperature=0)
    print(f"[init] Using LLM model: {MODEL_NAME}")
    return llm
