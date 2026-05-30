# Prompt Testing v1

Prompt Testing v1 adds the "who appears for buyer prompts?" layer to the audit generator.

It can:

- accept buyer-intent prompts
- retrieve public search results via a lightweight DuckDuckGo/Bing fallback
- filter obvious junk search results
- detect whether the target clinic appears
- extract competitor/source domains
- output a Markdown prompt visibility matrix
- output structured JSON
- accept a fixture/manual-source JSON file when scraping is unreliable or when results come from Perplexity/ChatGPT/Search APIs

## Important reality check

Public search result scraping is unreliable in this environment. Search engines can return bot-blocked, empty, or irrelevant dictionary-style pages.

The module is intentionally conservative:

- if it cannot retrieve reliable results, it says so
- it does not invent competitors
- it does not pretend a search scrape is a guaranteed ChatGPT ranking

For production-quality prompt testing, connect one of:

- Perplexity API
- SerpAPI / DataForSEO / Brave Search API
- Google Custom Search / Programmable Search
- a browser automation worker with residential/proxy support
- manual/fixture import from real AI-search captures

## Run automated prompt test

```bash
python3 -m audit_generator.prompt_testing \
  --target-domain tcaredental.com.au \
  --business-name "TCare Dental" \
  --prompt "Best dentist in Campsie" \
  --prompt "Best Invisalign dentist in Campsie" \
  --output reports/tcare-dental-prompt-visibility.md \
  --json-output reports/tcare-dental-prompt-visibility.json
```

## Fixture/manual-source mode

Create a JSON file mapping each prompt to result rows:

```json
{
  "Best dentist in Campsie": [
    {
      "title": "Example Dental Clinic Campsie",
      "url": "https://example.com/campsie-dentist",
      "snippet": "A dental clinic result shown by the search/AI provider."
    },
    {
      "title": "TCare Dental Centre",
      "url": "https://tcaredental.com.au/",
      "snippet": "TCare Dental Centre provides dentistry in Campsie and Villawood."
    }
  ]
}
```

Run:

```bash
python3 -m audit_generator.prompt_testing \
  --target-domain tcaredental.com.au \
  --business-name "TCare Dental" \
  --prompt "Best dentist in Campsie" \
  --fixture reports/manual-prompt-results.json \
  --output reports/prompt-visibility-from-fixture.md
```

This mode is useful when results are collected from Perplexity, ChatGPT browsing, Google, DataForSEO, SerpAPI, or a human-reviewed search capture.
