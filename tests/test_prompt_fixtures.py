import json
import tempfile
import unittest
from pathlib import Path

from audit_generator.prompt_testing import SearchResult, load_prompt_results_fixture


class PromptFixtureTests(unittest.TestCase):
    def test_load_prompt_results_fixture_maps_prompt_to_results(self):
        payload = {
            "Best dentist in Campsie": [
                {"title": "TCare Dental", "url": "https://tcaredental.com.au/", "snippet": "Dentist in Campsie"}
            ]
        }
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "fixture.json"
            path.write_text(json.dumps(payload), encoding="utf-8")

            loaded = load_prompt_results_fixture(path)

        self.assertEqual(loaded["Best dentist in Campsie"][0], SearchResult("TCare Dental", "https://tcaredental.com.au/", "Dentist in Campsie"))


if __name__ == "__main__":
    unittest.main()
