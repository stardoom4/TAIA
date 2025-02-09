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

    with open(file_path, "r", encoding="utf-8") as file:
        content = file.read().strip()

    # Regex to match TITL, UNDE, and DESC
    pattern = r"TITL:\s*(.+?)\n(?:UNDE:\s*(.+?)\n)?DESC:\s*(.+?)(?=\nTITL:|\Z)"
    matches = re.findall(pattern, content, re.DOTALL)

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

    return entries

def build_tree(entries):
    """Builds a nested tree structure for navigation."""
    tree = defaultdict(list)
    
    for title, entry in entries.items():
        parent = entry["parent"]
        tree[parent].append(title)  # Add child to its parent

    return tree

def generate_nav(tree, current_parent=None):
    """Recursively builds the navigation menu for infinite levels."""
    if current_parent not in tree:
        return ""

    nav_html = "<ul>\n"
    for child in sorted(tree[current_parent]):  # Sort for consistency
        nav_html += f'  <li><a href="{child}.html">{child}</a>\n'
        sub_nav = generate_nav(tree, child)  # Recursively build child navigation
        if sub_nav:
            nav_html += sub_nav
        nav_html += "  </li>\n"
    nav_html += "</ul>\n"
    return nav_html

def generate_html(entries, tree):
    """Generates an HTML page for each wiki entry, setting 'Index' as homepage."""
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    for title, entry in entries.items():
        desc = entry["desc"]
        nav = generate_nav(tree, None)  # Generate hierarchical navigation

        # If "Index" exists, set filename as "index.html"
        file_name = "index.html" if title.strip().lower() == "index" else f"{title}.html"
        file_path = os.path.join(OUTPUT_DIR, file_name)

        print(f"🔍 Processing: {title} -> {file_name}")  # Debugging output

        html_content = HTML_TEMPLATE.format(title=title, desc=desc, nav=nav)

        with open(file_path, "w", encoding="utf-8") as f:
            f.write(html_content)

    print("✅ HTML pages successfully generated!")

def generate_index(tree):
    """Generates the main index page with navigation."""
    full_nav = generate_nav(tree, None)
    index_content = HTML_TEMPLATE.format(title="Wiki Index", desc="Welcome to the Wiki.", nav=full_nav)
    
    with open(os.path.join(OUTPUT_DIR, "index.html"), "w", encoding="utf-8") as f:
        f.write(index_content)

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
    generate_index(tree)

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
