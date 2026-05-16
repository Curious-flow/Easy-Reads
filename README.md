# Easy Reads: An automated python program that makes arXiV papers more reader friendly and accessible 

Easy Reads is an automated Python program that downloads arXiv papers, processes their LaTeX source files, and generates more reader friendly and accessible paper outputs in PDF format with larger fonts and optional single-column formatting.

## Description

Scientific papers on ArXiv can be difficult to read because they often use smaller font sizes and a double-column page format. These papers inherit a publishing style that optimizes for economy and page-count efficiency, but this can lower the reading experience and cause accessibility issues. Extended reading over long periods can result in physical strain and fatigue, such as in eye, neck or shoulders, and in some cases create or exacerbate health conditions like headaches. While printed version of the paper prevent the strains from screens, some of the other issues persist. 

Zooming in on documents helps to an extent, but it can feel unnatural and is not seamless as the reader browses through the paper. Zooming in also does not intrinsically change the document, so a printed version of the paper will still have the same number of pages.

**Easy Reads** aims to solve this by editing the source LaTeX file of the paper and generating a newly formatted PDF. This output file will generally have more pages than the original, use larger font sizes, and optionally switch to a single-column layout, making both the digital and printed versions of the paper more reader-friendly and enjoyable. The final PDF also makes papers more accessible to people with visual impairments.

**Note:** This current version edits only the font sizes of the main body text and offers the ability to switch to a single-column page format. Future updates will likely support modifying the sizes of the title and abstract text, section headings, and figures and tables.

## Features

- **📥 Paper Download**: Automatically downloads ArXiv papers from URLs
- **📝 LaTeX Processing**: Extracts and processes LaTeX source files
- **🔤 Font Tuning**: Automatically adjusts font sizes and spacing for better readability
- **📄 PDF Compilation**: Compiles LaTeX to PDF with proper bibliography handling
- **🎯 User-Friendly**: Simple one-command execution with minimal setup

## Project Structure

- **`main_easy_reads.py`** - Main orchestrator script (entry point)
- **`paper_downloader.py`** - Handles ArXiv paper downloading and extraction
- **`paper_tuner.py`** - LaTeX formatting and tuning utilities
- **`unzipped/`** - Contains extracted paper files and generated outputs
- **`README.md`** - This documentation file

## Configuration

You can customize the following parameters in `main_easy_reads.py` to suit your reading preferences:

| Parameter | Description | Default Value |
|-----------|-------------|---------------|
| `base_font_pt` | Base font size in points | `12` recommended |
| `baseline_pt` | Line spacing in points | `1.2 * base_font_pt` (derived parameter) |
| `single_column` | Set to `True` to enable single-column formatting | `False` |


## Requirements

- **Python 3.x** - Download from [python.org](https://www.python.org/downloads/)
- **LaTeX distribution** - Choose one of the following:
  - [TeX Live](https://www.tug.org/texlive/) (cross-platform)
  - [MiKTeX](https://miktex.org/) (Windows-focused, easier installation)

- **Required Python packages:**

```bash
pip install requests
```

## Usage

The program needs the URL of the research paper on ArXiv as input.

**Example URL input format:** `https://arxiv.org/abs/XXXX.YYYY`  
*(Where XXXX and YYYY are unique numbers identifying the paper)*

The program assumes that the source file (typically in compressed .tar.gz format) containing the .tex and supporting files exists at:
`https://arxiv.org/src/XXXX.YYYY`

**It will automatically download the source file, create an edited `.tex` file, and output a new PDF.**

**File naming convention:** The program names the output files using the ArXiv PDF name with `_easy` appended. For example, if the ArXiv PDF name is `2905.10940v1`, the generated output will use `2905.10940v1_easy` as the base name.

### Steps to Use Easy Reads

Make sure the requirements are met.

1. **Download/Clone** this repository
2. **Open** `main_easy_reads.py` in your preferred editor
3. **Enter the URL** of the paper in the `url=''` variable
  - URL format: `https://arxiv.org/abs/XXXX.YYYY` within `main_easy_reads.py`
4. **Enter a font size**. The recommended font size is `12`. The line spacing is derived from the font size and can also be tuned if needed.
5. **Choose whether to enable the `single_column` feature**. Set it to `True` to make the final PDF single-column.
6. **Run the program** from a command prompt or terminal:

```bash
python main_easy_reads.py
```

**What the script does:**
1. Creates a `Downloads` folder in the same directory as `main_easy_reads.py`.
2. Downloads and extracts the specified ArXiv paper's source file, which is generally in `.tar.gz` format.
3. Applies formatting improvements to the paper's `.tex` file.
4. Compiles the LaTeX file, generates a new PDF, and saves it in a folder called `Formatted Papers`.
5. Names the final file using the ArXiv paper name followed by `_easy`.
