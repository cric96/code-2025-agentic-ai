## Note on Google Scholar Profiles API

If you see this error:

```
{"error": "The Google Scholar Profiles API is discontinued."}
```

that endpoint is no longer available (common with third‑party wrappers like old "Google Scholar Profiles" APIs). Instead, use open, supported sources such as OpenAlex or Semantic Scholar.

### Quick replacement: OpenAlex (no API key)

The repository includes a tiny helper `utils/openalex_client.py` (no extra deps, uses stdlib) that lets you search authors and list their works via the OpenAlex API.

Example:

```python
from utils.openalex_client import search_authors, get_author_works

# 1) Find an author
authors = search_authors("Yann LeCun", per_page=3)
for a in authors:
	print(a.display_name, a.h_index, a.id)

# 2) Fetch top works for the first result
if authors:
	works = get_author_works(authors[0].id, per_page=5)
	for w in works:
		print(w.publication_year, w.cited_by_count, w.display_name)
```

OpenAlex docs: https://docs.openalex.org/

### Alternative: Semantic Scholar (API key recommended)

Semantic Scholar also offers a solid public API (with generous free tier). You can search authors and papers, and fetch detailed profiles:
- Docs: https://api.semanticscholar.org/api-docs/
- Start with: `/graph/v1/author/search?query=...` and `/graph/v1/author/{authorId}`

If you'd like, we can wire a small client for Semantic Scholar too, with optional caching and rate‑limit handling.

### Why not “Google Scholar API”?  
Google Scholar does not offer an official public API. Many unofficial endpoints have been shut down or blocked, which is why you may see the discontinuation error above.
