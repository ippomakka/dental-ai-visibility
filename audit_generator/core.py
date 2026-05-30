from __future__ import annotations

import argparse
import html
import json
import re
import sys
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass
from html.parser import HTMLParser
from pathlib import Path
from typing import Any, Iterable

AI_CRAWLERS = ["GPTBot", "OAI-SearchBot", "PerplexityBot", "ClaudeBot", "Googlebot", "Bingbot", "Applebot"]
SERVICE_KEYWORDS = {
    "Invisalign / clear aligners": ["invisalign", "clear aligner", "clear aligners"],
    "Dental implants": ["dental implant", "dental implants", "all-on-4", "all on 4", "full arch"],
    "Orthodontics / braces": ["orthodont", "braces"],
    "Cosmetic dentistry": ["cosmetic", "veneers", "smile makeover", "porcelain veneer"],
    "Emergency dentistry": ["emergency dentist", "emergency dental"],
    "Children's dentistry": ["children dentistry", "children's dentistry", "kids dentist", "paediatric", "pediatric"],
    "General dentistry": ["general dentistry", "check-up", "checkup", "root canal", "wisdom teeth", "gum disease"],
}
LOCATION_PATTERN = re.compile(r"\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+){0,2})\b")
COMMON_NOT_LOCATIONS = {
    "Dental", "Dentist", "Dentistry", "Invisalign", "Clear", "Aligner", "Implants", "Cosmetic",
    "General", "Children", "Root", "Canal", "Wisdom", "Teeth", "Gum", "Disease", "About", "Contact",
    "Home", "Book", "Appointment", "Privacy", "Terms", "Facebook", "Instagram", "Google",
    "Organization", "All", "Json", "Schema", "Website", "Centre", "Clinic",
    "Australia", "Our", "We", "At", "Internet", "Explorer", "Full", "Mouth", "Implants",
    "Full Mouth Implants", "Internet Explorer",
}


@dataclass
class PageSignals:
    url: str
    title: str
    meta_description: str
    h1_count: int
    h1_texts: list[str]
    h2_texts: list[str]
    links: list[str]
    schema_types: list[str]
    schema_blocks: list[dict[str, Any]]
    schema_has_empty_same_as: bool
    schema_warnings: list[str]
    detected_services: list[str]
    detected_locations: list[str]
    has_faq_like_content: bool


@dataclass
class RobotsResult:
    sitemaps: list[str]
    blocks_all: bool
    ai_crawler_access: dict[str, str]


@dataclass
class ScoreCategory:
    score: int
    status: str
    reason: str


@dataclass
class AuditScore:
    overall: int
    categories: dict[str, ScoreCategory]


class SignalHTMLParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.title = ""
        self.meta_description = ""
        self.h1_texts: list[str] = []
        self.h2_texts: list[str] = []
        self.links: list[str] = []
        self.schema_raw: list[str] = []
        self._current: str | None = None
        self._buffer: list[str] = []
        self._in_schema = False
        self._schema_buffer: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attrs_dict = {k.lower(): v or "" for k, v in attrs}
        tag = tag.lower()
        if tag == "title" or tag in {"h1", "h2"}:
            self._current = tag
            self._buffer = []
        if tag == "meta" and attrs_dict.get("name", "").lower() == "description":
            self.meta_description = clean_text(attrs_dict.get("content", ""))
        if tag == "a" and attrs_dict.get("href"):
            self.links.append(attrs_dict["href"])
        if tag == "script" and attrs_dict.get("type", "").lower() == "application/ld+json":
            self._in_schema = True
            self._schema_buffer = []

    def handle_data(self, data: str) -> None:
        if self._in_schema:
            self._schema_buffer.append(data)
        if self._current:
            self._buffer.append(data)

    def handle_endtag(self, tag: str) -> None:
        tag = tag.lower()
        if self._in_schema and tag == "script":
            self.schema_raw.append("".join(self._schema_buffer).strip())
            self._in_schema = False
            self._schema_buffer = []
        if self._current == tag:
            text = clean_text(" ".join(self._buffer))
            if tag == "title" and not self.title:
                self.title = text
            elif tag == "h1" and text:
                self.h1_texts.append(text)
            elif tag == "h2" and text:
                self.h2_texts.append(text)
            self._current = None
            self._buffer = []


def clean_text(value: str) -> str:
    return re.sub(r"\s+", " ", html.unescape(value or "")).strip()


def iter_schema_objects(value: Any) -> Iterable[dict[str, Any]]:
    if isinstance(value, dict):
        if "@graph" in value and isinstance(value["@graph"], list):
            for item in value["@graph"]:
                yield from iter_schema_objects(item)
        yield value
    elif isinstance(value, list):
        for item in value:
            yield from iter_schema_objects(item)


def normalize_schema_type(value: Any) -> list[str]:
    if isinstance(value, str):
        return [value]
    if isinstance(value, list):
        return [str(v) for v in value if v]
    return []


def parse_json_lenient(raw: str) -> Any | None:
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        # Some WordPress plugins leave harmless JS comments/trailing commas. Try light cleanup.
        cleaned = re.sub(r",\s*([}\]])", r"\1", raw)
        try:
            return json.loads(cleaned)
        except json.JSONDecodeError:
            return None


def extract_page_signals(page_html: str, url: str) -> PageSignals:
    parser = SignalHTMLParser()
    parser.feed(page_html)
    visible_text = clean_text(re.sub(r"<[^>]+>", " ", page_html))
    lower_text = visible_text.lower()

    schema_blocks: list[dict[str, Any]] = []
    schema_types: list[str] = []
    schema_warnings: list[str] = []
    schema_has_empty_same_as = False
    for raw in parser.schema_raw:
        parsed = parse_json_lenient(raw)
        if parsed is None:
            schema_warnings.append("A JSON-LD schema block could not be parsed")
            continue
        for obj in iter_schema_objects(parsed):
            schema_blocks.append(obj)
            schema_types.extend(normalize_schema_type(obj.get("@type")))
            if obj.get("sameAs") == []:
                schema_has_empty_same_as = True
            legal_name = str(obj.get("legalName", ""))
            if legal_name and ("admin" in legal_name.lower() or "user" in legal_name.lower() or "_" in legal_name):
                schema_warnings.append("legalName appears to contain an admin/user artifact")

    detected_services = [service for service, terms in SERVICE_KEYWORDS.items() if any(term in lower_text for term in terms)]
    # Location extraction is intentionally conservative: full page text often contains font names,
    # plugin strings and SVG labels that look like places. Title + meta gives cleaner v1 signals.
    detected_locations = detect_locations(" ".join([parser.title, parser.meta_description]))
    has_faq_like_content = bool(re.search(r"\b(faq|frequently asked|how much|how long|is .* suitable|what is)\b", lower_text))

    return PageSignals(
        url=url,
        title=parser.title,
        meta_description=parser.meta_description,
        h1_count=len(parser.h1_texts),
        h1_texts=parser.h1_texts,
        h2_texts=parser.h2_texts,
        links=parser.links[:250],
        schema_types=sorted(set(schema_types)),
        schema_blocks=schema_blocks,
        schema_has_empty_same_as=schema_has_empty_same_as,
        schema_warnings=sorted(set(schema_warnings)),
        detected_services=detected_services,
        detected_locations=detected_locations,
        has_faq_like_content=has_faq_like_content,
    )


def detect_locations(text: str) -> list[str]:
    candidates = []
    explicit_places = ["Campsie", "Villawood"]
    for place in explicit_places:
        if re.search(rf"\b{re.escape(place)}\b", text, flags=re.I):
            candidates.append(place)
    for match in LOCATION_PATTERN.finditer(text):
        candidate = match.group(1).strip()
        candidate = re.sub(r"\s+Australia$", "", candidate).strip()
        first = candidate.split()[0]
        if first in COMMON_NOT_LOCATIONS:
            continue
        if candidate in COMMON_NOT_LOCATIONS:
            continue
        # Keep likely local place names from address/contact context; this intentionally stays conservative.
        around = text[max(0, match.start() - 80): match.end() + 80].lower()
        if any(marker in around for marker in ["nsw", "street", "st ", "place", "clinic", "location", "suburb", "dentist", "dental", "campsie", "villawood"]):
            if candidate not in candidates:
                candidates.append(candidate)
    return candidates[:8]


def parse_robots_txt(robots_txt: str) -> RobotsResult:
    sitemaps: list[str] = []
    blocks_all = False
    rules_by_agent: dict[str, list[tuple[str, str]]] = {}
    current_agents: list[str] = []

    for raw_line in robots_txt.splitlines():
        line = raw_line.split("#", 1)[0].strip()
        if not line or ":" not in line:
            continue
        key, value = [part.strip() for part in line.split(":", 1)]
        key_l = key.lower()
        if key_l == "sitemap":
            sitemaps.append(value)
        elif key_l == "user-agent":
            current_agents = [value]
            rules_by_agent.setdefault(value.lower(), [])
        elif key_l in {"disallow", "allow"}:
            for agent in current_agents or ["*"]:
                rules_by_agent.setdefault(agent.lower(), []).append((key_l, value))
                if agent == "*" and key_l == "disallow" and value == "/":
                    blocks_all = True

    ai_access: dict[str, str] = {}
    for crawler in AI_CRAWLERS:
        agent_rules = rules_by_agent.get(crawler.lower(), rules_by_agent.get("*", []))
        blocked = any(kind == "disallow" and path == "/" for kind, path in agent_rules)
        ai_access[crawler] = "blocked" if blocked else "allowed"
    return RobotsResult(sitemaps=sitemaps, blocks_all=blocks_all, ai_crawler_access=ai_access)


def generate_buyer_prompts(business_name: str, locations: list[str], services: list[str]) -> list[str]:
    locs = locations or ["your city"]
    prompts: list[str] = []
    for location in locs[:3]:
        prompts.append(f"Best dentist in {location}")
        prompts.append(f"Recommend a dental clinic near {location}")
    service_templates = {
        "Invisalign / clear aligners": "Best Invisalign dentist in {location}",
        "Dental implants": "Best dental implants clinic in {location}",
        "Orthodontics / braces": "Best orthodontist for braces in {location}",
        "Cosmetic dentistry": "Best cosmetic dentist in {location}",
        "Emergency dentistry": "Emergency dentist near {location}",
        "Children's dentistry": "Best children's dentist in {location}",
        "General dentistry": "Top-rated family dentist in {location}",
    }
    for service in services:
        template = service_templates.get(service)
        if not template:
            continue
        for location in locs[:2]:
            prompts.append(template.format(location=location))
    prompts.append(f"Is {business_name} a good dental clinic?")
    seen: list[str] = []
    for prompt in prompts:
        if prompt not in seen:
            seen.append(prompt)
    return seen[:16]


def status(score: int) -> str:
    if score >= 75:
        return "strong"
    if score >= 35:
        return "needs work"
    return "missing"


def calculate_score(signals: PageSignals, robots: RobotsResult, has_llms_txt: bool) -> AuditScore:
    clarity = 80
    clarity_reasons = []
    if signals.h1_count == 0:
        clarity -= 35
        clarity_reasons.append("No H1 detected")
    if not signals.meta_description:
        clarity -= 15
        clarity_reasons.append("Missing meta description")
    if len(signals.detected_locations) == 0:
        clarity -= 10
        clarity_reasons.append("No clear location terms detected")

    schema = 75 if signals.schema_types else 25
    schema_reasons = []
    if not signals.schema_types:
        schema_reasons.append("No JSON-LD schema detected")
    if signals.schema_has_empty_same_as:
        schema -= 15
        schema_reasons.append("sameAs is empty")
    if signals.schema_warnings:
        schema -= 15
        schema_reasons.extend(signals.schema_warnings)
    if not any(t in signals.schema_types for t in ["Dentist", "LocalBusiness", "MedicalBusiness"]):
        schema -= 15
        schema_reasons.append("No Dentist/LocalBusiness schema type detected")

    crawl = 85
    crawl_reasons = []
    if robots.blocks_all:
        crawl = 10
        crawl_reasons.append("robots.txt blocks all crawling")
    elif not robots.sitemaps:
        crawl -= 10
        crawl_reasons.append("No sitemap declared in robots.txt")

    profile = 85 if has_llms_txt else 20
    profile_reason = "AI-readable profile found" if has_llms_txt else "No llms.txt or AI-readable profile found"

    service_score = 70 if len(signals.detected_services) >= 2 else 45 if signals.detected_services else 25
    service_reason = f"Detected services: {', '.join(signals.detected_services) or 'none'}"
    if not signals.has_faq_like_content:
        service_score -= 10
        service_reason += "; no obvious FAQ-style content detected"

    categories = {
        "Website clarity": ScoreCategory(max(0, clarity), status(max(0, clarity)), "; ".join(clarity_reasons) or "Homepage basics are clear"),
        "Schema": ScoreCategory(max(0, schema), status(max(0, schema)), "; ".join(schema_reasons) or "Structured data foundation detected"),
        "Crawler access": ScoreCategory(crawl, status(crawl), "; ".join(crawl_reasons) or "Robots rules do not appear to block major crawlers"),
        "AI-readable profile": ScoreCategory(profile, status(profile), profile_reason),
        "Treatment coverage": ScoreCategory(max(0, service_score), status(max(0, service_score)), service_reason),
    }
    overall = round(sum(cat.score for cat in categories.values()) / len(categories))
    return AuditScore(overall=overall, categories=categories)


def generate_markdown_report(
    url: str,
    signals: PageSignals,
    robots: RobotsResult,
    score: AuditScore,
    prompts: list[str],
    has_llms_txt: bool,
) -> str:
    lines: list[str] = []
    lines.append("# AI Visibility Audit")
    lines.append("")
    lines.append(f"**Website:** {url}")
    lines.append("**Niche:** Dental / orthodontic clinic")
    lines.append("**Audit type:** Website AI-readiness snapshot")
    lines.append("")
    lines.append("## Executive Summary")
    lines.append("")
    summary_bits = []
    if signals.h1_count == 0:
        summary_bits.append("No H1 detected on the audited page")
    if signals.schema_warnings or signals.schema_has_empty_same_as:
        summary_bits.append("schema is present but needs cleanup")
    if not has_llms_txt:
        summary_bits.append("no AI-readable business profile / llms.txt was found")
    if signals.detected_locations:
        summary_bits.append(f"location signals detected for {', '.join(signals.detected_locations[:4])}")
    lines.append("This audit checks whether AI search systems can find, understand, verify and recommend the clinic. " + ("Key findings: " + "; ".join(summary_bits) + "." if summary_bits else "The site has a reasonable foundation but should still be validated against live AI prompts."))
    lines.append("")
    lines.append(f"## Overall AI Recommendation Score: **{score.overall}/100**")
    lines.append("")
    lines.append("| Category | Score | Status | Finding |")
    lines.append("|---|---:|---|---|")
    for name, cat in score.categories.items():
        lines.append(f"| {name} | {cat.score}/100 | {cat.status} | {cat.reason} |")
    lines.append("")
    lines.append("## Website Findings")
    lines.append("")
    lines.append(f"- Page title: {signals.title or 'Not detected'}")
    lines.append(f"- Meta description: {signals.meta_description or 'Not detected'}")
    lines.append(f"- H1 count: {signals.h1_count}")
    if signals.h1_count == 0:
        lines.append("- **No H1 detected**. Add a clear homepage H1 that states clinic type, services and locations.")
    if signals.h2_texts:
        lines.append("- H2 examples: " + "; ".join(signals.h2_texts[:5]))
    lines.append("")
    lines.append("## Schema & Entity Findings")
    lines.append("")
    lines.append("- Schema types detected: " + (", ".join(signals.schema_types) if signals.schema_types else "none"))
    if signals.schema_has_empty_same_as:
        lines.append("- `sameAs` is empty. Add trusted profile links such as Google Business Profile, Healthengine/HotDoc, Facebook, Instagram or relevant directories.")
    for warning in signals.schema_warnings:
        lines.append(f"- Warning: {warning}.")
    lines.append("")
    lines.append("## Crawlability")
    lines.append("")
    lines.append("- Sitemaps in robots.txt: " + (", ".join(robots.sitemaps) if robots.sitemaps else "none declared"))
    for crawler, access in robots.ai_crawler_access.items():
        lines.append(f"- {crawler}: {access}")
    lines.append("")
    lines.append("## Service & Location Signals")
    lines.append("")
    lines.append("- Detected services: " + (", ".join(signals.detected_services) if signals.detected_services else "none detected"))
    lines.append("- Detected locations: " + (", ".join(signals.detected_locations) if signals.detected_locations else "none detected"))
    lines.append(f"- AI-readable profile / llms.txt: {'found' if has_llms_txt else 'not found'}")
    lines.append("")
    lines.append("## Buyer Prompt Matrix")
    lines.append("")
    for prompt in prompts:
        lines.append(f"- {prompt}")
    lines.append("")
    lines.append("## 30-Day Fix Plan")
    lines.append("")
    lines.append("1. Add a clear homepage H1 that names the clinic category, core treatments and locations.")
    lines.append("2. Clean and expand Dentist / LocalBusiness schema, including address, phone, opening hours, service area, sameAs links and practitioner data.")
    lines.append("3. Add an AI-readable business profile with `llms.txt`, service summaries, location data and FAQs.")
    lines.append("4. Strengthen treatment + location pages for high-value prompts such as Invisalign, implants, cosmetic dentistry and emergency dentistry.")
    lines.append("5. Add FAQ sections that answer patient-intent questions directly and can be marked up with FAQPage schema.")
    lines.append("6. Compare live AI prompt results against competitors and prioritize third-party trust/citation gaps.")
    lines.append("")
    lines.append("## Note")
    lines.append("")
    lines.append("This is a website AI-readiness snapshot. AI recommendations vary by model, prompt, location, retrieval path and time. The goal is to improve the signals AI systems use to find, understand, verify and recommend the business.")
    return "\n".join(lines) + "\n"


def fetch_url(url: str, timeout: int = 20) -> str | None:
    request = urllib.request.Request(url, headers={"User-Agent": "DentalAIVisibilityAudit/0.1 (+https://dental-ai-visibility.pages.dev/)"})
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            raw = response.read(1_500_000)
            charset = response.headers.get_content_charset() or "utf-8"
            return raw.decode(charset, errors="replace")
    except (urllib.error.URLError, TimeoutError, UnicodeDecodeError):
        return None


def absolute_url(base: str, path: str) -> str:
    return urllib.parse.urljoin(base.rstrip("/") + "/", path.lstrip("/"))


def run_audit(url: str) -> tuple[str, AuditScore]:
    normalized = url if re.match(r"^https?://", url) else "https://" + url
    html_text = fetch_url(normalized)
    if not html_text:
        raise RuntimeError(f"Could not fetch homepage: {normalized}")
    signals = extract_page_signals(html_text, normalized)
    robots_text = fetch_url(absolute_url(normalized, "/robots.txt")) or ""
    robots = parse_robots_txt(robots_text)
    llms_text = fetch_url(absolute_url(normalized, "/llms.txt"))
    has_llms_txt = bool(llms_text and len(llms_text.strip()) > 0 and "<!doctype html" not in llms_text.lower())
    business_name = signals.title.split("|")[0].strip() if signals.title else urllib.parse.urlparse(normalized).netloc
    prompts = generate_buyer_prompts(business_name, signals.detected_locations, signals.detected_services)
    score = calculate_score(signals, robots, has_llms_txt)
    return generate_markdown_report(normalized, signals, robots, score, prompts, has_llms_txt), score


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Generate a dental AI visibility audit report.")
    parser.add_argument("url", help="Website URL to audit")
    parser.add_argument("--output", "-o", help="Markdown report output path")
    args = parser.parse_args(argv)
    report, score = run_audit(args.url)
    if args.output:
        path = Path(args.output)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(report, encoding="utf-8")
        print(f"Wrote audit report to {path} (score {score.overall}/100)")
    else:
        print(report)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
