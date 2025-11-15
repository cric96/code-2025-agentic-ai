"""
Lightweight OpenAlex client for author search and works retrieval.
No external dependencies; uses urllib from the standard library.
Docs: https://docs.openalex.org/
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional
import json
import urllib.parse
import urllib.request

OPENALEX_BASE = "https://api.openalex.org"


@dataclass
class Author:
    id: str  # e.g., https://openalex.org/A123...
    display_name: str
    orcid: Optional[str]
    works_count: int
    cited_by_count: int
    h_index: Optional[int]
    affiliation: Optional[str]


@dataclass
class Work:
    id: str
    display_name: str
    publication_year: Optional[int]
    doi: Optional[str]
    cited_by_count: int
    host_venue: Optional[str]


def _http_get_json(url: str) -> Dict[str, Any]:
    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": "agentic-ai-course/0.1 (+https://openalex.org)",
            "Accept": "application/json",
        },
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        data = resp.read()
        return json.loads(data)


def search_authors(query: str, per_page: int = 5) -> List[Author]:
    """Search authors by free-text query.

    Returns up to per_page results ordered by relevance.
    """
    params = urllib.parse.urlencode({
        "search": query,
        "per_page": per_page,
        "sort": "relevance_score:desc",
    })
    url = f"{OPENALEX_BASE}/authors?{params}"
    data = _http_get_json(url)
    results = []
    for item in data.get("results", []):
        affiliation_name = None
        last_known_institution = item.get("last_known_institution") or {}
        if last_known_institution:
            affiliation_name = last_known_institution.get("display_name")
        results.append(
            Author(
                id=item.get("id"),
                display_name=item.get("display_name"),
                orcid=(item.get("orcid") or None),
                works_count=int(item.get("works_count") or 0),
                cited_by_count=int(item.get("cited_by_count") or 0),
                h_index=(
                    int(item.get("summary_stats", {}).get("h_index"))
                    if item.get("summary_stats", {}).get("h_index") is not None
                    else None
                ),
                affiliation=affiliation_name,
            )
        )
    return results


def get_author_works(
    author_openalex_id: str,
    per_page: int = 25,
    sort: str = "cited_by_count:desc",
) -> List[Work]:
    """List works for an author by OpenAlex author id (full URL or short id).

    author_openalex_id can be "A12345" or "https://openalex.org/A12345".
    """
    # Normalize id to full URL form expected by OpenAlex filters
    if not author_openalex_id.startswith("http"):
        author_openalex_id = f"https://openalex.org/{author_openalex_id}"

    params = urllib.parse.urlencode({
        "filter": f"author.id:{author_openalex_id}",
        "per_page": per_page,
        "sort": sort,
    })
    url = f"{OPENALEX_BASE}/works?{params}"
    data = _http_get_json(url)
    results: List[Work] = []
    for item in data.get("results", []):
        results.append(
            Work(
                id=item.get("id"),
                display_name=item.get("display_name"),
                publication_year=item.get("publication_year"),
                doi=(item.get("doi") or None),
                cited_by_count=int(item.get("cited_by_count") or 0),
                host_venue=(
                    (item.get("host_venue") or {}).get("display_name")
                    if item.get("host_venue")
                    else None
                ),
            )
        )
    return results


def get_author(author_openalex_id: str) -> Optional[Author]:
    """Fetch a single author profile by OpenAlex id."""
    if not author_openalex_id.startswith("http"):
        author_openalex_id = f"https://openalex.org/{author_openalex_id}"
    url = f"{OPENALEX_BASE}/authors/{urllib.parse.quote(author_openalex_id.rsplit('/', 1)[-1])}"
    item = _http_get_json(url)

    if "id" not in item:
        return None

    affiliation_name = None
    last_known_institution = item.get("last_known_institution") or {}
    if last_known_institution:
        affiliation_name = last_known_institution.get("display_name")

    return Author(
        id=item.get("id"),
        display_name=item.get("display_name"),
        orcid=(item.get("orcid") or None),
        works_count=int(item.get("works_count") or 0),
        cited_by_count=int(item.get("cited_by_count") or 0),
        h_index=(
            int(item.get("summary_stats", {}).get("h_index"))
            if item.get("summary_stats", {}).get("h_index") is not None
            else None
        ),
        affiliation=affiliation_name,
    )


if __name__ == "__main__":
    # Simple demo
    authors = search_authors("Yann LeCun", per_page=3)
    for a in authors:
        print(f"- {a.display_name} (h-index={a.h_index}, works={a.works_count}) -> {a.id}")
    if authors:
        works = get_author_works(authors[0].id, per_page=5)
        for w in works:
            print(f"  * {w.publication_year} | {w.display_name} | cites={w.cited_by_count}")
