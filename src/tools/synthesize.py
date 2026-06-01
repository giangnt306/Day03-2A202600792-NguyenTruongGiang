def synthesize_findings(research_question: str, papers_data: str) -> str:
    """
    Synthesize findings from multiple papers into a cohesive thematic analysis ready for drafting.
    Args:
        research_question: The original research question being investigated.
        papers_data: Combined text of paper information from searches and comparisons.
    """
    try:
        from src.core.llm_provider import LLMProvider
        provider = LLMProvider()

        prompt = f"""You are a senior academic researcher. Synthesize the following research findings into a cohesive, well-structured thematic analysis suitable as notes for writing an academic paper.

Research Question: {research_question}

Papers and Findings:
{papers_data}

Write a structured synthesis with:
1. **Executive Summary**: 2-3 sentence overview of the field's current state
2. **Theme 1 — [Descriptive Name]**: Core finding + which papers support it
3. **Theme 2 — [Descriptive Name]**: Core finding + which papers support it
4. **Theme 3 — [Descriptive Name]**: Core finding + which papers support it
5. **State of the Art**: The current best-known approaches and their limitations
6. **Open Challenges**: What remains unsolved or contested
7. **Synthesis Conclusion**: What these findings collectively mean for answering the research question

IMPORTANT: Only reference papers that appear in the data above. Do NOT invent citations."""

        response = provider.generate(prompt)
        if isinstance(response, dict):
            content = response.get("content", "").strip()
        else:
            content = str(response).strip()

        return content
    except Exception as e:
        return f"Error synthesizing findings: {e}"
