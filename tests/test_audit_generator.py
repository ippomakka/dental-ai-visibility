import unittest

from audit_generator.core import (
    calculate_score,
    extract_page_signals,
    generate_buyer_prompts,
    generate_markdown_report,
    parse_robots_txt,
)


SAMPLE_HTML = """
<!doctype html>
<html>
<head>
  <title>TCare Dental Centre | Dentist Campsie & Villawood</title>
  <meta name="description" content="Dental implants, Invisalign and general dentistry in Campsie and Villawood.">
  <script type="application/ld+json">
  {
    "@context": "https://schema.org",
    "@type": ["Dentist", "Organization"],
    "name": "TCare Dental",
    "legalName": "cb_james_admin",
    "sameAs": []
  }
  </script>
</head>
<body>
  <h2>Dentistry With Heart</h2>
  <a href="/clear-aligner/">Invisalign Clear Aligner</a>
  <a href="/all-on-4-implants/">All-on-4 Dental Implants</a>
  <a href="/contact/">Campsie and Villawood</a>
</body>
</html>
"""


class AuditGeneratorTests(unittest.TestCase):
    def test_extract_page_signals_detects_missing_h1_schema_and_services(self):
        signals = extract_page_signals(SAMPLE_HTML, "https://tcaredental.com.au/")

        self.assertEqual(signals.title, "TCare Dental Centre | Dentist Campsie & Villawood")
        self.assertEqual(signals.h1_count, 0)
        self.assertIn("Dentist", signals.schema_types)
        self.assertIn("Organization", signals.schema_types)
        self.assertTrue(signals.schema_has_empty_same_as)
        self.assertIn("legalName appears to contain an admin/user artifact", signals.schema_warnings)
        self.assertIn("Invisalign / clear aligners", signals.detected_services)
        self.assertIn("Dental implants", signals.detected_services)
        self.assertIn("Campsie", signals.detected_locations)
        self.assertIn("Villawood", signals.detected_locations)

    def test_parse_robots_txt_flags_ai_crawlers_as_allowed_when_not_blocked(self):
        robots = """User-agent: *
Disallow: /wp-admin/
Allow: /wp-admin/admin-ajax.php
Sitemap: https://example.com/sitemap.xml
"""

        result = parse_robots_txt(robots)

        self.assertEqual(result.sitemaps, ["https://example.com/sitemap.xml"])
        self.assertFalse(result.blocks_all)
        self.assertEqual(result.ai_crawler_access["GPTBot"], "allowed")
        self.assertEqual(result.ai_crawler_access["PerplexityBot"], "allowed")
        self.assertEqual(result.ai_crawler_access["ClaudeBot"], "allowed")

    def test_generate_buyer_prompts_for_dental_location_and_services(self):
        prompts = generate_buyer_prompts(
            business_name="TCare Dental",
            locations=["Campsie", "Villawood"],
            services=["Invisalign / clear aligners", "Dental implants"],
        )

        self.assertIn("Best dentist in Campsie", prompts)
        self.assertIn("Best dentist in Villawood", prompts)
        self.assertIn("Best Invisalign dentist in Campsie", prompts)
        self.assertIn("Best dental implants clinic in Villawood", prompts)
        self.assertLessEqual(len(prompts), 16)

    def test_calculate_score_penalizes_missing_h1_and_incomplete_schema(self):
        signals = extract_page_signals(SAMPLE_HTML, "https://tcaredental.com.au/")
        score = calculate_score(signals=signals, robots=parse_robots_txt("User-agent: *\n"), has_llms_txt=False)

        self.assertLess(score.overall, 70)
        self.assertEqual(score.categories["Website clarity"].status, "needs work")
        self.assertEqual(score.categories["Schema"].status, "needs work")
        self.assertEqual(score.categories["AI-readable profile"].status, "missing")

    def test_generate_markdown_report_contains_concrete_findings_and_fix_plan(self):
        signals = extract_page_signals(SAMPLE_HTML, "https://tcaredental.com.au/")
        score = calculate_score(signals=signals, robots=parse_robots_txt("User-agent: *\n"), has_llms_txt=False)
        report = generate_markdown_report(
            url="https://tcaredental.com.au/",
            signals=signals,
            robots=parse_robots_txt("User-agent: *\nSitemap: https://tcaredental.com.au/sitemap.xml\n"),
            score=score,
            prompts=generate_buyer_prompts("TCare Dental", signals.detected_locations, signals.detected_services),
            has_llms_txt=False,
        )

        self.assertIn("# AI Visibility Audit", report)
        self.assertIn("Overall AI Recommendation Score", report)
        self.assertIn("No H1 detected", report)
        self.assertIn("Add a clear homepage H1", report)
        self.assertIn("Add an AI-readable business profile", report)
        self.assertIn("Best dentist in Campsie", report)


if __name__ == "__main__":
    unittest.main()
