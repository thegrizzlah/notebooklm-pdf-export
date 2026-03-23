# NotebookLM PDF Export

Export your Google NotebookLM saved notes as individual PDF files.

Based on the original script by [Vivek K. Singh](https://gist.github.com/vivekthedev/5bfe0655986d775d6d07661974ce414e) ([blog post](https://vivekhere.medium.com/how-to-export-google-notebooklm-saved-notes-as-pdf-10b5ce6c6c10)).

## Quick Start

Grab the script directly from the [Gist](https://gist.github.com/TheGrizzlah/e6da0904734c71709191ac589019364e):

```bash
curl -O https://gist.githubusercontent.com/TheGrizzlah/e6da0904734c71709191ac589019364e/raw/export_note.py
pip3 install beautifulsoup4==4.13.4 markdown_pdf==1.7
```

Requires Python 3.9+.

## Usage

1. Open your notebook in [NotebookLM](https://notebooklm.google.com/).
2. In the Studio section, click **"Convert all notes to source"**.
3. Open browser DevTools (F12), find the `div` with class `elements-container`, right-click it, and select **Copy Element**.
4. Paste the copied HTML into a file called `notes.txt` in this directory.
5. Run the script:

```bash
python3 export_note.py
```

Each note will be saved as a separate PDF in the current directory.

## Changes from the Original

- Handles single notes (original only worked with multiple notes separated by dashes)
- Parses `<b>`, `<strong>`, and `<code>` tags correctly
- Handles ordered/unordered lists (`<ol>`, `<ul>`, `<li>`)
- Converts HTML tables to markdown tables
- Falls back to `div.elements-container` if `labs-tailwind-doc-viewer` is not found
- Extracts titles from headings for meaningful filenames
- Prints progress output instead of failing silently

## Credits

Original script by [Vivek K. Singh](https://github.com/vivekthedev).

## License

MIT
