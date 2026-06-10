"""
Easy Reads - ArXiv Paper Processor
Automatically downloads ArXiv papers and generates reader-friendly PDFs with larger fonts.
"""

import os
import sys
import re
import urllib.request
import argparse

import paper_downloader
import paper_tuner
import paper_tex_to_pdf

from paper_downloader import download_file, extract_tar, find_largest_tex, replace_missing_document_class
from paper_tuner import set_tuning_values_newfile
from paper_tex_to_pdf import compile_with_multiple_passes

def main(url, base_font_pt, baseline_pt, single_column=False):

    """
    Main processing pipeline for Easy Reads.
    """

    # Step 1. Download Paper

    # Keep project root clean by storing all downloaded artifacts in Downloads/
    project_root = os.path.dirname(os.path.abspath(__file__))
    downloads_dir = os.path.join(project_root, "Downloads")
    os.makedirs(downloads_dir, exist_ok=True)

    print("=" * 60)
    print("📥 Downloading paper...")
    print("=" * 60)
    raw_id = url.rstrip("/").split("/")[-1]  # e.g. "3605.08080" or "3605.08080v2"
    version_match = re.search(r'(v\d+)$', raw_id)
    if version_match:
        paper_id = raw_id[:version_match.start()]
        version_str = version_match.group(1)
    else:
        paper_id = raw_id
        # Query arXiv API to get the latest version number
        try:
            api_url = f"https://export.arxiv.org/api/query?id_list={paper_id}"
            with urllib.request.urlopen(api_url) as resp:
                content = resp.read().decode()
            ver = re.search(r'arxiv\.org/abs/[\d.]+v(\d+)', content)
            version_str = f"v{ver.group(1)}" if ver else ""
        except Exception:
            version_str = ""
    print(f"arXiv ID: {paper_id}  Version: {version_str}")
    tar_path = download_file(url, save_as=os.path.join(downloads_dir, f"{paper_id}.tar.gz"))
    print("=" * 60 + "\n")

    # Derive folder name from URL (e.g., Just arXiv ID)
    # rstrip removes trailing slash
    # Then split the URL into chunks of words by slash, and take last part as folder name

    folder_name = paper_id
    paper_folder = os.path.join(downloads_dir, folder_name)

    # Step 2. Extract the Paper | Unzip the downloaded tar.gz file
    print("=" * 60)
    extract_tar(tar_path, paper_folder)
    print("=" * 60 + "\n")
    
    # Step 3. Find and process the Largest LaTeX file (the main paper source file)
    # There may be other latex files but those are not relevant.

    print("📝 Processing LaTeX file...")
    largest_tex = find_largest_tex(paper_folder)
    print("Largest TeX file is", largest_tex)

    if not largest_tex:
        print("\n❌ Could not find a .tex file to process.")
        return

    # Step 4. Replace missing document classes with standard article class
    tex_with_class = replace_missing_document_class(largest_tex)

    # Apply formatting improvements
    print("=" * 60)
    print("🎨 Applying formatting improvements...")
    print("=" * 60)
    new_tex = set_tuning_values_newfile(
        tex_with_class,
        base_font_pt=base_font_pt,
        baseline_pt=baseline_pt,
        single_column=single_column,
    )
    print("=" * 60 + "\n")
    
    # Compile to PDF
    print("=" * 60)
    print("📄 Compiling to PDF...")
    print("=" * 60)
    pdf_path = compile_with_multiple_passes(new_tex)
    print("=" * 60 + "\n")
    
    if pdf_path:
        # Move PDF to Formatted Papers folder with arxiv ID naming
        formatted_papers_dir = os.path.join(project_root, "Formatted Papers")
        os.makedirs(formatted_papers_dir, exist_ok=True)
        
        # Rename to arxiv_idvN_easy.pdf
        final_pdf_name = f"{paper_id}{version_str}_easy.pdf"
        final_pdf_path = os.path.join(formatted_papers_dir, final_pdf_name)
        
        # Move the PDF from /Downloads to /Formatted Papers
        import shutil
        shutil.move(pdf_path, final_pdf_path)
        
        print("=" * 60)
        print(f"🎉 Success! Your PDF is ready: {final_pdf_path}")
        print("=" * 60 + "\n")
    else:
        print("=" * 60)
        print("❌ Processing failed. Check error messages above.")
        print("=" * 60 + "\n")


if __name__ == "__main__":

    # ==========================================================
    # ╔════════════════════════════════════════════════════════╗
    # ║            Enter Settings Below Including:             ║
    # ║          ArXiv URL of the paper, Font Size,            ║
    # ║           Line Spacing (derived by default)            ║
    # ║          Don't Tweak Rest of the Code!                 ║
    # ╚════════════════════════════════════════════════════════╝
    # ==========================================================

    # HARDCODED DEFAULTS (used if no CLI args provided)

    # ENTER ARXIV URL BELOW
    # Make sure it's the main abstract page URL,
    # Of the form: https://arxiv.org/abs/XXXX.YYYYY

    # Example: URL="https://arxiv.org/abs/9000.12345"

    URL = ""
    DEFAULT_FONT_SIZE = 12  # Base font size (Recommended: 12)
    DEFAULT_SINGLE_COLUMN = False

    # =============================================================================
    # Command-Line Argument Parser (Optional Override)
    # =============================================================================

    parser = argparse.ArgumentParser(
        description="Easy Reads - ArXiv Paper Processor",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main_easy_reads.py
  python main_easy_reads.py --url https://arxiv.org/abs/9000.12345 --font-size 14
  python main_easy_reads.py --url https://arxiv.org/abs/9000.12345 --single-column
        """
    )

    parser.add_argument(
        "--url",
        type=str,
        default=URL,
        help=f"ArXiv paper URL (default: {URL})"
    )
    parser.add_argument(
        "--font-size",
        type=int,
        default=DEFAULT_FONT_SIZE,
        help=f"Base font size in points (default: {DEFAULT_FONT_SIZE})"
    )
    parser.add_argument(
        "--baseline",
        type=float,
        default=None,
        help="Line spacing in points (default: 1.2 * font-size, auto-calculated)"
    )
    parser.add_argument(
        "--single-column",
        action="store_true",
        default=DEFAULT_SINGLE_COLUMN,
        help="Enable single-column formatting (default: False)"
    )

    args = parser.parse_args()

    # Resolve final values (CLI args override defaults)
    url = args.url
    base_font_pt = args.font_size
    baseline_pt = args.baseline if args.baseline is not None else (1.2 * base_font_pt)
    single_column = args.single_column

    # =============================================================================
    # Display Banner and Configuration
    # =============================================================================

    print("\n" + "=" * 60)
    print("🚀 Easy Reads - ArXiv Paper Processor")
    print("=" * 60)
    print("📋 Paper Settings")
    print("=" * 60)
    print(f"   URL: {url}")
    print(f"   Font Size: {base_font_pt} pt")
    print(f"   Line Spacing: {baseline_pt:.1f} pt")
    print(f"   Single Column: {single_column}")
    print("=" * 60 + "\n")

    # =============================================================================
    # Run main
    # =============================================================================

    main(url, base_font_pt, baseline_pt, single_column=single_column)