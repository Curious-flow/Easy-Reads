# Easy Reads - ArXiv Paper Processor

A Python tool for downloading ArXiv papers, processing LaTeX files, and generating easy-to-read PDFs with larger fonts and improved formatting.

## Description

Scientific papers on ArXiv can be difficult to read because of their smaller font and figure sizes. Extended reading results in eye strain, and in some cases over prolonged periods can lead to or exacerbate other health problems. Zooming in the documents helps to an extent but can be unnatural and the process is not seamless as the reader browses through the document. Zooming in also does not intrinsically change the document, so a printed version of the paper will still look the same. 

**Easy Reads** aims to solve this by editing the source LaTeX file and generating a new formatted output PDF file. This output file will have more pages than the original with larger font and figure sizes, making both the digital and printed versions of the paper more reader-friendly and enjoybale.  

**Note:** This current beta version aims to edit only the fontsizes while future updates will have support for figures/tables and captions.

## Usage

The program needs the URL of the research paper on ArXiv.

**Example URL format:** `https://arxiv.org/abs/XXXX.YYYY`  
*(Where XXXX and YYYY are unique numbers identifying the paper)*

The program assumes that the source file (typically in compressed .tar.gz format) containing the .tex and supporting files exists at:
`https://arxiv.org/src/XXXX.YYYY`

It will automatically download the source file and create an edited .tex file and output a new PDF.

**File naming convention:** If the original .tex file is called `research_paper.tex`, the program will create a new .tex and .pdf file with `_easy` appended to the name. In this case, it would generate `research_paper_easy.tex` and `research_paper_easy.pdf` files.

### How to Use:

1. **Download/Clone** this repository
2. **Open** `main_easy_reads.py` in your preferred editor
3. **Enter the URL** of the paper in the `url=''` variable
   - URL format: `https://arxiv.org/abs/XXXX.YYYY`
4. **Run the program** from command prompt/terminal:

```bash
python main_easy_reads.py
```

**What the script does:**
1. Downloads the specified ArXiv paper's source to the current folder
2. Creates an unzipped folder containing the extracted files
3. Applies formatting improvements to the .tex file of the paper
4. Compiles the LaTeX to generate a new PDF

## Requirements

- **Python 3.x** - Download from [python.org](https://www.python.org/downloads/)
- **LaTeX distribution** - Choose one of the following:
  - [TeX Live](https://www.tug.org/texlive/) (Cross-platform)
  - [MiKTeX](https://miktex.org/) (Windows-focused, easier installation)
- **Required Python packages:**
  ```bash
  pip install requests
  ```
## Features

- **📥 Paper Download**: Automatically download ArXiv papers from URLs
- **📝 LaTeX Processing**: Extract and process LaTeX source files
- **🔤 Font Tuning**: Automatically adjust font sizes and spacing for better readability
- **🖼️ Figure Optimization**: Resize figures for optimal display and clarity
- **📄 PDF Compilation**: Compile LaTeX to PDF with proper bibliography handling
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
| `base_font_pt` | Base font size in points | `12` |
| `baseline_pt` | Line spacing in points | `14.4` |
| `default_fig_width` | Figure width as fraction of line width | `0.9\linewidth` |
| `caption_size` | Caption font size | `small` |

**💡 Tip:** Increase fontsize via `base_font_pt` and `baseline_pt` for even larger, more readable text, or adjust `default_fig_width` to make figures more prominent.