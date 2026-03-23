# pip install beautifulsoup4==4.13.4 markdown_pdf==1.7
from bs4 import BeautifulSoup
from bs4.element import Tag, NavigableString
import re
from markdown_pdf import MarkdownPdf, Section

note_data = open("notes.txt", "r", encoding="utf-8").read()
soup = BeautifulSoup(note_data, "html.parser")


def extract_text(tag):
    """Recursively extract text from a tag, handling bold/code formatting."""
    result = ""
    for child in tag.children:
        if isinstance(child, NavigableString):
            result += str(child)
        elif isinstance(child, Tag):
            if child.name == "b" or child.name == "strong":
                result += f"**{child.get_text()}**"
            elif child.name == "code":
                result += f"`{child.get_text()}`"
            elif child.name == "span":
                classes = child.get("class", [])
                text = child.get_text()
                if "bold" in classes:
                    text = f"**{text}**"
                if "code" in classes:
                    text = f"`{text}`"
                result += text
            else:
                result += extract_text(child)
    return result


def process_table(table_tag):
    """Convert an HTML table to markdown."""
    rows = table_tag.find_all("tr")
    if not rows:
        return ""

    md = "\n"
    for i, row in enumerate(rows):
        cells = row.find_all(["th", "td"])
        cell_texts = [extract_text(cell).strip().replace("\n", " ") for cell in cells]
        md += "| " + " | ".join(cell_texts) + " |\n"
        if i == 0:
            md += "| " + " | ".join(["---"] * len(cell_texts)) + " |\n"
    md += "\n"
    return md


def process_element(tag):
    """Process a single structural element and return markdown."""
    if not isinstance(tag, Tag):
        return ""

    # Handle tables
    if tag.name == "table":
        return process_table(tag)

    # Handle ordered/unordered lists
    if tag.name in ("ol", "ul"):
        items = tag.find_all("li", recursive=False)
        if not items:
            # Lists might have nested structural elements containing li tags
            items = tag.find_all("li")
        md = "\n"
        for j, li in enumerate(items):
            text = extract_text(li).strip()
            if tag.name == "ol":
                md += f"{j+1}. {text}\n"
            else:
                md += f"- {text}\n"
        md += "\n"
        return md

    # Handle divs (paragraphs, headings)
    classes = tag.get("class", [])

    if tag.name == "div":
        text = extract_text(tag).strip()
        if not text:
            return ""

        if "heading1" in classes:
            return f"# {text}\n\n"
        elif "heading2" in classes:
            return f"## {text}\n\n"
        elif "heading3" in classes:
            return f"### {text}\n\n"
        elif "paragraph" in classes or "normal" in classes:
            return f"{text}\n\n"
        else:
            return f"{text}\n\n"

    # For wrapper elements, recurse into children
    result = ""
    for child in tag.children:
        result += process_element(child)
    return result


# Find the main content container
parent = soup.find("labs-tailwind-doc-viewer")
if not parent:
    parent = soup.find("div", class_="elements-container")

if not parent:
    print("Error: Could not find the notes container in the HTML.")
    exit(1)

# Collect all structural elements
elements = parent.find_all(
    ["div", "table", "ol", "ul"],
    recursive=False
)

# If no direct children found, try going one level deeper
if not elements:
    inner = parent.find("element-list-renderer")
    if inner:
        elements = inner.find_all(
            ["labs-tailwind-structural-element-view-v2", "ol", "ul"],
            recursive=False
        )

# Build the full markdown
full_md = ""
for el in elements:
    full_md += process_element(el)

# Split into individual notes by the horizontal rule separator
separator = "---" * 20  # 60 dashes or similar
chunks = re.split(r'-{10,}', full_md)

# Filter out empty chunks
chunks = [c.strip() for c in chunks if c.strip()]

if not chunks:
    print("Error: No content was extracted from the HTML.")
    exit(1)

# Generate PDFs
for i, chunk in enumerate(chunks):
    pdf = MarkdownPdf(toc_level=1, optimize=True)
    # Clean up formatting
    clean_text = re.sub(r'-(\n+)', '- ', chunk)
    clean_text = re.sub(r'\[\s*\d+(?:\s*[-,]\s*\d+)*\s*\]', '', clean_text)
    pdf.add_section(Section(clean_text))

    # Extract title from first heading
    title_match = re.search(r'^#\s+(.+)', clean_text, re.MULTILINE)
    if title_match:
        title = title_match.group(1).strip()
    else:
        # Use first non-empty line
        lines = [l for l in clean_text.split("\n") if l.strip()]
        title = lines[0].strip("# ") if lines else f"Note_{i}"

    # Clean title for filename
    title = title[:80]  # Limit length
    title = re.sub(r'[^\w\s-]', '', title).strip()
    title = title.replace(" ", "_")

    filename = f"{i}. {title}.pdf"
    pdf.save(filename)
    print(f"Created: {filename}")

print(f"\nDone! Exported {len(chunks)} note(s) as PDF.")
