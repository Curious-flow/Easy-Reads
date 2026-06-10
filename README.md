# Easy Reads: An automated python program that makes arXiV papers more reader friendly and accessible

Easy Reads is an automated Python program that downloads arXiv papers, processes their LaTeX source files, and generates more reader friendly and accessible papers in PDF format with larger fonts and an optional single column formatting for the main text.

The main goal of this initial release of Easy Reads is: Ease of Read.

## DOI

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.20278341.svg)](https://doi.org/10.5281/zenodo.20278341)

## Motivation

Scientific papers often use smaller fonts and double-column layouts, features that optimize print efficiency, but can strain the reader and causes accessibility issues. Zooming helps temporarily but doesn't fundamentally change the document—printed copies remain difficult to read. 

**Easy Reads** solves this by making scientific papers from arXiv more reader friendly. By editing the LaTeX source to generate a new PDF with larger fonts, better line spacing, and optional single-column formatting, the final paper is more reader friendly both digitally and in print, and this also improves accessibility of the paper.

## Features

- **📥 Paper Download**: Automatically downloads ArXiv papers from URLs
- **🔧 LaTeX Processing**: Extracts and processes LaTeX source files
- **🎨 Font Tuning**: Automatically adjusts font sizes and line spacing and optionally switch to single column text format for better readability
- **✅ PDF Compilation**: Compiles LaTeX to PDF with proper bibliography handling
- **🚀 User-Friendly**: Simple one-command execution with minimal setup

## Configuration

You can customize the following parameters to suit your reading preferences. Parameters can be set either **via CLI arguments (recommended)** or by editing variables in `main_easy_reads.py`:

| Code Variable | CLI Argument | Description | Default Value |
|---------------|--------------|-------------|----------------|
| `URL` | `--url` | ArXiv paper URL | (empty - required) |
| `FONT_SIZE` | `--font-size` | Base font size in points | `12` (recommended) |
| `SINGLE_COLUMN` | `--single-column` | Enable single-column formatting | `False` |
| `SINGLE_COLUMN_MARGIN` | `--single-column-margin` | Margin width in inches for single-column mode | `None` (auto-scales with font size) |

*Note: Line spacing (`baseline_pt`) is auto-calculated as `1.2 * FONT_SIZE` unless overridden with `--baseline`.*

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

The program takes an ArXiv URL and outputs a formatted PDF to `Formatted Papers/`. Output files are named with `_easy` appended (e.g., `2606.11115_easy.pdf`).

**Example URL format:** `https://arxiv.org/abs/XXXX.YYYYY`

### Two Ways to Use Easy Reads

#### **Option 1: Command Line (Recommended)** 💻

Pass parameters directly via CLI arguments. This is the recommended approach for flexibility and ease of use.

**Basic Usage - Just the URL:**
```bash
python main_easy_reads.py --url https://arxiv.org/abs/XXXX.YYYYY
```

**Common CLI Arguments (in order of importance):**

| Argument | Description | Example |
|----------|-------------|---------|
| `--url` | ArXiv paper URL (required) | `--url https://arxiv.org/abs/XXXX.YYYY` |
| `--font-size` | Base font size in points (10-18 recommended) | `--font-size 14` |
| `--single-column` | Enable single-column formatting (flag, no value needed) | `--single-column` |
| `--single-column-margin` | Custom margin width in inches for single-column mode | `--single-column-margin 1.3` |
| `--baseline` | Line spacing in points | `--baseline 18` |

**Example Commands:**

```bash
# Larger font for easier reading
python main_easy_reads.py --url https://arxiv.org/abs/XXXX.YYYY --font-size 14

# Single-column layout with auto-scaled margins
python main_easy_reads.py --url https://arxiv.org/abs/XXXX.YYYY --single-column

# Single-column with custom margin
python main_easy_reads.py --url https://arxiv.org/abs/XXXX.YYYY --single-column --single-column-margin 1.3
```

#### **Single-Column Margin Auto-Scaling**

When `--single-column` is enabled without specifying `--single-column-margin`, margins automatically scale based on font size to maintain optimal readability. To use a fixed margin:

```bash
python main_easy_reads.py --url https://arxiv.org/abs/XXXX.YYYY --single-column --single-column-margin 1.5
```

---

#### **Option 2: Edit Code Directly**

For users with consistent preferences or frequent usage, edit the hardcoded defaults in `main_easy_reads.py`:

1. Open `main_easy_reads.py` in your preferred editor.
2. Locate the settings section (around line 224):
```python
URL = ""  # Enter ArXiv URL here
FONT_SIZE = 12  # Base font size (Recommended: 12)
SINGLE_COLUMN = False  # Set to True for single-column formatting
SINGLE_COLUMN_MARGIN = None  # Set to None for auto-scaling (1.5" at 12pt), or enter custom value in inches
```

3. Modify the values to your preferences.
4. Run:
```bash
python main_easy_reads.py
```

The program will download the paper, apply formatting, compile to PDF, and save it in `Formatted Papers/`.


