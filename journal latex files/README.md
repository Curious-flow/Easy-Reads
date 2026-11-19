# Journal LaTeX files

Shared journal-specific LaTeX dependencies for Easy Reads: document classes (.cls), bibliography styles (.bst), and supporting files as needed.

## Contents

- [AASTeX 6.3.1](aastex631/): official aastex631.cls for papers requesting aastex631, with its aasjournal.bst bibliography style. [Provenance and checksum](aastex631/SOURCE.md). [Upstream license](aastex631/LICENSE).

## Collection rules

- Retrieve files from the journal/society's official distribution or another authoritative upstream archive.
- Preserve exact class names and versions in separate subfolders.
- Keep upstream files unmodified, including copyright and license notices.
- Record retrieval URLs, release/commit identifiers, download dates, and checksums in SOURCE.md.
- Add dependencies as actual missing-file cases arise.
- Do not substitute generic article or silently switch a paper to a newer class version.

## Current status

Easy Reads now checks this folder for the exact requested document class. If that class is absent beside the paper and unavailable through kpsewhich, it copies the cached .cls into the paper directory. Existing local/installed classes are retained. Before BibTeX, Easy Reads also reads the requested bibliography style from the generated .aux and copies an exact-name cached .bst when unavailable locally or through kpsewhich. Other supporting files are not automatically copied.
