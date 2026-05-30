# Audit Generator v1

A lightweight Python audit generator for dental AI visibility audits.

It produces a Markdown report from a clinic website URL by checking:

- homepage title/meta/H1/H2 structure
- visible dental service signals
- location signals from clean title/meta text
- JSON-LD schema types and obvious schema warnings
- robots.txt sitemap and crawler access
- `llms.txt` / AI-readable profile presence
- buyer-intent dental prompt ideas
- weighted AI-readiness score
- 30-day fix plan

## Run an audit

From the repo root:

```bash
python3 -m audit_generator.core https://tcaredental.com.au/ --output reports/tcare-dental-generated-audit.md
```

Print to stdout instead:

```bash
python3 -m audit_generator.core https://example-dental-clinic.com/
```

## Run tests

```bash
python3 -m unittest tests/test_audit_generator.py -v
```

## Current limits

This is a website AI-readiness generator, not the full prompt-monitoring engine yet.

It does **not** currently query ChatGPT, Perplexity, Gemini or Google results to verify whether a clinic appears in live AI answers. That should be the next module.

The current report is still useful because it catches the foundational signals that affect AI discoverability and recommendation confidence:

- crawlability
- schema/entity clarity
- local/treatment clarity
- AI-readable profile gaps
- FAQ/content gaps
- prompt coverage opportunities
