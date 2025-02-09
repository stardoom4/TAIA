import os
import re
import shutil
from collections import defaultdict

# Configuration
INPUT_FILE = "database/chronicle.taia"  # The .taia file containing wiki entries
OUTPUT_DIR = "output_pages"   # Directory to store generated HTML files
            
# HTML Template
HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <link rel="stylesheet" href="styles.css">
</head>
<body>
    <nav>
        <h2>Navigation</h2>
        {nav}
    </nav>
    <main>
        <h1>{title}</h1>
        <p>{desc}</p>
    </main>
</body>
</html>
"""

def parse_taia(file_path):
    with open(file_path, "r", encoding="utf-8") as file:
         content = file.read().strip()

    print("\n=== RAW .taia CONTENT ===")
    print(content)  # Print the file content exactly as read

    """Parses the .taia file and returns a dictionary of entries."""
    entries = {}
    seen_titles = set()

    # Regex to match TITL, UNDE, and DESC
    pattern = r"TITL:\s*(.+?)\n(?:UNDE:\s*(.+?)\n)?DESC:\s*(.+?)(?=\nTITL:|\Z)"
    matches = re.findall(pattern, content, re.DOTALL)

    print("\n=== Parsed Entries ===")
    for match in matches:
        title, parent, desc = match
        title = title.strip()
        parent = parent.strip() if parent else None
        desc = desc.strip()

        # Check for duplicate titles
        if title in seen_titles:
            print(f"❌ ERROR: Duplicate title detected -> {title}")
            exit(1)
        seen_titles.add(title)

        entries[title] = {"title": title, "parent": parent, "desc": desc}

        print(f"✔ {title} (Parent: {parent})")  # Debug print

    return entries

def get_outermost_master(entries, title):
    """Finds the outermost master page of a given entry."""
    while title in entries and entries[title]["parent"]:
        title = entries[title]["parent"]  # Move up to the parent
    return title  # The topmost master page

def get_master_pages(entries):
    """Finds all top-level master pages (pages that are parents but not children)."""
    children = {entry["parent"] for entry in entries.values() if entry["parent"]}
    masters = [title for title in entries if title not in children or title == "Index"]
    return masters

def build_tree(entries):
    """Builds a nested tree structure for navigation."""
    tree = defaultdict(list)
    
    for title, entry in entries.items():
        parent = entry["parent"]
        tree[parent].append(title)  # Add child to its parent

    return tree
            
def generate_nav(entries, tree, current_page):
    """Generates hierarchical navigation but always includes master pages."""
    nav_html = "<ul>\n"

    # 🔹 Always include master pages (Index, Faora, Nova, etc.)
    for master in sorted(entries.keys()):
        if entries[master]["parent"] is None:  # Master page check
            nav_html += f'<li><a href="{master}.html">{master}</a></li>\n'

    # 🔹 Show child pages if current page is a master page
    if current_page in tree:
        nav_html += "<ul>\n"
        for child in sorted(tree[current_page]):
            nav_html += f'  <li><a href="{child}.html">{child}</a></li>\n'
        nav_html += "</ul>\n"

    nav_html += "</ul>\n"
    return nav_html


def generate_html(entries, tree, master_pages):
    """Generates an HTML page for each wiki entry."""
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    for title, entry in entries.items():
        desc = entry["desc"]
        nav = generate_nav(entries, tree, title)  # Generate nav for each page

        html_content = HTML_TEMPLATE.format(title=title, desc=desc, nav=nav)
        file_path = os.path.join(OUTPUT_DIR, f"{title}.html")

        with open(file_path, "w", encoding="utf-8") as f:
            f.write(html_content)



def generate_homepage(entries, tree, master_pages):
    """Generates index.html with only the outermost master pages."""
    index_desc = entries.get("Index", {}).get("desc", "Welcome to the Wiki.")
    master_pages = {get_outermost_master(entries, title) for title in entries}

    nav_html = "<ul>\n"
    for master in sorted(master_pages):
        nav_html += f'  <li><a href="{master}.html">{master}</a></li>\n'
    nav_html += "</ul>\n"

    index_content = HTML_TEMPLATE.format(title="Index", desc=index_desc, nav=nav_html)

    with open(os.path.join(OUTPUT_DIR, "index.html"), "w", encoding="utf-8") as f:
        f.write(index_content)

def main():
    """Main function to generate the static wiki."""
    entries = parse_taia(INPUT_FILE)

    tree = build_tree(entries)
    master_pages = get_master_pages(entries)  # Identify master pages

    generate_html(entries, tree, master_pages)
    generate_homepage(entries, tree, master_pages)

    print("\n✅ Wiki successfully generated!")


if __name__ == "__main__":
    main()
