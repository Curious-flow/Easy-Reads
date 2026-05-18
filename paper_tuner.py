import re
import os


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


def _normalize_pt_value(value) -> str:
    """Return a numeric string for TeX point dimensions (without the 'pt' suffix)."""
    text = str(value).strip()
    if text.lower().endswith("pt"):
        text = text[:-2].strip()
    return text


def set_tuning_values_newfile(
    tex_path: str,
    base_font_pt=None,
    baseline_pt=None,
    single_column: bool = False,
) -> str:
    with open(tex_path, "r", encoding="utf-8", errors="ignore") as f:
        tex = f.read()

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

    # Single column: remove twocolumn from documentclass options and inject \onecolumn
    if single_column:
        # Remove twocolumn from \documentclass[...] options
        new_tex = re.sub(
            r'(\\documentclass\[)([^\]]*)(\])',
            lambda m: m.group(1) + re.sub(r',?\btwocolumn\b,?', lambda mm: ',' if mm.group(0).count(',') == 2 else '', m.group(2)).strip(',') + m.group(3),
            new_tex,
        )
        # Inject \onecolumn right after \begin{document}
        new_tex = re.sub(
            r'(\\begin\{document\})',
            r'\1\n\\onecolumn',
            new_tex,
        )
        print("📐 Single column mode applied")

    root, ext = os.path.splitext(tex_path)

    # ✅ If filename already ends with _easy, overwrite it
    if root.endswith("_easy"):
        new_path = tex_path
    else:
        new_path = root + "_easy" + ext

    with open(new_path, "w", encoding="utf-8", errors="ignore") as f:
        f.write(new_tex)

    print(f"🆕 Updated TeX file: {new_path}")
    return new_path