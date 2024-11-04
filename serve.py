import os
import shutil
import json

def generate_html_from_taia(file_path, output_dir, microblog_file, homepage_title):
    os.makedirs(output_dir, exist_ok=True)  # Create output directory if it doesn't exist
    entries = read_taia_file(file_path)
    microblog_entries = read_taia_file(microblog_file)

    # Copy the style.css and script.js file to the output directory
    for file_name in ['style.css', 'script.js', 'splash.html']:
        if os.path.exists(file_name):
            shutil.copy(file_name, os.path.join(output_dir, file_name))

    # Generate HTML for each entry except for microblog
    for entry in entries:
        if entry.get('TAG') != 'mb':
            generate_html_file(entry, entries, output_dir)

    # Generate the microblog page with pagination
    generate_microblog_page(microblog_entries, entries, output_dir)

    # Generate search index file
    generate_search_index(entries, microblog_entries, output_dir)

    # Set the specified entry as the homepage
    homepage_entry = next((entry for entry in entries if entry['TITLE'] == homepage_title), None)
    if homepage_entry:
        homepage_path = os.path.join(output_dir, f"{homepage_entry['TITLE'].replace(' ', '_').lower()}.html")
        index_path = os.path.join(output_dir, 'index.html')
        shutil.copy(homepage_path, index_path)


def read_taia_file(file_path):
    entries = []
    with open(file_path, 'r') as file:
        entry = {}
        for line in file:
            line = line.strip()
            if line:  # Non-empty line
                key, value = line.split(': ', 1)
                entry[key] = value
            else:  # Blank line indicates end of an entry
                if entry:
                    entries.append(entry)  # Append entry to list
                    entry = {}  # Reset for next entry
        if entry:  # Handle last entry if no trailing blank line
            entries.append(entry)
    return entries


def generate_html_file(entry, entries, output_dir):
    title = entry.get('TITLE', 'Untitled')
    description = entry.get('DESCRIPTION', 'No content available.')
    
    # Process the description to convert `link "page_name"` syntax to hyperlinks
    description = replace_links(description, entries)

    # Add a sidebar link to the microblog
    html_content = f"""<html>
<!DOCTYPE html>
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title}</title>
<link rel="stylesheet" type="text/css" href="style.css">
</head>
<body>
<input type="text" id="searchInput" placeholder="Search..." onkeyup="searchPages()">
<ul id="searchResults"></ul><button class="toggle-btn" aria-label="Toggle Sidebar">☰</button>
<div class="sidebar">
    <nav>
        <ul>
            <a href="home.html">Home</a>
            <a href="microblog_page_1.html">Microblog</a>
            {generate_master_navigation(entries, entry)}
        </ul>
    </nav>
</div>
<div class="content">
    <h1>{title}</h1>
    {description}
</div>
<script src="script.js"></script>
<div class="footer">
<p>TAIA</p>
</div>
</body>
</html>
"""
    # Save the HTML file with the title as the filename
    file_name = f"{title.replace(' ', '_').lower()}.html"
    with open(os.path.join(output_dir, file_name), 'w') as html_file:
        html_file.write(html_content)

# Add a `homepage_title` parameter to specify the homepage entry title.
generate_html_from_taia('elements.taia', 'output_pages', 'microblog.taia', homepage_title='Home')
