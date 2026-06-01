import requests
import xml.etree.ElementTree as ET
import urllib.parse
import re

from src.tools._mock_database import _search_mock_database


def search_arxiv(query: str, limit: int = 10) -> str:
    """
    Search arXiv for academic preprints.
    Args:
        query: Search keywords or query string.
        limit: Max number of papers to return (default 10).
    """
    try:
        query_encoded = urllib.parse.quote(query.strip())
        url = f"http://export.arxiv.org/api/query?search_query=all:{query_encoded}&max_results={limit}"

        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            root = ET.fromstring(response.content)
            ns = {"atom": "http://www.w3.org/2005/Atom"}
            entries = root.findall("atom:entry", ns)

            if entries:
                results = []
                for i, entry in enumerate(entries):
                    title = entry.find("atom:title", ns).text.strip()
                    title = re.sub(r"\s+", " ", title)
                    summary = entry.find("atom:summary", ns).text.strip()
                    summary = re.sub(r"\s+", " ", summary)
                    published = entry.find("atom:published", ns).text.strip()[:4]
                    arxiv_id = entry.find("atom:id", ns).text.strip().split("/abs/")[-1]
                    pdf_url = f"https://arxiv.org/pdf/{arxiv_id}.pdf"

                    authors = [a.find("atom:name", ns).text.strip() for a in entry.findall("atom:author", ns)]
                    authors_str = ", ".join(authors)

                    results.append(
                        f"[{i+1}] Title: {title}\n"
                        f"    Authors: {authors_str}\n"
                        f"    Year: {published}\n"
                        f"    ID: arXiv:{arxiv_id}\n"
                        f"    PDF: {pdf_url}\n"
                        f"    Abstract: {summary[:300]}...\n"
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
            f"    ID: {paper['id']}\n"
            f"    PDF: {paper['pdf']}\n"
            f"    Abstract: {paper['abstract'][:300]}...\n"
        )
    return "\n".join(results)
