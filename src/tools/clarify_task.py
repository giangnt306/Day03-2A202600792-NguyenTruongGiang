def clarify_task(topic: str, context: str = "") -> str:
    """
    Analyze and structure a research topic into a focused research plan.
    Args:
        topic: The research topic or question to clarify.
        context: Optional additional context or constraints about the research goal.
    """
    try:
        from src.core.llm_provider import LLMProvider
        provider = LLMProvider()

        context_section = f"\nAdditional Context: {context}" if context.strip() else ""
        prompt = f"""You are a senior academic research advisor. Analyze the following research topic and produce a structured research plan.

Research Topic: {topic}{context_section}

Provide a concise, actionable plan with these sections:
1. **Refined Research Question**: A precise, answerable academic question
2. **Key Subtopics**: 3-5 specific areas to investigate
3. **Suggested Search Queries**: 3 specific queries optimized for academic databases (arXiv, Semantic Scholar)
4. **Expected Paper Types**: Types of papers to look for (surveys, empirical studies, benchmarks, etc.)
5. **Research Scope**: Clear boundaries — what is and is not in scope

Be specific and actionable. Do not pad the response."""

        response = provider.generate(prompt)
        if isinstance(response, dict):
            content = response.get("content", "").strip()
        else:
            content = str(response).strip()

        return f"=== Research Plan for: '{topic}' ===\n\n{content}"
    except Exception as e:
        return f"Error clarifying task: {e}"
