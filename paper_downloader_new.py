import requests
import os
import tarfile
import shutil
import re

from typing import Optional

def download_file(url, save_as=None):

    '''
    Downloads a file from a URL and saves it to a local path.
    If `save_as` is not provided, the filename is inferred from the URL or headers.
    '''

    # Requests.get Send a GET request
    # Requests.get takes the URL and tries to connect to the server at the address
    # Server responds with Headers and File Data (if successful)
    # Stream=True means the response body is downloaded in chunks, not all at once

    # arXiv abstract links need to be converted to source links for tar download
    if "arxiv.org/abs/" in url:
        url = url.replace("arxiv.org/abs/", "arxiv.org/src/", 1)

    response = requests.get(url, stream=True)

    # Raise an exception if the server returned an error (e.g. 404, 500)
    response.raise_for_status()

    # print(type(response))
    # print(response.status_code)

    # If no filename was provided (save_as = input parameter, Set to None by default 
    # Then try to figure one out automatically

    if save_as is None:

        # Check the Content-Disposition header — servers sometimes specify the filename here
        # e.g. Content-Disposition: attachment; filename="2602.07159.tar.gz"
        cd = response.headers.get("content-disposition")

        if cd and "filename=" in cd:
            # Extract the filename value from the header and strip surrounding quotes/spaces
            save_as = cd.split("filename=")[-1].strip().strip('"')
        else:
            # Fall back to the last segment of the URL (e.g. "2602.07159" from the arXiv URL)
            # If that's also empty, use a generic default name
            #basename gets the last part of the URL path, which is often the paper ID or filename
            save_as = os.path.basename(url) or "downloaded_file"
            print("TEST",save_as)

    # Open the destination file in binary write mode
    with open(save_as, "wb") as f:

        # Write the response in 8 KB chunks to avoid loading the whole file
        # into memory at once

        # response.iter_content streams the data (within response) in chunks
        for chunk in response.iter_content(chunk_size=8192):
            f.write(chunk)

    print(f"✅ Downloaded {save_as} Successfully")

    # Return the filename so the caller knows where the file was saved
    return save_as



def extract_tar(filename, extract_to="."):
                        
    '''
    Extracts a tar file to a specified directory.
    '''

    # Downloaded file is likely a zip/tar file, so we need to extract it
    # tarfile.open opens the tar file for reading. The 'r:*' mode auto-detects
    # the compression type (gzip, bzip2, xz, or uncompressed tar)
    # tar.extractall extracts all the contents of the tar file to the 
    # specified directory (extract_to)
    # After extraction, it prints how many files were extracted and where they
    # were extracted to

    try:
        os.makedirs(extract_to, exist_ok=True)
    except OSError:
        if not os.path.isdir(extract_to):
            raise
    with tarfile.open(filename, "r:*") as tar:  # r:* auto-detects compression (.gz, .bz2, .xz, or plain .tar)
        tar.extractall(path=extract_to)
        print(f"📂 Extracted {len(tar.getnames())} files to '{os.path.abspath(extract_to)}'")


### Line by Line Comments Good Till Top


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
    docclass_pattern = re.compile(
        r"^[ \t]*\\(?:documentclass|documentstyle)(?:\[[^\]]*\])?\{([^}]+)\}",
        flags=re.MULTILINE,
    )
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