import unittest

from audit_generator.prompt_testing import (
    SearchResult,
    analyze_prompt_results,
    build_search_query,
    generate_prompt_test_markdown,
    normalize_text,
)


class PromptTestingTests(unittest.TestCase):
    def test_build_search_query_targets_ai_like_buyer_prompt(self):
        query = build_search_query("Best dentist in Campsie", "Campsie")

        self.assertIn("Best dentist in Campsie", query)
        self.assertIn("Campsie", query)
        self.assertIn("dentist", query.lower())

    def test_analyze_prompt_results_detects_target_domain_and_competitors(self):
        results = [
            SearchResult(
                title="TCare Dental Centre - Dentist Campsie",
                url="https://tcaredental.com.au/",
                snippet="Dental clinic in Campsie and Villawood.",
            ),
            SearchResult(
                title="Bupa Dental Campsie",
                url="https://www.bupadental.com.au/campsie",
                snippet="Book a dentist in Campsie.",
            ),
            SearchResult(
                title="No Gaps Dental",
                url="https://www.nogapsdental.com/campsie/",
                snippet="Family dental clinic.",
            ),
        ]

        analysis = analyze_prompt_results(
            prompt="Best dentist in Campsie",
            target_domain="tcaredental.com.au",
            business_name="TCare Dental",
            results=results,
        )

        self.assertTrue(analysis.target_appeared)
        self.assertEqual(analysis.target_position, 1)
        self.assertEqual(analysis.competitors[0].name, "Bupa Dental Campsie")
        self.assertEqual(analysis.competitors[1].domain, "nogapsdental.com")
        self.assertIn("tcaredental.com.au", analysis.sources[0])

    def test_analyze_prompt_results_marks_invisible_when_target_absent(self):
        results = [
            SearchResult(title="Bupa Dental Campsie", url="https://www.bupadental.com.au/campsie", snippet=""),
            SearchResult(title="Pacific Smiles Dental", url="https://www.pacificsmilesdental.com.au/", snippet=""),
        ]

        analysis = analyze_prompt_results(
            prompt="Best dentist in Campsie",
            target_domain="tcaredental.com.au",
            business_name="TCare Dental",
            results=results,
        )

        self.assertFalse(analysis.target_appeared)
        self.assertIsNone(analysis.target_position)
        self.assertEqual(len(analysis.competitors), 2)
        self.assertIn("Target clinic did not appear", analysis.notes[0])

    def test_generate_prompt_test_markdown_contains_matrix_and_competitors(self):
        analysis = analyze_prompt_results(
            prompt="Best dentist in Campsie",
            target_domain="tcaredental.com.au",
            business_name="TCare Dental",
            results=[
                SearchResult(title="Bupa Dental Campsie", url="https://www.bupadental.com.au/campsie", snippet=""),
                SearchResult(title="TCare Dental", url="https://tcaredental.com.au/", snippet=""),
            ],
        )

        markdown = generate_prompt_test_markdown([analysis])

        self.assertIn("# Prompt Visibility Test", markdown)
        self.assertIn("Best dentist in Campsie", markdown)
        self.assertIn("Yes, position 2", markdown)
        self.assertIn("Bupa Dental Campsie", markdown)

    def test_normalize_text_strips_case_and_symbols(self):
        self.assertEqual(normalize_text("TCare Dental® Centre!"), "tcare dental centre")


if __name__ == "__main__":
    unittest.main()
