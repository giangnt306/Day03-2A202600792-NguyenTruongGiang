# Individual Report: Lab 3 - Chatbot vs ReAct Agent

- **Student Name**: Nguyen Truong Giang
- **Student ID**: 2A202600792
- **Date**: 2026-06-01

---

## I. Technical Contribution (15 Points)

### Modules Implemented

#### 1. `src/tools/draft_paper.py` — Core missing pipeline step

This is my most significant contribution, completing the final step of the pipeline where the team was stuck. The tool receives `topic`, `synthesis` (output from the previous step), and `citation_style`, then calls the LLM to generate a complete paper draft with 6 sections: Abstract, Introduction, Related Work, Methodology, Results & Discussion, Conclusion, and References.

```python
# src/tools/draft_paper.py (core logic)
def draft_paper(topic: str, synthesis: str, citation_style: str = "APA") -> str:
    from src.core.llm_provider import LLMProvider
    provider = LLMProvider()
    prompt = f"""You are a professional academic writer...
    Research Topic: {topic}
    Synthesized Research Findings:
    {synthesis}
    Write a full academic paper with ALL sections..."""
    response = provider.generate(prompt)
    ...
```

This tool interacts with the ReAct loop as follows: `synthesize_findings` returns an Observation → the agent extracts the synthesis text → calls `draft_paper(topic=..., synthesis=...)` → receives the completed draft → outputs `Final Answer`.

#### 2. `src/tools/clarify_task.py`, `compare_sources.py`, `synthesize.py`

Three intermediate tools that complete the missing pipeline stages:
- `clarify_task` — structures the research question into an actionable plan
- `compare_sources` — compares multiple papers, identifying common themes, differences, and research gaps
- `synthesize_findings` — synthesizes results into a thematic analysis

#### 3. Splitting tools into separate files (per teacher's requirement)

Refactored the entire monolithic `academic_tools.py` into 8 independent files:

```
src/tools/
├── _mock_database.py          # shared fallback data
├── clarify_task.py
├── search_arxiv.py
├── search_semantic_scholar.py
├── compare_sources.py
├── synthesize.py
├── draft_paper.py             ← main contribution
├── academic_polisher.py
├── format_citation.py
└── __init__.py                # re-exports all 8 tools
```

`academic_tools.py` is retained as a backward-compatibility shim to avoid breaking the team's existing code.

#### 4. Two critical bug fixes in `src/agent/agent.py`

**Bug fix 1 — Regex failing to match multiline arguments** ([agent.py:147](../../src/agent/agent.py#L147)):

```python
# BEFORE (broken): .*? does not match \n, long args are silently truncated
action_match = re.search(r"Action:\s*(\w+)\((.*?)\)", response_text)

# AFTER (correct): re.DOTALL + greedy to match up to the last ')'
action_match = re.search(r"Action:\s*(\w+)\((.*)\)", response_text, re.DOTALL)
```

This bug caused `compare_sources` and `synthesize_findings` — tools that receive multi-line observations as arguments — to always receive empty args, leading to `PARSER_ERROR`.

**Bug fix 2 — Input guard to prevent off-topic hallucination** ([agent.py:_is_research_related](../../src/agent/agent.py)):

```python
def _is_research_related(self, user_input: str) -> bool:
    probe = ('Answer with only YES or NO.\n'
             'Is the following request related to scientific research...?\n'
             f'Request: "{user_input}"')
    result = self.llm.generate(probe)
    return result.get("content", "").strip().upper().startswith("YES")
```

#### 5. `src/chatbot.py` — Baseline for comparison

A minimal chatbot: a single LLM call with no tools and no ReAct loop. Used as a control condition to measure quality differences against the ReActAgent.

---

## II. Debugging Case Study (10 Points)

### Incident: Agent never successfully calls `compare_sources` or `synthesize_findings`

**Problem description:**
When testing the full pipeline, the agent consistently skipped step 4 (compare) and step 5 (synthesize) despite the system prompt explicitly requiring them. The agent either jumped directly to `draft_paper` with `synthesis=""`, or returned a Final Answer immediately after the search steps.

**Log source** (`logs/2026-06-01.log`):
```json
{"event": "TOOL_EXECUTION", "tool": "search_arxiv", "arguments": "query=\"deep learning cancer\"", "observation": "[1] Title: ..."}
{"event": "TOOL_EXECUTION", "tool": "search_semantic_scholar", "arguments": "query=\"deep learning cancer\"", "observation": "[1] Title: ..."}
{"event": "PARSER_ERROR", "response": "Thought: I now have enough data.\nAction: compare_sources(papers_data=\"[1] Title: Deep Learning...\\n    Authors: Jenkins...\\n    Year: 2022\\n    Abstract: We present...\")"}
{"event": "AGENT_END", "steps": 3, "status": "timeout"}
```

**Diagnosis:**
The `PARSER_ERROR` log makes the root cause clear: the LLM wrote a correctly formatted Action, but `re.search(r"Action:\s*(\w+)\((.*?)\)", response_text)` returned `None`. Reasons:

1. `.*?` is **non-greedy and has no `re.DOTALL`** — the regex does not match the `\n` character
2. `papers_data` contains multi-line search results (with newlines) → regex fails → `action_match = None`
3. Code falls into the `else` branch → checks `"Final Answer:" in response_text` → not found → logs `PARSER_ERROR` → returns raw response text

**Verification:**
```python
import re
text = 'Action: compare_sources(papers_data="Title: X\nAuthors: Y")'
print(re.search(r"Action:\s*(\w+)\((.*?)\)", text))            # → None
print(re.search(r"Action:\s*(\w+)\((.*)\)", text, re.DOTALL))  # → Match object
```

**Solution:**
Add the `re.DOTALL` flag and change `.*?` to `.*` (greedy) to match up to the last `)` in the string:
```python
action_match = re.search(r"Action:\s*(\w+)\((.*)\)", response_text, re.DOTALL)
```

**Result after fix:** The pipeline runs all 6 steps end-to-end; `compare_sources` and `synthesize_findings` are now called correctly with complete observations.

---

## III. Personal Insights: Chatbot vs ReAct (10 Points)

### 1. Reasoning — How does the `Thought` block help compared to a Chatbot?

A chatbot answers directly from parametric memory (knowledge learned during training) with no planning step. When asked "find papers on RAG," it may return plausible paper names but **fabricates URLs and publication years**. The ReActAgent works differently:

- `Thought:` forces the LLM to ask itself "what do I need to do next?" before acting
- Each `Observation` provides ground truth from a real API — subsequent steps reason over actual data
- Result: URLs, years, authors, and citation counts all come from real arXiv/Semantic Scholar responses, not from training data

This is most visible with `format_citation`: a chatbot can guess the APA format reasonably well, but the ReActAgent first calls `search_semantic_scholar` to retrieve the exact metadata before formatting.

### 2. Reliability — When does the Agent actually perform *worse* than the Chatbot?

| Scenario | Chatbot | ReActAgent |
|---|---|---|
| Simple question requiring no search | Responds in ~1s | Takes 10–30s running 6 steps |
| Off-topic input | Declines or gives a generic answer | May timeout or trigger pipeline on wrong topic |
| arXiv / Semantic Scholar API down | N/A | Falls back to mock DB → irrelevant results |
| Deep reasoning questions (math, logic) | Better | Agent "wastes" steps on unnecessary tool calls |

The ReActAgent underperforms in scenarios requiring fast response times (conversational chitchat) or when the tool infrastructure is unavailable — in those cases, the loop overhead becomes a liability rather than an advantage.

### 3. Observation — How does environment feedback influence subsequent steps?

Observation is the component that distinguishes ReAct from standard Chain-of-Thought. Each Observation:
- **Updates the agent's knowledge state** in the context window — search results from step 2 are available to steps 4 and 5
- **Triggers re-planning** — if an Observation is empty or contains an error, the agent adjusts its search query on the next attempt
- **Is the sole permitted source of citations** — this constraint in the system prompt prevents hallucination

However, there is a known limitation: when an Observation exceeds ~500 tokens, the LLM tends to **summarize it** rather than pass it verbatim as an argument to the next tool. This is why `compare_sources` sometimes receives a condensed version of the papers rather than the full raw data.

---

## IV. Future Improvements (5 Points)

### Scalability — Concurrent execution and tool retrieval

The current pipeline is sequential: step 2 must complete before step 3 begins. The most obvious improvement is to **run searches in parallel**:

```python
# Replace sequential calls with asyncio.gather:
arxiv_results, ss_results = await asyncio.gather(
    async_search_arxiv(query),
    async_search_semantic_scholar(query)
)
```

For systems with more than 20 tools, a **Vector DB (FAISS or Chroma)** should be used to retrieve relevant tools at runtime rather than listing all of them in the system prompt — this reduces token cost and improves tool selection precision.

### Safety — Supervisor LLM and output validation

Deploy a lightweight **Supervisor Agent** running in parallel that inspects each `Final Answer` before it is returned to the user:
- Hallucination detection: compare citations in the draft against the list of papers extracted from Observations
- Flag any URL that did not appear in any Observation block
- Rate limiting to prevent users from triggering multiple expensive pipeline runs

### Performance — Stateful memory instead of "pass observations as args"

The core architectural weakness: the agent must "remember" observations by copy-pasting them into the arguments of the next tool call. A production-grade solution is a shared state object:

```python
# Instead of:
synthesize_findings(papers_data="<full 500-token observations>")

# Use a shared state object:
class AgentMemory:
    search_results: List[Paper]   # structured, deduplicated
    synthesis_notes: str
    draft: str
```

This approach avoids truncation from context window limits, reduces token usage by ~40%, and guarantees data integrity across all pipeline steps.

---

> **Submission note**: This report documents individual contributions made during the development of the system — from the state where the pipeline was stalled at `synthesize` to the completion of all 6 steps including `draft_paper`, along with two critical bug fixes in the ReActAgent parser.
