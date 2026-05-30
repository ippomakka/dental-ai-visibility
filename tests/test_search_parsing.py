import unittest

from audit_generator.prompt_testing import parse_bing_results, parse_duckduckgo_results


class PromptSearchParsingTests(unittest.TestCase):
    def test_parse_duckduckgo_results_extracts_titles_urls_and_snippets(self):
        html = '''
        <a rel="nofollow" class="result__a" href="//duckduckgo.com/l/?uddg=https%3A%2F%2Ftcaredental.com.au%2F">TCare Dental Centre</a>
        <a class="result__snippet">Dental clinic in Campsie.</a>
        '''

        results = parse_duckduckgo_results(html)

        self.assertEqual(results[0].title, "TCare Dental Centre")
        self.assertEqual(results[0].url, "https://tcaredental.com.au/")
        self.assertEqual(results[0].snippet, "Dental clinic in Campsie.")

    def test_parse_bing_results_extracts_titles_urls_and_snippets(self):
        html = '''
        <li class="b_algo">
          <h2><a href="https://www.bupadental.com.au/campsie">Bupa Dental Campsie</a></h2>
          <div class="b_caption"><p>Book a dentist in Campsie.</p></div>
        </li>
        <li class="b_algo">
          <h2><a href="https://tcaredental.com.au/">TCare Dental Centre</a></h2>
          <p>Dental clinic in Campsie and Villawood.</p>
        </li>
        '''

        results = parse_bing_results(html)

        self.assertEqual(len(results), 2)
        self.assertEqual(results[0].title, "Bupa Dental Campsie")
        self.assertEqual(results[0].url, "https://www.bupadental.com.au/campsie")
        self.assertEqual(results[0].snippet, "Book a dentist in Campsie.")
        self.assertEqual(results[1].title, "TCare Dental Centre")


if __name__ == "__main__":
    unittest.main()
