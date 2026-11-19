import re
import os
from paper_metadata import preserve_original_date


TUNING_BLOCK_TEMPLATE = r"""
% === BEGIN AUTO FONT/FIG TUNING (inserted by script) =========================

\newcommand{\BaseFontSizePt}{__BASE_FONT_PT__pt}
\newcommand{\BaseBaselineSkipPt}{__BASELINE_PT__pt}

% === EASY_READS Font override =================

\makeatletter
\renewcommand\normalsize{
    \@setfontsize\normalsize{\BaseFontSizePt}{\BaseBaselineSkipPt}
}
\normalsize
\makeatother
% =====================================================
% === END AUTO FONT/FIG TUNING ================================================
""".lstrip("\n")

# Margin tuning for single-column mode
# Load geometry package with explicit margins to override AASTeX defaults
SINGLE_COLUMN_MARGIN_TEMPLATE = r"""
\usepackage[left=__MARGIN_IN__in,right=__MARGIN_IN__in,top=1in,bottom=1in]{geometry}
""".lstrip("\n")

# Use \newgeometry{} command to reset margins after document starts
SINGLE_COLUMN_GEOMETRY_RESET = r"""
\newgeometry{left=__MARGIN_IN__in,right=__MARGIN_IN__in,top=1in,bottom=1in}
""".lstrip("\n")

def _normalize_pt_value(value) -> str:
    """Return a numeric string for TeX point dimensions (without the 'pt' suffix)."""
    text = str(value).strip()
    if text.lower().endswith("pt"):
        text = text[:-2].strip()
    return text


def _repair_mnras_author_footnotes(tex: str) -> str:
    """Move simple author footnotes out of superscript math in MNRAS sources."""
    if not re.search(
        r"^[ \t]*\\documentclass(?:\[[^\]]*\])?\{mnras\}", tex, re.MULTILINE
    ):
        return tex

    author = re.search(r"^[ \t]*\\author(?:\[[^\]]*\])?\{", tex, re.MULTILINE)
    if not author:
        return tex

    # Locate the complete author argument, including nested TeX groups.
    start = author.end()
    depth, end = 1, start
    while end < len(tex) and depth:
        if tex[end] == "\\":
            end += 2
            continue
        if tex[end] == "%":
            newline = tex.find("\n", end)
            end = len(tex) if newline == -1 else newline + 1
            continue
        if tex[end] == "{":
            depth += 1
        elif tex[end] == "}":
            depth -= 1
        end += 1
    if depth:
        return tex

    author_text = tex[start:end - 1]
    author_text = re.sub(
        r"(\$\^\{[^{}$\n]+\})(\\thanks\{[^{}\n]*\})([ \t]*,?)[ \t]*\$",
        lambda match: match[1] + "$" + match[2] + match[3],
        author_text,
    )
    return tex[:start] + author_text + tex[end - 1:]


def set_tuning_values_newfile(
    tex_path: str,
    base_font_pt=None,
    baseline_pt=None,
    single_column: bool = False,
    single_column_margin=None,
    original_printed_date=None,
) -> str:
    with open(tex_path, "r", encoding="utf-8", errors="ignore") as f:
        tex = f.read()

    tex = _repair_mnras_author_footnotes(tex)

    resolved_base_font_pt = 12 if base_font_pt is None else base_font_pt
    if baseline_pt is None:
        resolved_baseline_pt = 1.2 * float(_normalize_pt_value(resolved_base_font_pt))
    else:
        resolved_baseline_pt = baseline_pt

    base_font_pt_text = _normalize_pt_value(resolved_base_font_pt)
    baseline_pt_text = _normalize_pt_value(resolved_baseline_pt)

    tuned_block = (
        TUNING_BLOCK_TEMPLATE
        .replace("__BASE_FONT_PT__", base_font_pt_text)
        .replace("__BASELINE_PT__", baseline_pt_text)
    )

    block_pattern = re.compile(
        r"(% === BEGIN AUTO FONT/FIG TUNING.*?% === END AUTO FONT/FIG TUNING[^\n]*\n?)",
        flags=re.DOTALL,
    )
    block_match = block_pattern.search(tex)
    
    if not block_match:
        m = re.search(
            r"^[ \t]*\\(?:documentclass|documentstyle)(?:\[[^\]]*\])?\{[^\}]+\}",
            tex,
            flags=re.MULTILINE,
        )
        if m:
            new_tex = tex[: m.end()] + "\n" + tuned_block + "\n" + tex[m.end():]
        else:
            new_tex = tuned_block + "\n" + tex
    else:
        new_tex = tex[: block_match.start()] + tuned_block + tex[block_match.end():]

    # Single column: remove twocolumn from documentclass options if present, and inject single-column commands
    # NOTE: Margin application disabled temporarily for debugging
    if single_column:
        # Detect document class
        docclass_match = re.search(r'\\documentclass(?:\[[^\]]*\])?\{([^}]+)\}', new_tex)
        if docclass_match:
            doc_class = docclass_match.group(1).strip()
        else:
            doc_class = "unknown"
        
        # Calculate effective margin (scales with font size)
        # Base: 1.5" margin at 12pt, scales inversely with font size
        if single_column_margin is None:
            margin_value = 1.5 * (12.0 / float(_normalize_pt_value(resolved_base_font_pt)))
        else:
            margin_value = single_column_margin
        
        # Remove twocolumn from \documentclass[...] options if present
        new_tex = re.sub(
            r'(\\documentclass\[)([^\]]*)(\])',
            lambda m: m.group(1) + re.sub(r',?\btwocolumn\b,?', lambda mm: ',' if mm.group(0).count(',') == 2 else '', m.group(2)).strip(',') + m.group(3),
            new_tex,
        )
        
        # Add \onecolumn after \begin{document} for all classes
        new_tex = re.sub(
            r'^([ \t]*)\\begin\{document\}',
            r'\1\\begin{document}\n\\onecolumn',
            new_tex,
            flags=re.MULTILINE,
        )
        
        print(f"✅ Single column mode applied for {doc_class}")

    new_tex = preserve_original_date(new_tex, original_printed_date)

    root, ext = os.path.splitext(tex_path)

    # ✅ If filename already ends with _formatted, overwrite it
    if root.endswith("_formatted"):
        new_path = tex_path
    else:
        new_path = root + "_formatted" + ext

    with open(new_path, "w", encoding="utf-8", errors="ignore") as f:
        f.write(new_tex)

    print(f"🆕 Updated TeX file: {new_path}")
    return new_path
