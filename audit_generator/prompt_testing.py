from __future__ import annotations

import argparse
import html
import json
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import asdict, dataclass
from html.parser import HTMLParser
from pathlib import Path


@dataclass
class SearchResult:
    title: str
    url: str
    snippet: str


@dataclass
class Competitor:
    name: str
    domain: str
    url: str


@dataclass
class PromptAnalysis:
    prompt: str
    target_appeared: bool
    target_position: int | None
    competitors: list[Competitor]
    sources: list[str]
    notes: list[str]
    raw_results: list[SearchResult]


class DuckDuckGoHTMLParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.results: list[SearchResult] = []
        self._in_result_link = False
        self._in_snippet = False
        self._current_title: list[str] = []
        self._current_url = ""
        self._current_snippet: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attrs_dict = {k: v or "" for k, v in attrs}
        classes = attrs_dict.get("class", "")
        if tag == "a" and "result__a" in classes:
            self._flush_if_needed()
            self._in_result_link = True
            self._current_title = []
            self._current_snippet = []
            self._current_url = decode_duckduckgo_url(attrs_dict.get("href", ""))
        elif tag in {"a", "div"} and "result__snippet" in classes:
            self._in_snippet = True

    def handle_data(self, data: str) -> None:
        if self._in_result_link:
            self._current_title.append(data)
        elif self._in_snippet:
            self._current_snippet.append(data)

    def handle_endtag(self, tag: str) -> None:
        if tag == "a" and self._in_result_link:
            self._in_result_link = False
        elif tag in {"a", "div"} and self._in_snippet:
            self._in_snippet = False
            self._flush_if_needed()

    def close(self) -> None:
        self._flush_if_needed()
        super().close()

    def _flush_if_needed(self) -> None:
        title = clean(" ".join(self._current_title))
        if not title or not self._current_url:
            return
        snippet = clean(" ".join(self._current_snippet))
        if self.results and self.results[-1].title == title and self.results[-1].url == self._current_url:
            if snippet and not self.results[-1].snippet:
                self.results[-1].snippet = snippet
        else:
            self.results.append(SearchResult(title=title, url=self._current_url, snippet=snippet))
        self._current_title = []
        self._current_snippet = []
        self._current_url = ""


def clean(value: str) -> str:
    return re.sub(r"\s+", " ", html.unescape(value or "")).strip()


def normalize_text(value: str) -> str:
    value = html.unescape(value or "").lower()
    value = re.sub(r"[®™©]", "", value)
    value = re.sub(r"[^a-z0-9]+", " ", value)
    return re.sub(r"\s+", " ", value).strip()


def extract_domain(url: str) -> str:
    parsed = urllib.parse.urlparse(url if re.match(r"^https?://", url) else "https://" + url)
    domain = parsed.netloc.lower()
    if domain.startswith("www."):
        domain = domain[4:]
    return domain


def decode_duckduckgo_url(url: str) -> str:
    if url.startswith("//"):
        url = "https:" + url
    parsed = urllib.parse.urlparse(url)
    query = urllib.parse.parse_qs(parsed.query)
    if "uddg" in query and query["uddg"]:
        return query["uddg"][0]
    return url


def build_search_query(prompt: str, location: str | None = None) -> str:
    parts = [prompt]
    if location and normalize_text(location) not in normalize_text(prompt):
        parts.append(location)
    # Search fallback approximates answer-source visibility: what public pages are likely retrievable/citable.
    parts.append("dentist reviews")
    return " ".join(parts)


def parse_duckduckgo_results(body: str, max_results: int = 8) -> list[SearchResult]:
    parser = DuckDuckGoHTMLParser()
    parser.feed(body)
    parser.close()
    deduped: list[SearchResult] = []
    seen: set[str] = set()
    for result in parser.results:
        key = result.url
        if key in seen:
            continue
        seen.add(key)
        deduped.append(result)
        if len(deduped) >= max_results:
            break
    return deduped


def parse_bing_results(body: str, max_results: int = 8) -> list[SearchResult]:
    results: list[SearchResult] = []
    blocks = re.findall(r'<li[^>]+class="[^"]*b_algo[^"]*"[^>]*>(.*?)</li>', body, flags=re.I | re.S)
    for block in blocks:
        link = re.search(r'<h2[^>]*>\s*<a[^>]+href="([^"]+)"[^>]*>(.*?)</a>\s*</h2>', block, flags=re.I | re.S)
        if not link:
            continue
        url = html.unescape(link.group(1))
        title = clean(re.sub(r"<[^>]+>", " ", link.group(2)))
        snippet_match = re.search(r'<(?:div[^>]+class="[^"]*b_caption[^"]*"[^>]*>\s*)?<p[^>]*>(.*?)</p>', block, flags=re.I | re.S)
        snippet = clean(re.sub(r"<[^>]+>", " ", snippet_match.group(1))) if snippet_match else ""
        results.append(SearchResult(title=title, url=url, snippet=snippet))
        if len(results) >= max_results:
            break
    return results


def search_duckduckgo(query: str, max_results: int = 8, timeout: int = 20) -> list[SearchResult]:
    encoded = urllib.parse.urlencode({"q": query})
    url = f"https://html.duckduckgo.com/html/?{encoded}"
    request = urllib.request.Request(
        url,
        headers={
            "User-Agent": "Mozilla/5.0 (compatible; DentalAIVisibilityAudit/0.1)",
            "Accept": "text/html,application/xhtml+xml",
        },
    )
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            body = response.read(1_000_000).decode(response.headers.get_content_charset() or "utf-8", errors="replace")
    except (urllib.error.URLError, TimeoutError):
        return []
    return parse_duckduckgo_results(body, max_results=max_results)


def search_bing(query: str, max_results: int = 8, timeout: int = 20) -> list[SearchResult]:
    encoded = urllib.parse.urlencode({"q": query})
    url = f"https://www.bing.com/search?{encoded}"
    request = urllib.request.Request(
        url,
        headers={
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml",
        },
    )
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            body = response.read(1_000_000).decode(response.headers.get_content_charset() or "utf-8", errors="replace")
    except (urllib.error.URLError, TimeoutError):
        return []
    return parse_bing_results(body, max_results=max_results)


def is_junk_result(result: SearchResult) -> bool:
    domain = extract_domain(result.url)
    title = normalize_text(result.title)
    junk_domains = {
        "bing.com", "merriam-webster.com", "dictionary.com", "cambridge.org", "collinsdictionary.com",
        "wordreference.com", "usdictionary.com",
    }
    if domain in junk_domains:
        return True
    if "definition" in title and "dentist" not in title and "dental" not in title:
        return True
    return False


def search_web(query: str, max_results: int = 8) -> list[SearchResult]:
    results = [result for result in search_duckduckgo(query, max_results=max_results) if not is_junk_result(result)]
    if results:
        return results
    return [result for result in search_bing(query, max_results=max_results * 2) if not is_junk_result(result)][:max_results]


def result_mentions_target(result: SearchResult, target_domain: str, business_name: str) -> bool:
    target = extract_domain(target_domain)
    result_domain = extract_domain(result.url)
    if result_domain == target or result_domain.endswith("." + target):
        return True
    business_tokens = [token for token in normalize_text(business_name).split() if len(token) > 2]
    haystack = normalize_text(" ".join([result.title, result.snippet, result.url]))
    return bool(business_tokens and all(token in haystack for token in business_tokens[:3]))


def competitor_name_from_title(title: str) -> str:
    title = re.split(r"[|–—-]", title)[0]
    return clean(title)[:80] or "Unknown competitor"


def analyze_prompt_results(prompt: str, target_domain: str, business_name: str, results: list[SearchResult]) -> PromptAnalysis:
    target_position: int | None = None
    competitors: list[Competitor] = []
    sources: list[str] = []
    target = extract_domain(target_domain)

    for idx, result in enumerate(results, start=1):
        domain = extract_domain(result.url)
        sources.append(f"{domain} — {result.title}")
        if result_mentions_target(result, target, business_name):
            if target_position is None:
                target_position = idx
            continue
        if domain and domain != target:
            competitors.append(Competitor(name=competitor_name_from_title(result.title), domain=domain, url=result.url))

    # De-dupe competitors by domain.
    unique_competitors: list[Competitor] = []
    seen_domains: set[str] = set()
    for competitor in competitors:
        if competitor.domain in seen_domains:
            continue
        seen_domains.add(competitor.domain)
        unique_competitors.append(competitor)

    notes: list[str] = []
    if target_position is None:
        if results:
            notes.append("Target clinic did not appear in the retrieved results for this prompt.")
        else:
            notes.append("No reliable search results were retrieved automatically for this prompt.")
    elif target_position <= 3:
        notes.append("Target clinic appeared in the top 3 retrieved results for this prompt.")
    else:
        notes.append("Target clinic appeared, but below the strongest visible results.")
    if unique_competitors:
        notes.append("Competitor/source domains appeared before or alongside the target clinic.")
    return PromptAnalysis(
        prompt=prompt,
        target_appeared=target_position is not None,
        target_position=target_position,
        competitors=unique_competitors[:5],
        sources=sources[:8],
        notes=notes,
        raw_results=results,
    )


def generate_prompt_test_markdown(analyses: list[PromptAnalysis]) -> str:
    lines: list[str] = []
    lines.append("# Prompt Visibility Test")
    lines.append("")
    lines.append("This is a search-backed visibility snapshot. It approximates which public pages and competitors are most retrievable/citable for each buyer-intent prompt. It is not a guaranteed ChatGPT ranking report.")
    lines.append("")
    lines.append("| Prompt | Target appeared? | Top competitors / sources | Notes |")
    lines.append("|---|---|---|---|")
    for analysis in analyses:
        appeared = f"Yes, position {analysis.target_position}" if analysis.target_appeared else "No"
        competitors = ", ".join(f"{c.name} ({c.domain})" for c in analysis.competitors[:3]) or "None detected"
        notes = " ".join(analysis.notes)
        lines.append(f"| {analysis.prompt} | {appeared} | {competitors} | {notes} |")
    lines.append("")
    lines.append("## Sources by Prompt")
    for analysis in analyses:
        lines.append("")
        lines.append(f"### {analysis.prompt}")
        for source in analysis.sources:
            lines.append(f"- {source}")
    return "\n".join(lines) + "\n"


def load_prompt_results_fixture(path: str | Path) -> dict[str, list[SearchResult]]:
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    fixture: dict[str, list[SearchResult]] = {}
    for prompt, rows in payload.items():
        fixture[prompt] = [
            SearchResult(
                title=str(row.get("title", "")),
                url=str(row.get("url", "")),
                snippet=str(row.get("snippet", "")),
            )
            for row in rows
        ]
    return fixture


def run_prompt_tests(prompts: list[str], target_domain: str, business_name: str, delay_seconds: float = 1.0, fixture_path: str | None = None) -> list[PromptAnalysis]:
    fixture = load_prompt_results_fixture(fixture_path) if fixture_path else {}
    analyses: list[PromptAnalysis] = []
    for prompt in prompts:
        if prompt in fixture:
            results = fixture[prompt]
        else:
            query = build_search_query(prompt)
            results = search_web(query)
        analyses.append(analyze_prompt_results(prompt, target_domain, business_name, results))
        if delay_seconds and not fixture_path:
            time.sleep(delay_seconds)
    return analyses


def analyses_to_json(analyses: list[PromptAnalysis]) -> str:
    return json.dumps([asdict(analysis) for analysis in analyses], indent=2)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run search-backed prompt visibility tests.")
    parser.add_argument("--target-domain", required=True, help="Target clinic domain, e.g. tcaredental.com.au")
    parser.add_argument("--business-name", required=True, help="Business name to match in result titles/snippets")
    parser.add_argument("--prompt", action="append", required=True, help="Buyer prompt to test. Can be passed multiple times.")
    parser.add_argument("--output", "-o", help="Markdown output path")
    parser.add_argument("--json-output", help="Optional JSON output path")
    parser.add_argument("--delay", type=float, default=1.0, help="Delay between searches in seconds")
    parser.add_argument("--fixture", help="Optional JSON fixture mapping prompts to search/AI results")
    args = parser.parse_args(argv)

    analyses = run_prompt_tests(args.prompt, args.target_domain, args.business_name, delay_seconds=args.delay, fixture_path=args.fixture)
    markdown = generate_prompt_test_markdown(analyses)
    if args.output:
        output = Path(args.output)
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(markdown, encoding="utf-8")
        print(f"Wrote prompt visibility report to {output}")
    else:
        print(markdown)
    if args.json_output:
        json_output = Path(args.json_output)
        json_output.parent.mkdir(parents=True, exist_ok=True)
        json_output.write_text(analyses_to_json(analyses), encoding="utf-8")
        print(f"Wrote prompt visibility JSON to {json_output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
