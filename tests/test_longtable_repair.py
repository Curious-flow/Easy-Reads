import unittest

from paper_tuner import _repair_aastex_longtable_paragraph_cells as repair


class LongtableRepairTests(unittest.TestCase):
    def test_preserves_nested_note_width_and_column_span(self):
        note = r'\textsc{Note}---Flux in 10$^{-20}$ W m$^{-2}$; r=$0\farcs3$.'
        original = r'\multicolumn{6}{p{16.0cm}}{' + note + '}'
        source = '\\documentclass[twocolumn]{aastex7}\n' + (
            r'\begin{longtable}{cccccc}' + original + r'\end{longtable}'
        )
        expected = r'\multicolumn{6}{l}{\parbox[t]{16.0cm}{' + note + '}}'
        self.assertEqual(repair(source), source.replace(original, expected))
        self.assertEqual(repair(repair(source)), repair(source))

    def test_does_not_change_other_journals_or_regular_tables(self):
        cell = r'\multicolumn{6}{p{16.0cm}}{A note}'
        for journal, table in [('mnras', 'longtable'), ('article', 'longtable'),
                               ('aastex7', 'tabular')]:
            with self.subTest(journal=journal, table=table):
                source = ('\\documentclass{' + journal + '}\n'
                          + '\\begin{' + table + '}{cccccc}' + cell
                          + '\\end{' + table + '}')
                self.assertEqual(repair(source), source)

    def test_comments_and_escaped_braces_preserved(self):
        source = (
            '\\documentclass{aastex631}\n\\begin{longtable}{cc}\n'
            '% \\multicolumn{2}{p{4cm}}{Comment only}\n'
            '\\multicolumn{2}{p{4cm}}{Text \\{x\\}, 50\\%\n'
            '% ignored brace }\n'
            '\\textbf{nested text}}\n\\end{longtable}'
        )
        result = repair(source)
        self.assertIn('% \\multicolumn{2}{p{4cm}}{Comment only}', result)
        self.assertIn('Text \\{x\\}, 50\\%\n% ignored brace }\n\\textbf{nested text}', result)
        self.assertIn(r'\multicolumn{2}{l}{\parbox[t]{4cm}{', result)

    def test_nonparagraph_cells_and_malformed_content_left_unchanged(self):
        for cell in (r'\multicolumn{2}{c}{Heading}',
                     r'\multicolumn{2}{p{4cm}}{Unclosed {group}'):
            with self.subTest(cell=cell):
                source = '\\documentclass{aastex7}\n' + (
                    r'\begin{longtable}{cc}' + cell + r'\end{longtable}'
                )
                self.assertEqual(repair(source), source)


if __name__ == '__main__':
    unittest.main()
