import sys
from dotenv import load_dotenv

load_dotenv()

from src.core.llm_provider import LLMProvider
from src.agent.agent import ReActAgent
from src.tools.clarify_task import clarify_task
from src.tools.search_arxiv import search_arxiv
from src.tools.search_semantic_scholar import search_semantic_scholar
from src.tools.compare_sources import compare_sources
from src.tools.synthesize import synthesize_findings
from src.tools.draft_paper import draft_paper
from src.tools.academic_polisher import academic_polisher
from src.tools.format_citation import format_citation


def get_research_tools():
    return [
        {
            "name": "clarify_task",
            "description": (
                "Analyze and structure a research topic into a focused research plan. "
                "Args: topic (str), context (str, optional). "
                "Returns a structured plan with refined question, subtopics, and suggested search queries."
            ),
            "func": clarify_task,
        },
        {
            "name": "search_arxiv",
            "description": (
                "Search arXiv database for preprints and drafts. "
                "Args: query (str), limit (int, optional, default 3). "
                "Returns paper titles, authors, years, IDs, PDF links, and abstract snippets."
            ),
            "func": search_arxiv,
        },
        {
            "name": "search_semantic_scholar",
            "description": (
                "Search Semantic Scholar for peer-reviewed papers with citation counts. "
                "Args: query (str), limit (int, optional, default 3). "
                "Returns paper titles, authors, years, citation count, URLs, and abstracts."
            ),
            "func": search_semantic_scholar,
        },
        {
            "name": "compare_sources",
            "description": (
                "Compare multiple papers to identify common themes, methodological differences, agreements, "
                "contradictions, and research gaps. "
                "Args: papers_data (str — combined text from previous search observations). "
                "Returns a structured comparative analysis."
            ),
            "func": compare_sources,
        },
        {
            "name": "synthesize_findings",
            "description": (
                "Synthesize findings from multiple papers into a cohesive thematic analysis. "
                "Args: research_question (str), papers_data (str — combined search and comparison observations). "
                "Returns a thematic synthesis ready for paper drafting."
            ),
            "func": synthesize_findings,
        },
        {
            "name": "draft_paper",
            "description": (
                "Generate a complete academic paper draft with all standard sections "
                "(Abstract, Introduction, Related Work, Methodology, Results, Conclusion, References). "
                "Args: topic (str), synthesis (str — output from synthesize_findings), "
                "citation_style (str, optional, default 'APA'). "
                "Returns the full paper draft."
            ),
            "func": draft_paper,
        },
        {
            "name": "academic_polisher",
            "description": (
                "Rewrite draft text into premium publication-grade academic style. "
                "Args: text (str), tone (str, optional, default 'formal academic style'). "
                "Returns polished text."
            ),
            "func": academic_polisher,
        },
        {
            "name": "format_citation",
            "description": (
                "Format paper metadata into standard citation styles (APA, IEEE, or BibTeX). "
                "Args: title (str), authors (str, comma-separated), year (int), style (str, optional, default 'APA'). "
                "Returns formatted citation string."
            ),
            "func": format_citation,
        },
    ]


def main():
    print("=" * 60)
    print("🔬 AI SCIENTIFIC RESEARCH ASSISTANT AGENT (ReAct CLI) 🔬")
    print("=" * 60)

    print("🤖 Initializing LLM Brain...")
    try:
        llm = LLMProvider()
        tools = get_research_tools()
        agent = ReActAgent(llm=llm, tools=tools, max_steps=10)
        print(f"✅ LLM Brain and {len(tools)} Academic Tools registered successfully!\n")
    except Exception as e:
        print(f"❌ Error during initialization: {e}")
        sys.exit(1)

    # Check if prompt passed via CLI arguments
    if len(sys.argv) > 1:
        query = " ".join(sys.argv[1:])
        print(f"📥 Received CLI Request: '{query}'")
        print("\n🚀 Starting Agentic Reasoning Loop...")
        final_answer = agent.run(query)
        print("\n" + "=" * 50)
        print("🏁 FINAL RESPONSE:")
        print("=" * 50)
        print(final_answer)
        print("=" * 50)
        return

    # Interactive CLI loop
    print("💡 Enter your research request below (or type 'exit' to stop).")
    print("💡 Examples:")
    print("   - 'Search papers on RAG and draft a short literature review.'")
    print("   - 'Find papers about Attention Is All You Need and format citation in BibTeX.'")
    print("   - 'Polish this text: we ran tests on deep learning and got 95% accuracy.'")
    print("   - 'Write a complete academic paper on deep learning for cancer detection.'")
    print("-" * 60)

    while True:
        try:
            query = input("\n🧑‍🔬 Research Prompt > ").strip()
            if not query:
                continue
            if query.lower() in ["exit", "quit", "q"]:
                print("\n👋 Goodbye!")
                break

            print("\n🚀 Agent is thinking...")
            final_answer = agent.run(query)

            print("\n" + "=" * 50)
            print("🏁 FINAL RESPONSE:")
            print("=" * 50)
            print(final_answer)
            print("=" * 50)

        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"\n❌ Error: {e}")


if __name__ == "__main__":
    main()
