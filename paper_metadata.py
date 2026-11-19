"""Preserve printed paper dates without substituting arXiv upload metadata."""

import calendar
from datetime import date
import hashlib
import re
import subprocess

import requests


DATE_BLOCK = re.compile(
    r"% === BEGIN EASY READS ORIGINAL DATE ===.*?"
    r"% === END EASY READS ORIGINAL DATE ===[^\n]*\n?",
    re.DOTALL,
)


def extract_printed_date(first_page_text):
    """Accept one valid, unambiguous English date beside a draft/preprint label."""
    compact = re.sub(r"\s+", "", first_page_text).lower()
    months = {}
    for number in range(1, 13):
        months[calendar.month_name[number].lower()] = number
        months[calendar.month_abbr[number].lower()] = number
    month = "(?:" + "|".join(sorted(months, key=len, reverse=True)) + r")\.?"
    day = r"\d{1,2}(?:st|nd|rd|th)?"
    pattern = re.compile(
        r"(?:draftversion|draft|preprint)[:,-]?"
        rf"(?:(?P<month>{month})(?P<day>{day}),?(?P<year>\d{{4}})"
        rf"|(?P<day_first>{day})(?P<month_second>{month}),?(?P<year_last>\d{{4}}))"
        r"(?!\d)"
    )
    found = {}
    for match in pattern.finditer(compact):
        month_first = match['month'] is not None
        month_text = match['month'] or match['month_second']
        day_text = match['day'] or match['day_first']
        try:
            value = date(
                int(match['year'] or match['year_last']),
                months[month_text.rstrip('.')],
                int(re.match(r"\d+", day_text)[0]),
            )
        except ValueError:
            return None
        if month_first:
            rendered = f"{calendar.month_name[value.month]} {value.day}, {value.year}"
        else:
            rendered = f"{value.day} {calendar.month_name[value.month]} {value.year}"
        found[value] = rendered
    return next(iter(found.values())) if len(found) == 1 else None


def read_original_date(paper_id, version):
    """Read only the first PDF page, using the same pinned version as the source."""
    result = {"pdf_url": None, "printed_date": None, "status": "version-unresolved"}
    if not re.fullmatch(r"v\d+", version or ""):
        return result
    result['pdf_url'] = f"https://arxiv.org/pdf/{paper_id}{version}"
    try:
        response = requests.get(result['pdf_url'], timeout=30)
        response.raise_for_status()
        if not response.content.startswith(b"%PDF-"):
            raise ValueError("The original-paper response is not a PDF")
        result['pdf_sha256'] = hashlib.sha256(response.content).hexdigest()
        extracted = subprocess.run(
            ['pdftotext', '-f', '1', '-l', '1', '-layout', '-', '-'],
            input=response.content, capture_output=True, timeout=30,
        )
        if extracted.returncode:
            raise ValueError("Could not extract the original PDF's first page")
        text = extracted.stdout.decode('utf-8', errors='replace')
        # Refuse a redirected/mismatched version if the PDF prints its arXiv ID.
        printed_ids = re.findall(
            r"arxiv:\s*([\w./-]+v\d+)", text, flags=re.IGNORECASE,
        )
        if printed_ids and any(value != paper_id + version for value in printed_ids):
            raise ValueError("The original PDF identifies a different arXiv version")
        result['printed_date'] = extract_printed_date(text)
        result['status'] = 'preserved' if result['printed_date'] else 'date-not-found'
    except (requests.RequestException, OSError, subprocess.TimeoutExpired, ValueError) as error:
        result['status'] = 'unavailable'
        result['reason'] = str(error)
    return result


def preserve_original_date(tex, printed_date=None):
    """Change generated TeX only; keep explicit dates and publication history intact."""
    tex = DATE_BLOCK.sub('', tex)
    # Ignore commented-out commands when detecting the class or author definitions.
    active = re.sub(r"(?<!\\)%[^\n]*", '', tex)
    if re.search(
        r"\\(?:renew|provide|new)command\*?\s*\{?\\today\b|\\(?:g|e|x)?def\s*\\today\b",
        active,
    ):
        print('Keeping the author-supplied definition of \\today')
        return tex
    begin = re.search(r"^[ \t]*\\begin\{document\}", tex, re.MULTILINE)
    if not begin:
        return tex

    if printed_date:
        # Only dates produced by our strict parser may be inserted as TeX.
        if extract_printed_date('Draft version ' + printed_date) != printed_date:
            raise ValueError('Invalid original printed date')
        commands = (
            '% Preserve the original paper\'s printed draft date\n'
            + r'\renewcommand{\today}{' + printed_date + '}\n'
        )
        print(f'Preserving original printed date: {printed_date}')
    else:
        match = re.search(
            r"\\(?:documentclass|documentstyle)(?:\[[^\]]*\])?\{([^}]+)\}", active,
        )
        journal = match[1].strip().lower() if match else ''
        if journal.startswith('aastex'):
            commands = (
                r'\usepackage{etoolbox}' '\n'
                r'\makeatletter' '\n'
                r'\patchcmd{\@journalinfo}{Draft version \today}{}{}{}' '\n'
                + (r'\patchcmd{\frontmatter@title@above}'
                   r'{{\sc Draft version \today}\\[2pt]}{}{}{}' '\n') * 3
                + r'\makeatother' '\n'
            )
        elif journal in ('mnras', 'mn'):
            commands = (
                r'\usepackage{etoolbox}' '\n'
                r'\makeatletter' '\n'
                r'\patchcmd{\@printed}{Preprint \tod@y}{}{}{}' '\n'
                r'\makeatother' '\n'
            )
        else:
            print('No recovered draft date; no known automatic draft-date hook for this class')
            return tex
        commands = '% Omit only the automatic draft/preprint date when recovery fails\n' + commands
        print('Omitting the automatic draft/preprint date; explicit dates retained')

    block = (
        '% === BEGIN EASY READS ORIGINAL DATE ===\n' + commands
        + '% === END EASY READS ORIGINAL DATE ===\n'
    )
    return tex[:begin.start()] + block + tex[begin.start():]
