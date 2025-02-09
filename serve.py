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

def build_tree(entries):
    """Builds a nested tree structure for navigation."""
    tree = defaultdict(list)
    
    for title, entry in entries.items():
        parent = entry["parent"]
        tree[parent].append(title)  # Add child to its parent

    return tree

def generate_nav(tree, current_parent):
    """Generates navigation for a specific page, showing only direct subpages."""
    if current_parent not in tree:
        return ""  # No children, return empty

    nav_html = "<ul>\n"
    for child in sorted(tree[current_parent]):  # Sort for consistent order
        nav_html += f'  <li><a href="{child}.html">{child}</a></li>\n'
    nav_html += "</ul>\n"
    
    return nav_html


def generate_html(entries, tree):
    """Generates an HTML page for each wiki entry with a limited navigation."""
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    for title, entry in entries.items():
        desc = entry["desc"]
        nav = generate_nav(tree, title)  # Only show direct subpages

        html_content = HTML_TEMPLATE.format(title=title, desc=desc, nav=nav)
        file_path = os.path.join(OUTPUT_DIR, f"{title}.html")

        with open(file_path, "w", encoding="utf-8") as f:
            f.write(html_content)


    print("✅ HTML pages successfully generated!")

def main():
    """Main function to generate the static wiki."""
    entries = parse_taia(INPUT_FILE)

    # 🔴 Debugging: Check if entries are parsed correctly
    print("=== Parsed Entries ===")
    for title, data in entries.items():
        print(f"Title: {title}")
        print(f"  Parent: {data['parent']}")
        print(f"  Description: {data['desc']}\n")

    tree = build_tree(entries)

    # 🔴 Debugging: Check tree structure
    print("\n=== Tree Structure ===")
    for parent, children in tree.items():
        print(f"Parent: {parent}")
        for child in children:
            print(f"  - {child}")

    generate_html(entries, tree)

    # 🔴 Debugging: Check if all pages were generated
    print("\n=== Generated Pages ===")
    for title in entries:
        file_path = os.path.join(OUTPUT_DIR, f"{title}.html")
        if os.path.exists(file_path):
            print(f"✅ {file_path}")
        else:
            print(f"❌ MISSING: {file_path}")

    print("\n✅ Wiki successfully generated!")

if __name__ == "__main__":
    main()
