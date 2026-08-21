"""
Fame check + disambiguation resolution against Wikipedia.

Pure HTTP against Wikipedia's REST summary endpoint and the Action API —
no LLM involvement, per the PRD (the REST endpoint's `type` field tells us
directly whether a name is ambiguous).
"""

import requests

from . import config

_session = requests.Session()
_session.headers.update({"User-Agent": config.WIKI_USER_AGENT})


def _rest_summary(title: str) -> dict | None:
    """Fetch the REST summary for a title. Returns None on 404."""
    url = config.WIKI_REST_SUMMARY_URL.format(title=title.replace(" ", "_"))
    resp = _session.get(url, timeout=10)
    if resp.status_code == 404:
        return None
    resp.raise_for_status()
    return resp.json()


def _action_info_and_extract(title: str) -> dict | None:
    """Fetch wikitext byte length + plain-text extract in one Action API call."""
    params = {
        "action": "query",
        "titles": title,
        "prop": "info|extracts",
        "explaintext": 1,
        "exlimit": 1,
        "format": "json",
    }
    resp = _session.get(config.WIKI_ACTION_API_URL, params=params, timeout=15)
    resp.raise_for_status()
    pages = resp.json().get("query", {}).get("pages", {})
    page = next(iter(pages.values()), None)
    if page is None or "missing" in page:
        return None
    return {
        "length_bytes": page.get("length", 0),
        "extract": page.get("extract", ""),
    }


def _disambiguation_candidates(title: str) -> list[dict]:
    """Pull up to MAX_DISAMBIGUATION_CANDIDATES candidates from a disambiguation
    page's outgoing namespace-0 links, each with a one-line descriptor pulled
    from that candidate's own REST summary."""
    params = {
        "action": "query",
        "titles": title,
        "prop": "links",
        "plnamespace": 0,
        "pllimit": config.MAX_DISAMBIGUATION_LINKS_TO_CHECK,
        "format": "json",
    }
    resp = _session.get(config.WIKI_ACTION_API_URL, params=params, timeout=15)
    resp.raise_for_status()
    pages = resp.json().get("query", {}).get("pages", {})
    page = next(iter(pages.values()), None)
    if page is None:
        return []

    link_titles = [link["title"] for link in page.get("links", [])]

    candidates = []
    for link_title in link_titles:
        if len(candidates) >= config.MAX_DISAMBIGUATION_CANDIDATES:
            break
        summary = _rest_summary(link_title)
        if summary is None or summary.get("type") == "disambiguation":
            continue
        descriptor = summary.get("description") or summary.get("extract", "").split(". ")[0]
        if not descriptor:
            continue
        candidates.append({
            "title": summary.get("title", link_title),
            "descriptor": descriptor,
        })
    return candidates


def fame_check(name: str) -> dict:
    """
    Resolve a name against Wikipedia and check it against the fame threshold.

    Returns one of:
      {"status": "NOT_FOUND"}
      {"status": "AMBIGUOUS", "candidates": [{"title", "descriptor"}, ...]}
      {"status": "TOO_OBSCURE"}
      {"status": "OK", "title": str, "length_bytes": int, "extract": str}
    """
    summary = _rest_summary(name)
    if summary is None:
        return {"status": "NOT_FOUND"}

    if summary.get("type") == "disambiguation":
        candidates = _disambiguation_candidates(summary.get("title", name))
        if not candidates:
            return {"status": "NOT_FOUND"}
        return {"status": "AMBIGUOUS", "candidates": candidates}

    title = summary.get("title", name)
    info = _action_info_and_extract(title)
    if info is None:
        return {"status": "NOT_FOUND"}

    if info["length_bytes"] < config.FAME_BYTE_THRESHOLD:
        return {"status": "TOO_OBSCURE"}

    return {
        "status": "OK",
        "title": title,
        "length_bytes": info["length_bytes"],
        "extract": info["extract"],
    }


def fame_check_exact_title(title: str) -> dict:
    """Same as fame_check, but for a title already resolved (e.g. a picked
    disambiguation candidate) — skips the disambiguation branch."""
    info = _action_info_and_extract(title)
    if info is None:
        return {"status": "NOT_FOUND"}
    if info["length_bytes"] < config.FAME_BYTE_THRESHOLD:
        return {"status": "TOO_OBSCURE"}
    return {
        "status": "OK",
        "title": title,
        "length_bytes": info["length_bytes"],
        "extract": info["extract"],
    }
