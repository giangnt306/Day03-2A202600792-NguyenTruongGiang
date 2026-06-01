import requests
import urllib.parse
import re

from src.tools._mock_database import _search_mock_database


def search_semantic_scholar(query: str, limit: int = 10) -> str:
    """
    Search Semantic Scholar for peer-reviewed academic papers.
    Args:
        query: Search keywords or query string.
        limit: Max number of papers to return (default 10).
    """
    try:
        query_encoded = urllib.parse.quote(query.strip())
        url = (
            f"https://api.semanticscholar.org/graph/v1/paper/search"
            f"?query={query_encoded}&limit={limit}"
            f"&fields=title,authors,abstract,url,year,citationCount"
        )

        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            data = response.json()
            papers = data.get("data", [])
            if papers:
                results = []
                for i, paper in enumerate(papers):
                    title = paper.get("title", "No Title")
                    year = paper.get("year", "N/A")
                    citation_count = paper.get("citationCount", 0)
                    paper_url = paper.get("url", "N/A")
                    abstract = paper.get("abstract", "No Abstract Available") or "No Abstract Available"
                    abstract = re.sub(r"\s+", " ", abstract)

                    authors = [a.get("name", "") for a in paper.get("authors", [])]
                    authors_str = ", ".join(authors) if authors else "Unknown Authors"

                    results.append(
                        f"[{i+1}] Title: {title}\n"
                        f"    Authors: {authors_str}\n"
                        f"    Year: {year}\n"
                        f"    Citations: {citation_count}\n"
                        f"    URL: {paper_url}\n"
                        f"    Abstract: {abstract[:300]}...\n"
                    )
                return "\n".join(results)
    except Exception:
        pass

    # Fallback to local mock database
    mock_results = _search_mock_database(query, limit)
    if not mock_results:
        return "No relevant papers found matching the query in the local fallback database."
    results = []
    for i, paper in enumerate(mock_results):
        results.append(
            f"[{i+1}] Title: {paper['title']} (Source: Local Database Fallback)\n"
            f"    Authors: {paper['authors']}\n"
            f"    Year: {paper['year']}\n"
            f"    Citations: {paper['citations']}\n"
            f"    URL: {paper['url']}\n"
            f"    Abstract: {paper['abstract'][:300]}...\n"
        )
    return "\n".join(results)
