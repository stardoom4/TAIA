import os
import re
import json
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
    """Parses the .taia file and returns a dictionary of entries."""
    entries = []
    with open(file_path, "r", encoding="utf-8") as file:
        content = file.read().strip()

    # Regex to match TITL, UNDE, and DESC
    pattern = r"TITL:\s*(.+?)\n(?:UNDE:\s*(.+?)\n)?DESC:\s*(.+?)\n\n?"
    matches = re.findall(pattern, content, re.DOTALL)

    for match in matches:
        title, parent, desc = match
        parent = parent.strip() if parent else None
        desc = desc.strip()
        entries.append({"title": title.strip(), "parent": parent, "desc": desc})

    return entries

def build_tree(entries):
    """Builds a hierarchical tree structure from entries using UNDE as hierarchy."""
    tree = defaultdict(list)
    index = {}

    for entry in entries:
        index[entry["title"]] = entry  # Store entries in a dictionary
        tree[entry["parent"]].append(entry["title"])  # Create hierarchy

    return tree, index

def generate_nav(tree, current_title=None):
    """Recursively generates an infinite-level nested navigation menu."""
    if current_title not in tree:
        return ""

    nav_html = "<ul>\n"
    for child in sorted(tree[current_title]):  # Sort for consistency
        nav_html += f'  <li><a href="{child}.html">{child}</a>\n'
        sub_nav = generate_nav(tree, child)  # Recursively build child navigation
        if sub_nav:
            nav_html += sub_nav
        nav_html += "  </li>\n"
    nav_html += "</ul>\n"
    return nav_html

def generate_html(tree, index):
    """Generates HTML pages for all entries."""
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    # Generate global navigation once (visible on all pages)
    full_nav = generate_nav(tree, None)

    for title, entry in index.items():
        desc = entry["desc"]
        
        html_content = HTML_TEMPLATE.format(title=title, desc=desc, nav=full_nav)
        with open(os.path.join(OUTPUT_DIR, f"{title}.html"), "w", encoding="utf-8") as f:
            f.write(html_content)

def generate_index(tree):
    """Generates an index page with links to top-level pages."""
    full_nav = generate_nav(tree, None)
    index_content = HTML_TEMPLATE.format(title="Wiki Index", desc="Welcome to the Wiki.", nav=full_nav)
    
    with open(os.path.join(OUTPUT_DIR, "index.html"), "w", encoding="utf-8") as f:
        f.write(index_content)

def main():
    """Main function to generate the wiki."""
    entries = parse_taia(INPUT_FILE)
    tree, index = build_tree(entries)
    generate_html(tree, index)
    generate_index(tree)
    print("✅ Wiki generated successfully!")

if __name__ == "__main__":
    main()
