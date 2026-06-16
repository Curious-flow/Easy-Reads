# Easy Reads: An automated python program that makes scientific papers from arXiV more reader friendly and accessible

The main goal of Easy Reads is: Ease of Reading.

## DOI

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.20278341.svg)](https://doi.org/10.5281/zenodo.20278341)

## Motivation

Scientific papers often use smaller fonts and double-column layouts, features that optimize print efficiency, but can strain the reader and causes accessibility issues. Zooming helps temporarily but doesn't fundamentally change the document, printed copies may remain difficult to read. 

**Easy Reads** solves this by making scientific papers from arXiv more reader friendly. It works directly with the source LaTeX file to generate a new PDF with larger fonts, better line spacing, and optional single-column formatting.

**🚀 User-Friendly**: Easy Reads has a simple one-command execution with minimal setup.


## Requirements

- **Python 3.x** - Download from [python.org](https://www.python.org/downloads/)
- **LaTeX distribution** - Choose one of the following:
  - [TeX Live](https://www.tug.org/texlive/) (cross-platform)
  - [MiKTeX](https://miktex.org/) (cross-platform, easier installation)
    
    When using MikTex, it is recommended to allow missing packages to installed automatically (on-the-fly) under Settings -> General

- **Required Python packages:**

```bash
pip install requests
```

## Usage

**Example URL format:** `https://arxiv.org/abs/XXXX.YYYYY`

The program takes an ArXiv URL, downlaods the source file to the `Downloads/` folder, modifies the main latex file and converts it to a formatted PDF. The final PDF is saved to `Formatted Papers/`. Output files are named with `_easy` appended (e.g., `XXXX.YYYYY_easy.pdf`) to distinguish them from the original PDF.


### Two Ways to Use Easy Reads


#### **Option 1: Command Line (Recommended)** 💻

Pass parameters directly via CLI arguments. This is the recommended approach for flexibility and ease of use.

**Basic Usage - Just the URL:**
```bash
python main_easy_reads.py --url https://arxiv.org/abs/XXXX.YYYYY
```


**Allowed CLI Arguments (in order of importance):**

| Argument | Description | Default | Example |
|----------|-------------|---------|---------|
| `--url` | ArXiv paper URL (required) | (none - required) | `--url https://arxiv.org/abs/XXXX.YYYY` |
| `--font-size` | Base font size in points | `12` | `--font-size 14` |
| `--single-column` | Enable single-column formatting (flag, no value needed) | `False` | `--single-column` |
| `--single-column-margin` | Custom margin width in inches for single-column mode | `None` (auto-scales) | `--single-column-margin 1.3` |
| `--baseline` | Line spacing in points | Auto-calculated (1.2 × font size) | `--baseline 18` || `--output-suffix` | Suffix for output filename | `_easy` | `--output-suffix _formatted` |
**Example of Single Command Execution:**

```bash
# Larger font for easier reading
python main_easy_reads.py --url https://arxiv.org/abs/XXXX.YYYY --font-size 14

# Single-column layout with auto-scaled margins
python main_easy_reads.py --url https://arxiv.org/abs/XXXX.YYYY --single-column

# Single-column with custom margin (in inches)
python main_easy_reads.py --url https://arxiv.org/abs/XXXX.YYYY --single-column --single-column-margin 1.3

# Adding a Custom suffix for the output file
python main_easy_reads.py --url https://arxiv.org/abs/XXXX.YYYY --output-suffix _formatted
```

---

#### **Option 2: Edit Code Directly**

For users with consistent preferences or frequent usage, edit the hardcoded defaults in `main_easy_reads.py`:

1. Open `main_easy_reads.py` in your preferred editor.
2. Locate the settings section (around line 224):
```python
URL = ""  # Enter ArXiv URL here
FONT_SIZE = 12  # Base font size (Default Size: 12)
BASELINE = None  # Line spacing in points (default: 1.2 * font size, auto-calculated), or enter custom value
SINGLE_COLUMN = False  # Set to True for single-column formatting
SINGLE_COLUMN_MARGIN = None  # Set to None for auto-scaling (1.5" at 12pt), or enter custom value in inches
OUTPUT_SUFFIX = "_formatted"  # Suffix for output filename (can change to e.g., "_easy", "_readable", etc., or "" for no suffix)
```

3. Modify the values to your preferences.
4. Run:
```bash
python main_easy_reads.py
```

The program will download the paper, apply formatting, compile to PDF, and save the final PDF in `Formatted Papers/`.