def draft_paper(topic: str, synthesis: str, citation_style: str = "APA") -> str:
    """
    Generate a complete academic paper draft with all standard sections based on synthesized research.
    Args:
        topic: The main research topic or proposed paper title.
        synthesis: Synthesized findings and thematic analysis from the research phase.
        citation_style: Citation format — APA, IEEE, or BibTeX (default: APA).
    """
    try:
        from src.core.llm_provider import LLMProvider
        provider = LLMProvider()

        prompt = f"""You are a professional academic writer and journal editor. Based on the research topic and synthesized findings below, write a complete, well-structured academic paper draft.

Research Topic: {topic}
Citation Style: {citation_style}

Synthesized Research Findings:
{synthesis}

---

Write a full academic paper with ALL sections below. Each section must be substantive — no placeholder text.

# [Propose a precise academic title]

## Abstract
Write a 150–250 word abstract covering: background and motivation, research objectives, key findings from the literature, and implications.

## 1. Introduction
Cover: (1) background and real-world motivation, (2) the specific problem this paper addresses, (3) why existing solutions are insufficient, (4) research objectives and contributions, (5) paper organization overview.

## 2. Related Work
Organize by thematic groups. For each group, describe what prior work found, compare approaches, and note limitations. Cite only papers mentioned in the synthesis above.

## 3. Methodology
Describe the research methodology used in this survey/analysis: search strategy, inclusion/exclusion criteria, how papers were evaluated and compared.

## 4. Results and Discussion
Present the key findings thematically. Discuss what the literature agrees on, where debates exist, and what the strongest evidence points to. Include a comparative analysis of the most impactful approaches.

## 5. Conclusion
Summarize the main contributions of this paper, state the key takeaways, acknowledge limitations, and propose concrete directions for future research.

## References
List all cited papers in {citation_style} format. Only include papers from the synthesis — do NOT invent references.

---
CRITICAL RULES:
- Never invent paper titles, authors, years, or statistics not present in the synthesis.
- Maintain formal academic prose throughout.
- Use hedged language where evidence is limited (e.g., "suggests", "indicates", "may").
- Each section must be complete and ready to submit (not skeleton notes)."""

        response = provider.generate(prompt)
        if isinstance(response, dict):
            content = response.get("content", "").strip()
        else:
            content = str(response).strip()

        header = (
            f"{'='*60}\n"
            f"ACADEMIC PAPER DRAFT\n"
            f"Topic: {topic}\n"
            f"Citation Style: {citation_style}\n"
            f"{'='*60}\n\n"
        )
        return header + content
    except Exception as e:
        return f"Error drafting paper: {e}"
