import os
import subprocess
import re

# Common journal class files that might not be installed
JOURNAL_CLASS_MAPPING = {
    'mn.cls': 'article',  # Monthly Notices of the Royal Astronomical Society
    'mnras.cls': 'article',
    'aastex.cls': 'article',  # AAS journals
    'apj.cls': 'article',  # Astrophysical Journal
    'revtex4-1.cls': 'article',  # APS journals
    'revtex4.cls': 'article',
    'iopart.cls': 'article',  # IOP journals
    'elsarticle.cls': 'article',  # Elsevier
    'svjour3.cls': 'article',  # Springer
}

def check_and_suggest_missing_class(log_content, output_dir=None):
    """
    Checks for missing class file errors and suggests solutions.
    Returns the missing class name if found, None otherwise.
    """
    # Look for "File `X.cls' not found" pattern
    missing_class_match = re.search(r"File `([^']+\.cls)' not found", log_content)
    if missing_class_match:
        missing_class = missing_class_match.group(1)
        print(f"\n⚠️  Missing LaTeX class file detected: {missing_class}")
        
        # Check if class file exists in the output directory
        class_found_in_dir = False
        if output_dir and os.path.exists(output_dir):
            class_path = os.path.join(output_dir, missing_class)
            if os.path.exists(class_path):
                print(f"✅ Found {missing_class} in extracted files!")
                print(f"   Location: {class_path}")
                print(f"   LaTeX should find it automatically on next compilation")
                class_found_in_dir = True
        
        if not class_found_in_dir:
            if missing_class in JOURNAL_CLASS_MAPPING:
                print(f"💡 This is a journal-specific class file.")
                print(f"   Solutions:")
                print(f"   1. Replace \\documentclass{{{missing_class}}} with \\documentclass{{article}}")
                print(f"   2. Download {missing_class} from the journal's website")
                print(f"   3. Check if {missing_class} exists in the extracted files directory")
            else:
                print(f"💡 This class file is not installed in your LaTeX distribution")
                print(f"   Solutions:")
                print(f"   1. Install the class file manually")
                print(f"   2. Replace \\documentclass{{{missing_class}}} with \\documentclass{{article}}")
                if output_dir:
                    print(f"   3. Check if {missing_class} exists in: {output_dir}")
        
        return missing_class
    return None



def compile_with_multiple_passes(tex_file_path, output_dir=None):
    """
    Compiles a LaTeX file to PDF with multiple passes to ensure proper citation resolution.
    This function handles the complete compilation workflow including bibliography processing.
    Automatically replaces missing document classes if compilation fails.
    
    Args:
        tex_file_path: Path to the .tex file
        output_dir: Directory to run compilation in (default: same as tex file)
    
    Returns:
        Path to the generated PDF file, or None if compilation failed
    """
    if not tex_file_path or not os.path.exists(tex_file_path):
        print("❌ No tuned LaTeX file found to compile.")
        return None

    def run_single_compile(current_tex_path, output_dir_override=None):
        # Convert to absolute paths to avoid path issues
        current_tex_path = os.path.abspath(current_tex_path)

        if output_dir_override is None:
            compile_dir = os.path.dirname(current_tex_path)
        else:
            compile_dir = os.path.abspath(output_dir_override)

        tex_filename = os.path.basename(current_tex_path)
        tex_name = os.path.splitext(tex_filename)[0]

        original_dir = os.getcwd()
        os.chdir(compile_dir)

        try:
            print("\n")
            print(f"🔄 Compiling {tex_filename} to PDF...")
            print(f"   Working directory: {os.path.abspath(compile_dir)}")
            print(f"   TeX file: {tex_filename}")

            print("   Pass 1: pdflatex")
            result1 = subprocess.run([
                'pdflatex',
                '-interaction=nonstopmode',
                '-output-directory', '.',
                tex_filename
            ], capture_output=True, text=True)

            if result1.returncode != 0:
                print("   ⚠️ Errors in Pass 1:")
                error_lines = result1.stderr.split('\n')[-20:] if result1.stderr else []
                stdout_lines = result1.stdout.split('\n')[-20:] if result1.stdout else []
                for line in error_lines + stdout_lines:
                    if line.strip() and ('error' in line.lower() or '!' in line or 'fatal' in line.lower()):
                        print(f"      {line}")

            possible_bib_files = [
                tex_name + '.bib',
                os.path.splitext(tex_name.replace('_easy', ''))[0] + '.bib',
            ]
            bib_files_in_dir = [f for f in os.listdir('.') if f.endswith('.bib')]

            bib_file = None
            for possible_bib in possible_bib_files + bib_files_in_dir:
                if os.path.exists(possible_bib):
                    bib_file = possible_bib
                    break

            if bib_file:
                print(f"   Pass 2: bibtex (using {bib_file})")
                result2 = subprocess.run(['bibtex', tex_name], capture_output=True, text=True)
                if result2.returncode != 0:
                    print("   ⚠️ Errors in bibtex pass")
                    if result2.stderr:
                        print(f"      {result2.stderr[:200]}")
            else:
                print("   Pass 2: No .bib file found, skipping bibtex")
                print("   ℹ️  If you have citations, make sure a .bib file exists in the same directory")

            print("   Pass 3: pdflatex (bibliography)")
            subprocess.run([
                'pdflatex',
                '-interaction=nonstopmode',
                '-output-directory', '.',
                tex_filename
            ], capture_output=True, text=True)

            print("   Pass 4: pdflatex (final references)")
            subprocess.run([
                'pdflatex',
                '-interaction=nonstopmode',
                '-output-directory', '.',
                tex_filename
            ], capture_output=True, text=True)

            aux_file = tex_name + '.aux'
            if os.path.exists(aux_file):
                with open(aux_file, 'r', encoding='utf-8', errors='ignore') as f:
                    aux_content = f.read()
                if '\\citation' in aux_content:
                    citation_count = aux_content.count('\\citation')
                    print(f"   ℹ️  Found {citation_count} citation(s) in .aux file")
                    if '\\bibdata' in aux_content:
                        bibdata_match = re.search(r'\\bibdata\{([^}]+)\}', aux_content)
                        if bibdata_match:
                            expected_bib = bibdata_match.group(1) + '.bib'
                            print(f"   ℹ️  LaTeX expects bibliography file: {expected_bib}")
                            if not os.path.exists(expected_bib):
                                print(f"   ⚠️  Warning: Expected .bib file '{expected_bib}' not found!")

            pdf_path = os.path.join(compile_dir, f"{tex_name}.pdf")
            if os.path.exists(pdf_path):
                log_file = tex_name + '.log'
                if os.path.exists(log_file):
                    with open(log_file, 'r', encoding='utf-8', errors='ignore') as f:
                        log_content = f.read()

                    critical_errors = [
                        'Emergency stop',
                        'Fatal error',
                        '! LaTeX Error:',
                        '! Undefined control sequence',
                        '! Missing number',
                        '! Illegal unit of measure'
                    ]

                    has_critical_errors = any(error in log_content for error in critical_errors)

                    if has_critical_errors:
                        print("⚠️ PDF generated but contains LaTeX errors")
                        print("   Check the log file for details")
                    else:
                        print("✅ PDF successfully generated with minimal issues")

                    undefined_citations = False
                    if 'undefined citations' in log_content.lower():
                        undefined_citations = True
                    if 'Citation' in log_content and ('undefined' in log_content or 'on input line' in log_content):
                        undefined_matches = re.findall(r'Citation `([^\']+)\' on page \d+ undefined', log_content)
                        if undefined_matches:
                            undefined_citations = True
                            print(f"⚠️ Warning: {len(undefined_matches)} undefined citation(s) found:")
                            for cite in undefined_matches[:5]:
                                print(f"      - {cite}")

                    undefined_refs = re.findall(r'Reference `([^\']+)\' on page \d+ undefined', log_content)
                    if undefined_refs:
                        print(f"⚠️ Warning: {len(undefined_refs)} undefined reference(s) found:")
                        for ref in undefined_refs[:5]:
                            print(f"      - {ref}")

                    if undefined_citations or undefined_refs:
                        print("\n💡 Tips to fix '???' references:")
                        print("   1. Make sure the .bib file exists and is in the same directory")
                        print("   2. Check that \\bibliography{} command in .tex points to correct .bib file")
                        print("   3. Run compilation again - sometimes multiple passes are needed")
                        print("   4. Check that citation keys in \\cite{} match keys in .bib file")

                    overfull_count = log_content.count('Overfull \\hbox')
                    underfull_count = log_content.count('Underfull \\hbox')
                    if overfull_count > 0 or underfull_count > 0:
                        print(f"⚠️ Warning: {overfull_count} overfull and {underfull_count} underfull boxes")
                        print("   This may cause spacing issues in the PDF")

                print(f"📄 PDF location: {pdf_path}")
                return pdf_path

            print("❌ PDF file not found after compilation")
            log_file = tex_name + '.log'
            if os.path.exists(log_file):
                print("\n📋 Checking LaTeX log file for errors...")
                with open(log_file, 'r', encoding='utf-8', errors='ignore') as f:
                    log_content = f.read()

                errors_found = []
                lines = log_content.split('\n')
                for i, line in enumerate(lines):
                    if '!' in line and ('Error' in line or 'error' in line or 'Fatal' in line):
                        context = '\n'.join(lines[i:min(i + 5, len(lines))])
                        errors_found.append(context)
                        if len(errors_found) >= 5:
                            break

                check_and_suggest_missing_class(log_content, compile_dir)

                if errors_found:
                    print("\n🔍 LaTeX Errors Found:")
                    for i, error in enumerate(errors_found[:3], 1):
                        print(f"   Error {i}:")
                        for err_line in error.split('\n')[:3]:
                            if err_line.strip():
                                print(f"      {err_line}")
                else:
                    print("\n📄 Last 30 lines of log file:")
                    for line in lines[-30:]:
                        if line.strip():
                            print(f"   {line}")

            return None

        except FileNotFoundError:
            print("❌ Error: pdflatex not found. Please install LaTeX (e.g., TeX Live, MiKTeX)")
            return None
        except Exception as e:
            print(f"❌ Unexpected error: {e}")
            return None
        finally:
            os.chdir(original_dir)
    
    # Track which tex file we're using (might be replaced if class is missing)
    current_tex_path = tex_file_path
    
    print("🔄 Running initial compilation...")
    
    pdf_path = run_single_compile(current_tex_path, output_dir)
    
    # If compilation failed, check if it's due to missing class file
    if not pdf_path:
        # Check log file for missing class error
        tex_name = os.path.splitext(os.path.basename(current_tex_path))[0]
        log_file = os.path.join(os.path.dirname(current_tex_path) if output_dir is None else output_dir, tex_name + '.log')
        
        if os.path.exists(log_file):
            with open(log_file, 'r', encoding='utf-8', errors='ignore') as f:
                log_content = f.read()
            
            # Check for missing class file error
            missing_class_match = re.search(r"File `([^']+\.cls)' not found", log_content)
            if missing_class_match:
                missing_class = missing_class_match.group(1)
                print(f"\n🔧 Detected missing class file: {missing_class}")
                print("   Attempting automatic class replacement...")
                
                # Import the replacement function
                from paper_downloader_new import replace_missing_document_class
                
                # Replace the class (force replace since we know it's missing from compilation error)
                new_tex_path = replace_missing_document_class(current_tex_path, force_replace=True)
                
                if new_tex_path != current_tex_path:
                    print("   ✅ Class replaced, retrying compilation...")
                    current_tex_path = new_tex_path
                    # Try compilation again with replaced class
                    pdf_path = run_single_compile(current_tex_path, output_dir)
                    if pdf_path:
                        print(f"\n🎉 Success! Your PDF is ready: {pdf_path}")
                        return pdf_path
    
    if pdf_path:
        print(f"\n🎉 Success! Your PDF is ready: {pdf_path}")
        print("\n")
        return pdf_path
    else:
        print("❌ PDF compilation failed. Check the error messages above.")
        return None