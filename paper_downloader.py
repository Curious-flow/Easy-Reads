import requests
import os
import tarfile
import shutil
from typing import Optional
import re



def download_file(url, save_as=None):

    '''
    Downloads a file from a URL and saves it to a local path.
    If `save_as` is not provided, the filename is inferred from the URL or headers.
    '''

    response = requests.get(url, stream=True)
    response.raise_for_status()

    # Try filename from Content-Disposition header
    if save_as is None:
        cd = response.headers.get("content-disposition")
        if cd and "filename=" in cd:
            save_as = cd.split("filename=")[-1].strip().strip('"')
        else:
            save_as = os.path.basename(url) or "downloaded_file"

    # Save to disk
    with open(save_as, "wb") as f:
        for chunk in response.iter_content(chunk_size=8192):
            f.write(chunk)

    print(f"✅ Downloaded {save_as} Successfully")
    return save_as



def extract_tar(filename, extract_to="."):

    '''
    Extracts a tar file to a specified directory.
    '''

    with tarfile.open(filename, "r:*") as tar:  # r:* auto-detects compression (.gz, .bz2, .xz, or plain .tar)
        tar.extractall(path=extract_to)
        print(f"📂 Extracted {len(tar.getnames())} files to '{os.path.abspath(extract_to)}'")



def find_largest_tex(root_folder):

    """
    Finds the largest .tex file in a root folder and its subfolders.
    Prefers original files over _easy versions.
    """

    largest_file = None
    largest_size = -1
    easy_files = {}  # Track _easy files separately

    for dirpath, _, filenames in os.walk(root_folder):
        for f in filenames:
            if f.endswith(".tex"):
                path = os.path.join(dirpath, f)
                size = os.path.getsize(path)
                
                # Check if this is an _easy file
                if '_easy.tex' in f:
                    # Store _easy files separately
                    original_name = f.replace('_easy.tex', '.tex')
                    original_path = os.path.join(dirpath, original_name)
                    if not os.path.exists(original_path):
                        # Only use _easy if original doesn't exist
                        easy_files[path] = size
                else:
                    # Prefer original files
                    if size > largest_size:
                        largest_size = size
                        largest_file = path

    # If no original file found, use largest _easy file
    if largest_file is None and easy_files:
        largest_file = max(easy_files, key=easy_files.get)
        largest_size = easy_files[largest_file]

    if largest_file:
        print(f"📄 Largest .tex file Found is: {largest_file} ({largest_size/1024:.2f} KB)")
    else:
        print("⚠️ No .tex files found")

    return largest_file



############################## Works Fine till Above #####################################
##########################################################################################



TUNING_BLOCK = r"""
% === BEGIN AUTO FONT/FIG TUNING (inserted by script) =========================
\newcommand{\BaseFontSizePt}{12}
\newcommand{\BaseBaselineSkipPt}{14.4}

\usepackage{graphicx}
\usepackage{etoolbox}

% Figure width and caption customization intentionally disabled
\AtBeginDocument{%
}

% === EASY_READS forced font override =================
\makeatletter
\renewcommand\normalsize{%
   \@setfontsize\normalsize{\BaseFontSizePt}{\BaseBaselineSkipPt}%
}
\normalsize
\makeatother
% =====================================================
% === END AUTO FONT/FIG TUNING ================================================
""".lstrip("\n")



def replace_missing_document_class(tex_path: str, force_replace: bool = False) -> str:
    """
    Replaces journal-specific document classes with standard 'article' class
    only if the class file is not found. Returns the path to the modified file.
    
    Args:
        tex_path: Path to the .tex file
        force_replace: If True, always replace journal classes regardless of file existence
    """
    with open(tex_path, "r", encoding="utf-8", errors="ignore") as f:
        tex = f.read()
    
    # Journal-specific classes that might not be installed
    journal_classes = [
        'mn', 'mnras',  # Monthly Notices
        'apj', 'apjl', 'apjs',  # Astrophysical Journal
        'aastex', 'aastex6',  # AAS journals
        'revtex4', 'revtex4-1',  # APS journals
        'iopart', 'iopart-num',  # IOP journals
        'elsarticle',  # Elsevier
        'svjour3', 'svjour',  # Springer
        'achemso',  # ACS journals
    ]
    
    # Find documentclass or documentstyle line (documentstyle is old LaTeX 2.09 syntax)
    docclass_pattern = re.compile(r"\\(?:documentclass|documentstyle)(?:\[[^\]]*\])?\{([^}]+)\}")
    match = docclass_pattern.search(tex)
    
    if match:
        current_class = match.group(1)
        
        # Check if it's a journal-specific class
        if current_class.lower() in [jc.lower() for jc in journal_classes]:
            class_file = current_class + '.cls'
            
            # If force_replace is True, skip existence check and always replace
            if force_replace:
                should_replace = True
            else:
                # Check if class file exists (local directory first)
                tex_dir = os.path.dirname(tex_path)
                class_exists_local = (
                    os.path.exists(class_file) or 
                    os.path.exists(os.path.join(tex_dir, class_file)) or
                    os.path.exists(os.path.join(tex_dir, os.path.basename(class_file)))
                )
                
                # Also check if LaTeX can find it system-wide using kpsewhich
                class_exists_system = False
                if not class_exists_local:
                    try:
                        import subprocess
                        result = subprocess.run(
                            ['kpsewhich', class_file],
                            capture_output=True,
                            text=True,
                            timeout=2
                        )
                        class_exists_system = (result.returncode == 0 and result.stdout.strip() != '')
                    except (FileNotFoundError, subprocess.TimeoutExpired, Exception):
                        # kpsewhich not available or failed, assume class might not exist
                        class_exists_system = False
                
                # Only replace if class file is not found locally or system-wide
                should_replace = not class_exists_local and not class_exists_system
            
            if should_replace:
                # Replace with article class (always use \documentclass, not \documentstyle)
                # Get the full match to preserve brackets
                full_match = match.group(0)
                # Replace the class name and convert documentstyle to documentclass
                if '\\documentstyle' in full_match:
                    # Convert old \documentstyle to modern \documentclass
                    replacement = full_match.replace('\\documentstyle', '\\documentclass').replace(current_class, 'article')
                else:
                    # Just replace the class name
                    replacement = full_match.replace(current_class, 'article')
                new_tex = tex[:match.start()] + replacement + tex[match.end():]
                
                # Write to new file (or overwrite if already _easy)
                root, ext = os.path.splitext(tex_path)
                if root.endswith('_easy'):
                    new_path = tex_path
                else:
                    new_path = root + "_easy" + ext
                
                with open(new_path, "w", encoding="utf-8", errors="ignore") as f:
                    f.write(new_tex)
                
                # Show what was replaced
                old_cmd = '\\documentstyle' if '\\documentstyle' in match.group(0) else '\\documentclass'
                print(f"🔄 Replaced {old_cmd}{{{current_class}}} with \\documentclass{{article}}")
                if force_replace:
                    print(f"   (Forced replacement due to compilation error - using standard article class)")
                else:
                    print(f"   (Class file {class_file} not found - using standard article class)")
                return new_path
            else:
                if not force_replace:
                    print(f"ℹ️  Using original document class: {current_class} (class file found)")
    
    return tex_path



def ensure_tuning_block(tex_path: str) -> str:
    """
    Ensures the tuning block exists in the .tex file.
    Creates a new file with _easy suffix if added.
    """
    with open(tex_path, "r", encoding="utf-8", errors="ignore") as f:
        tex = f.read()

    if "BEGIN AUTO FONT/FIG TUNING" in tex:
        print("ℹ️ Tuning block already present")
        return tex_path

    # Insert after \documentclass if found, else prepend
    m = re.search(r"\\documentclass(?:\[[^\]]*\])?\{[^\}]+\}", tex)
    if m:
        new_tex = tex[: m.end()] + "\n" + TUNING_BLOCK + "\n" + tex[m.end():]
    else:
        new_tex = TUNING_BLOCK + "\n" + tex

    root, ext = os.path.splitext(tex_path)
    
    # If file already ends with _easy, overwrite it; otherwise create new _easy file
    if root.endswith('_easy'):
        new_path = tex_path
    else:
        new_path = root + "_easy" + ext

    with open(new_path, "w", encoding="utf-8", errors="ignore") as f:
        f.write(new_tex)

    print(f"✅ Inserted tuning block into new file: {new_path}")
    return new_path