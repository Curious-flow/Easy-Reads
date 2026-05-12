"""
Easy Reads - ArXiv Paper Processor
Automatically downloads ArXiv papers and generates reader-friendly PDFs with larger fonts.
"""



import os
import sys

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

    # Display Banner
    print("\n" + "=" * 50)
    print("🚀 Easy Reads - ArXiv Paper Processor")
    print("=" * 50)
    #print("\n")

    
    # Step 1. Download Paper

    print("URL is", url)
    print("\n")

    # Keep project root clean by storing all downloaded artifacts in Downloads/
    project_root = os.path.dirname(os.path.abspath(__file__))
    downloads_dir = os.path.join(project_root, "Downloads")
    os.makedirs(downloads_dir, exist_ok=True)

    print("📥 Downloading paper...")
    paper_id = url.rstrip("/").split("/")[-1]
    tar_path = download_file(url, save_as=os.path.join(downloads_dir, f"{paper_id}.tar.gz"))
    print("\n")

    # Derive folder name from URL (e.g., Just arXiv ID)
    # rstrip removes trailing slas
    # Then split the URL into chunks of words by slash, and take last part as folder name

    folder_name = paper_id
    paper_folder = os.path.join(downloads_dir, folder_name)
    #print("\n")

    # Step 2. Extract the Paper | Likely involves unzipping a document source archive 
    extract_tar(tar_path, paper_folder)
    
    # Step 3. Find and process the Largest LaTeX file (the main paper source file)
    # There may be other latex files but those are not relevant.

    print("📝 Processing LaTeX file...")
    largest_tex = find_largest_tex(paper_folder)
    print("Largest TeX file is", largest_tex)

    if not largest_tex:
        print("\n❌ Could not find a .tex file to process.")
        return


    ### Fine Till Above

    ### Now Will try to Fix Below
    
    # Step 4 (Check This). Replace missing document classes with standard article class
    tex_with_class = replace_missing_document_class(largest_tex)

    # Apply formatting improvements
    print("\n")
    print("🎨 Applying formatting improvements...")
    new_tex = set_tuning_values_newfile(
        tex_with_class,
        base_font_pt=base_font_pt,
        baseline_pt=baseline_pt,
        single_column=single_column,
    )
    

    # Compile to PDF
    print("📄 Compiling to PDF...")
    pdf_path = compile_with_multiple_passes(new_tex)
    
    if pdf_path:
        # Move PDF to Formatted Papers folder with arxiv ID naming
        formatted_papers_dir = os.path.join(project_root, "Formatted Papers")
        os.makedirs(formatted_papers_dir, exist_ok=True)
        
        # Rename to arxiv_id_easy.pdf
        final_pdf_name = f"{paper_id}_easy.pdf"
        final_pdf_path = os.path.join(formatted_papers_dir, final_pdf_name)
        
        # Move the PDF from Downloads to Formatted Papers
        import shutil
        shutil.move(pdf_path, final_pdf_path)
        
        print(f"\n🎉 Success! Your PDF is ready: {final_pdf_path}")
        print("\n")
    else:
        print("\n❌ Processing failed. Check error messages above.")
        print("\n")


if __name__ == "__main__":


    # ==========================================================
    # ╔════════════════════════════════════════════════════════╗
    # ║             Enter Settings Below Including:            ║
    # ║          ArXiv URL of the paper, Font Size,            ║
    # ║                 and Line Spacing                       ║
    # ║          Don't Tweak Rest of the Code!                 ║
    # ╚════════════════════════════════════════════════════════╝
    # ==========================================================


    ### Chess Classic
    #url = "https://arxiv.org/src/2509.19443"

    ### My Paper
    #url = "https://arxiv.org/src/2602.07159"

    ### This Paper: High Energy Astro, Works Well
    #url="https://arxiv.org/abs/2605.10940"

    url="https://arxiv.org/src/2602.07159"

    # Font and formatting settings (optional)
    base_font_pt = 12 # Base font size (Recommended: 12)
    baseline_pt = 1.2* base_font_pt # Line spacing
    single_column = True # Default is False, which means it will
    # keep the original column format (often double colum).
    # Set to True to force single column

    # Future Knobs: 
    # Fig Size, Caption Size, Section/Subsection Heading Sizes
    # Abstract Size

    # =============================================================================
    # Run the main process
    # =============================================================================

    main(url, base_font_pt, baseline_pt, single_column=single_column)




