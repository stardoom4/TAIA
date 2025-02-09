import os
import re
import shutil
from collections import defaultdict

# Configuration
INPUT_FILE = "database/chronicle.taia"  # The .taia file containing wiki entries
OUTPUT_DIR = "output_pages"   # Directory to store generated HTML files

# Ensure the output directory exists
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Copy CSS to output directory
shutil.copy("style.css", os.path.join(OUTPUT_DIR, "style.css"))

# HTML Template
HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <link rel="stylesheet" href="style.css">
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
    <script>
        // Mobile Navigation Toggle
        document.getElementById('mobile-nav-toggle').addEventListener('click', function() {
            document.getElementById('sidebar').classList.toggle('open');
        });
    </script>
</html>
"""

def parse_taia(file_path):
    """Parses the .taia file and returns a dictionary of entries."""
    with open(file_path, "r", encoding="utf-8") as file:
        content = file.read().strip()

    entries = {}
    seen_titles = set()

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
    """Builds a hierarchical tree structure for navigation."""
    tree = defaultdict(list)
    
    for title, entry in entries.items():
        parent = entry["parent"]
        tree[parent].append(title)  # Add child to its parent

    return tree

def generate_nav(tree, current_parent=None, depth=0):
    """Recursively builds the hierarchical navigation menu."""
    if current_parent not in tree:
        return ""

    indent = "  " * depth  # Indentation for better readability
    nav_html = f"{indent}<ul>\n"
    
    for child in sorted(tree[current_parent]):  # Sort for consistency
        nav_html += f'{indent}  <li><a href="{child}.html">{child}</a>'
        sub_nav = generate_nav(tree, child, depth + 1)  # Recursively build sub-navigation
        if sub_nav:
            nav_html += "\n" + sub_nav  # Append sub-navigation
        nav_html += f"{indent}  </li>\n"

    nav_html += f"{indent}</ul>\n"
    return nav_html

def generate_html(entries, tree):
    """Generates an HTML page for each wiki entry."""
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    for title, entry in entries.items():
        desc = entry["desc"]
        nav = generate_nav(tree, None)  # Generate hierarchical navigation

        # Ensure "Index" becomes "index.html"
        file_name = "index.html" if title.lower() == "index" else f"{title}.html"
        file_path = os.path.join(OUTPUT_DIR, file_name)

        html_content = HTML_TEMPLATE.format(title=title, desc=desc, nav=nav)

        with open(file_path, "w", encoding="utf-8") as f:
            f.write(html_content)

def generate_index(entries, tree):
    """Generates the main index page with hierarchical navigation."""
    full_nav = generate_nav(tree, None)
    
    index_desc = entries.get("Index", {}).get("desc", "Welcome to the Wiki.")
    index_content = HTML_TEMPLATE.format(title="Wiki Index", desc=index_desc, nav=full_nav)

    with open(os.path.join(OUTPUT_DIR, "index.html"), "w", encoding="utf-8") as f:
        f.write(index_content)

def main():
    """Main function to generate the static wiki."""
    entries = parse_taia(INPUT_FILE)
    tree = build_tree(entries)

    # 🔴 Debugging: Print hierarchical tree structure
    print("\n=== Tree Structure ===")
    for parent, children in tree.items():
        print(f"Parent: {parent}")
        for child in children:
            print(f"  - {child}")

    generate_html(entries, tree)
    generate_index(entries, tree)

    # 🔴 Debugging: Verify if all pages were generated
    print("\n=== Generated Pages ===")
    for title in entries:
        file_name = "index.html" if title.lower() == "index" else f"{title}.html"
        file_path = os.path.join(OUTPUT_DIR, file_name)
        if os.path.exists(file_path):
            print(f"✅ {file_path}")
        else:
            print(f"❌ MISSING: {file_path}")

    print("\n✅ Wiki successfully generated!")

if __name__ == "__main__":
    main()
