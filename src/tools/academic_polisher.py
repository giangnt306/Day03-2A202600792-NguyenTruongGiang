def academic_polisher(text: str, tone: str = "formal academic style") -> str:
    """
    Rewrite a draft text into premium academic writing style using an LLM.
    Args:
        text: The draft or informal text to polish.
        tone: The target writing style tone (default: 'formal academic style').
    """
    try:
        from src.core.llm_provider import LLMProvider
        provider = LLMProvider()

        prompt = f"""You are a senior scientific journal editor. Rewrite the following draft text to match a premium, high-quality, {tone}.
Use clear, precise, formal scientific vocabulary, and maintain logical syntax. Return ONLY the polished text.

Draft Text:
{text}

Polished Academic Version:"""

        response = provider.generate(prompt)
        if isinstance(response, dict):
            return response.get("content", "").strip()
        return str(response).strip()
    except Exception as e:
        return f"Error polishing text: {e}"
