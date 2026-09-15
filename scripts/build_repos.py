#!/usr/bin/env python3
"""Generate the "All public repositories" HTML fragment for software.html.

Reads jon-chun's public non-fork repositories from the GitHub REST API
(or from a local JSON file with --from-file) and prints an HTML fragment
of categorised <section> blocks to stdout. Standard library only.

Usage:
    python3 scripts/build_repos.py > /tmp/repos.html
    python3 scripts/build_repos.py --from-file repos.json
    python3 scripts/build_repos.py --user jon-chun --token "$GITHUB_TOKEN"

Paste the output into software.html between the
<!-- BEGIN all-repos --> and <!-- END all-repos --> markers.
"""

import argparse
import html
import json
import os
import sys
import urllib.error
import urllib.request

API = "https://api.github.com/users/{user}/repos?per_page=100&page={page}&type=owner&sort=full_name"

# Repos whose names match these rules are scaffolding, not work worth listing.
EXCLUDE_PREFIXES = ("test-", "demo-", "sample", "remote-test")
EXCLUDE_SUBSTRINGS = ("-copy",)

# Exact names that are scaffolding but do not match the prefix rules.
EXCLUDE_NAMES = ("actions-test", "test_multi", "jon-chun")

# Ordered category list. The first category whose keywords match a repo's
# name, description or topics wins, so put the specific ones first.
CATEGORIES = [
    (
        "SentimentArcs & Narrative",
        (
            "sentimentarc", "sentiment_arc", "sentiment-arc", "narrative",
            "story", "stories", "novel", "plot", "literary", "literature",
            "sentiment", "poetry", "screenplay", "script", "play",
            "film", "shakespeare", "kafka", "proust", "woolf", "chekhov",
            "augustine", "confessions", "comedy", "sitcom",
            "diachronic", "emotion", "affect", "arc", "nabokov",
            "palefire", "gatsby", "creative", "engl", "text-analysis",
            "music", "haiku",
        ),
    ),
    (
        "AI Evaluation, Safety & Policy",
        (
            "audit", "ethic", "safety", "align", "bias", "fair", "regulat",
            "policy", "governance", "benchmark", "eval", "red-team",
            "redteam", "robust", "negation", "framing", "recidivism",
            "tom-", "theory-of-mind", "calibrat", "madcal", "cei-",
            "trust", "risk", "privacy", "security",
        ),
    ),
    (
        "Agents & LLM Tooling",
        (
            "agent", "agentic", "multi-agent", "llm", "gpt", "rag",
            "prompt", "chatbot", "chat-", "openai", "langchain", "ollama",
            "transformer", "finetune", "fine-tune", "embedding", "vector",
            "digital-twin", "digital_twin", "mcp", "workflow", "autogen",
            "crew", "gemini", "claude", "anthropic", "diffusion",
            "nlp", "spacy", "tokeniz", "translat", "linguist", "lexic",
            "speech", "whisper", "vision", "multimodal",
        ),
    ),
    (
        "Courses & Teaching",
        (
            "iphs", "course", "teaching", "curriculum", "syllabus",
            "workshop", "tutorial", "lesson", "class", "student",
            "cultural-analytics", "cultural_analytics", "frontiers",
            "programming-humanity", "programminghumanity", "seminar",
            "bootcamp", "intro", "learn", "kenyon", "2020spr", "2021spr",
            "2022spr", "2019fall", "2020fall", "2021fall", "2022fall",
            "mastering-", "digital_humanities", "digital-humanities",
            "mla-",
        ),
    ),
    (
        "Data Collection & Scraping",
        (
            "scrap", "crawl", "spider", "download", "harvest", "corpus",
            "dataset", "data-collect", "api-", "youtube", "reddit",
            "twitter", "wikipedia", "archive", "ocr", "etl", "pipeline",
            "ingest",
        ),
    ),
]

FALLBACK_CATEGORY = "Dev Tooling & Misc"


def fetch(user: str, token: str | None) -> list[dict]:
    """Page through the GitHub repos API and return every repo object."""
    repos: list[dict] = []
    for page in range(1, 11):
        req = urllib.request.Request(
            API.format(user=user, page=page),
            headers={
                "Accept": "application/vnd.github+json",
                "User-Agent": "build_repos.py",
                **({"Authorization": f"Bearer {token}"} if token else {}),
            },
        )
        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                batch = json.load(resp)
        except urllib.error.HTTPError as exc:
            sys.exit(f"GitHub API error {exc.code}: {exc.reason}")
        except urllib.error.URLError as exc:
            sys.exit(f"Network error: {exc.reason}")
        if not batch:
            break
        repos.extend(batch)
        if len(batch) < 100:
            break
    return repos


def keep(repo: dict) -> bool:
    """True if the repo belongs in the public listing."""
    if repo.get("fork") or repo.get("archived") or repo.get("private"):
        return False
    name = (repo.get("name") or "").lower()
    if name.startswith(EXCLUDE_PREFIXES) or name in EXCLUDE_NAMES:
        return False
    if any(sub in name for sub in EXCLUDE_SUBSTRINGS):
        return False
    if repo.get("size", 1) == 0:
        return False
    return True


def categorise(repo: dict) -> str:
    """Return the category name for a repo."""
    haystack = " ".join(
        [
            (repo.get("name") or "").lower(),
            (repo.get("description") or "").lower(),
            " ".join(repo.get("topics") or []).lower(),
        ]
    )
    for label, keywords in CATEGORIES:
        if any(word in haystack for word in keywords):
            return label
    return FALLBACK_CATEGORY


def render(repos: list[dict]) -> str:
    """Render grouped repositories as an HTML fragment."""
    groups: dict[str, list[dict]] = {label: [] for label, _ in CATEGORIES}
    groups[FALLBACK_CATEGORY] = []
    for repo in repos:
        groups[categorise(repo)].append(repo)

    lines: list[str] = []
    for label in list(groups):
        items = sorted(
            groups[label],
            key=lambda r: (-(r.get("stargazers_count") or 0), (r.get("name") or "").lower()),
        )
        if not items:
            continue
        slug = label.lower().replace(" & ", "-").replace(" ", "-").replace(",", "")
        lines.append(f'        <section class="repo-group" aria-labelledby="rg-{slug}">')
        lines.append(
            f'          <h3 id="rg-{slug}">{html.escape(label)} '
            f'<span class="repo-count">{len(items)}</span></h3>'
        )
        lines.append('          <ul class="repo-list">')
        for repo in items:
            url = html.escape(repo["html_url"], quote=True)
            name = html.escape(repo["name"])
            desc = html.escape((repo.get("description") or "").strip())
            meta: list[str] = []
            if repo.get("language"):
                meta.append(
                    f'<span class="repo-lang">{html.escape(repo["language"])}</span>'
                )
            stars = repo.get("stargazers_count") or 0
            if stars:
                meta.append(
                    f'<span class="repo-stars">{stars} star{"s" if stars != 1 else ""}</span>'
                )
            lines.append("            <li>")
            lines.append(
                f'              <a href="{url}" rel="noopener">{name}</a>'
            )
            if desc:
                lines.append(f'              <span class="repo-desc">{desc}</span>')
            if meta:
                lines.append(
                    f'              <span class="repo-meta">{" ".join(meta)}</span>'
                )
            lines.append("            </li>")
        lines.append("          </ul>")
        lines.append("        </section>")
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--user", default="jon-chun", help="GitHub username")
    parser.add_argument("--from-file", help="read a JSON array of repos instead of calling the API")
    parser.add_argument(
        "--token",
        default=os.environ.get("GITHUB_TOKEN"),
        help="GitHub token (optional; raises the rate limit)",
    )
    args = parser.parse_args()

    if args.from_file:
        with open(args.from_file, encoding="utf-8") as handle:
            repos = json.load(handle)
    else:
        repos = fetch(args.user, args.token)

    kept = [r for r in repos if keep(r)]
    print(f"<!-- generated by scripts/build_repos.py: {len(kept)} repositories -->")
    print(render(kept))
    print(f"<!-- {len(repos) - len(kept)} repositories excluded (archived, empty or scaffolding) -->", file=sys.stderr)


if __name__ == "__main__":
    main()
