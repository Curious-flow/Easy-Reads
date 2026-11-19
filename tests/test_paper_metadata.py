import unittest

from paper_metadata import extract_printed_date, preserve_original_date, read_original_date


class OriginalDateTests(unittest.TestCase):
    def test_printed_labels_and_small_caps(self):
        examples = {
            'D RAFT VERSION JANUARY 6, 2026': 'January 6, 2026',
            'Preprint 26 October 2018': '26 October 2018',
            'Preprint 6 Oct. 2026': '6 October 2026',
        }
        for printed, expected in examples.items():
            with self.subTest(printed=printed):
                self.assertEqual(extract_printed_date(printed), expected)

    def test_does_not_guess_from_other_dates(self):
        for text in (
            'Received January 6, 2026; Accepted January 7, 2026',
            'arXiv:2601.01540v1 [astro-ph.HE] 6 Jan 2026',
            'Draft version February 30, 2026',
            'Preprint 6 January 2026; Draft version January 7, 2026',
        ):
            with self.subTest(text=text):
                self.assertIsNone(extract_printed_date(text))

    def test_never_fetches_unresolved_latest_version(self):
        result = read_original_date('2601.01540', '')
        self.assertIsNone(result['pdf_url'])
        self.assertIsNone(result['printed_date'])

    def test_explicit_dates_survive_both_paths(self):
        source = (
            '\\documentclass{aastex631}\n'
            '\\date{January 1, 2026}\n'
            '\\received{January 2, 2026}\n'
            '\\revised{January 3, 2026}\n'
            '\\accepted{January 4, 2026}\n'
            '\\begin{document}\n'
        )
        for recovered in ('January 6, 2026', None):
            with self.subTest(recovered=recovered):
                generated = preserve_original_date(source, recovered)
                for line in source.splitlines():
                    self.assertIn(line, generated)
                self.assertEqual(preserve_original_date(generated, recovered), generated)

    def test_author_defined_today_is_preserved(self):
        for definition in (
            r'\renewcommand{\today}{January 1, 2026}',
            r'\def\today{January 1, 2026}',
        ):
            source = '\\documentclass{mnras}\n' + definition + '\n\\begin{document}\n'
            self.assertEqual(preserve_original_date(source, 'January 6, 2026'), source)

    def test_recovery_replaces_old_generated_date_instead_of_accumulating(self):
        source = '\\documentclass{mnras}\n\\begin{document}\n'
        old = preserve_original_date(source, 'January 6, 2026')
        updated = preserve_original_date(old, 'January 7, 2026')
        self.assertNotIn('January 6, 2026', updated)
        self.assertIn(r'\renewcommand{\today}{January 7, 2026}', updated)
        omitted = preserve_original_date(updated, None)
        self.assertNotIn(r'\renewcommand{\today}', omitted)
        self.assertIn(r'\patchcmd{\@printed}{Preprint \tod@y}{}{}{}', omitted)


if __name__ == '__main__':
    unittest.main()
