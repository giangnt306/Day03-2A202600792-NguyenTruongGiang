def compare_sources(papers_data: str) -> str:
    """
    Compare and analyze multiple academic papers to identify themes, agreements, and research gaps.
    Args:
        papers_data: Combined text of paper information gathered from previous search results.
    """
    try:
        from src.core.llm_provider import LLMProvider
        provider = LLMProvider()

        prompt = f"""You are an expert research analyst. Analyze the following collection of academic papers and provide a structured comparative analysis.

Papers Data:
{papers_data}

Provide a concise comparative analysis with:
1. **Common Themes**: Recurring topics and approaches across papers
2. **Methodological Comparison**: How different papers approach similar problems
3. **Key Agreements**: What the majority of papers agree on
4. **Contradictions / Debates**: Where papers disagree or present conflicting results
5. **Research Gaps**: Open questions not yet addressed by existing literature
6. **Most Impactful Papers**: Papers with highest influence (citations, novelty, or methodology)

Be specific and cite paper titles when making claims. Do not invent papers not present in the data above."""

        response = provider.generate(prompt)
        if isinstance(response, dict):
            content = response.get("content", "").strip()
        else:
            content = str(response).strip()

        return content
    except Exception as e:
        return f"Error comparing sources: {e}"
