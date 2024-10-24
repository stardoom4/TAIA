import os
import shutil
import json

def generate_html_from_taia(elements_file, microblog_file, output_dir):
    os.makedirs(output_dir, exist_ok=True)  # Create output directory if it doesn't exist
    entries = read_taia_file(elements_file)
    microblog_entries = read_taia_file(microblog_file)

    # Copy the style.css and script.js file to the output directory
    if os.path.exists('style.css'):
        shutil.copy('style.css', os.path.join(output_dir, 'style.css'))
    if os.path.exists('script.js'):
        shutil.copy('script.js', os.path.join(output_dir, 'script.js'))

    # Generate each HTML file based on the entries
    for entry in entries:
        if entry.get('TAG') != 'mb':  # Don't generate separate pages for microblog entries
            generate_html_file(entry, entries, output_dir)

    # Generate the microblog page
    generate_microblog_page(microblog_entries, entries, output_dir)

    # Generate the search index JSON file
    generate_search_index(entries + microblog_entries, output_dir)


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
                if entry:  # If there is an entry to add
                    entries.append(entry)  # Append entry to list
                    entry = {}  # Reset for next entry
        # Handle the last entry if there is no trailing blank line
        if entry:
            entries.append(entry)
    return entries


def generate_html_file(entry, entries, output_dir):
    title = entry.get('TITLE', 'Untitled')
    description = entry.get('DESCRIPTION', 'No content available.')
    under = entry.get('UNDER', None)

    # Generate the navigation menu with dynamic visibility for subpages
    html_content = f"""<html>
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <link rel="stylesheet" type="text/css" href="style.css">  <!-- CSS path -->
</head>
<body>
<button class="toggle-btn" aria-label="Toggle Sidebar">☰</button>
<div class="sidebar">
    <nav>
    <a href="microblog.html">Microblog</a>
        <ul>
            {generate_master_navigation(entries, entry)}
        </ul>
    </nav>
    </div>
    <div class="content">
    <h1>{title}</h1>
    {description}
    </div>
    <script src="script.js"></script><!-- Description can contain HTML tags -->
</body>
</html>
"""
    # Save the HTML file with the title as the filename
    file_name = f"{title.replace(' ', '_').lower()}.html"
    with open(os.path.join(output_dir, file_name), 'w') as html_file:
        html_file.write(html_content)


def generate_microblog_page(microblog_entries, entries, output_dir):
    if microblog_entries:
        html_content = f"""<html>
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Microblog</title>
    <link rel="stylesheet" type="text/css" href="style.css">  <!-- CSS path -->
</head>
<body>
<button class="toggle-btn" aria-label="Toggle Sidebar">☰</button>
<div class="sidebar">
    <nav>
        <ul>
            {generate_master_navigation(entries, None)}  <!-- Sidebar with main entries -->
        </ul>
    </nav>
</div>
<div class="content">
    <h1>Microblog</h1>
    <div class="microblog-feed">
        {generate_microblog_feed(microblog_entries)}
    </div>
</div>
<script src="script.js"></script>
</body>
</html>
"""

        # Save the microblog page as microblog.html
        file_name = "microblog.html"
        with open(os.path.join(output_dir, file_name), 'w') as html_file:
            html_file.write(html_content)


def generate_microblog_feed(entries):
    feed_content = ''
    for entry in entries:
        title = entry.get('TITLE', 'Untitled')
        description = entry.get('DESCRIPTION', 'No content available.')

        feed_content += f"""<div class="microblog-entry">
        <h3>{title}</h3>
        <p>{description}</p>
        </div>
        <hr>
        """

    return feed_content


def generate_master_navigation(entries, current_entry):
    nav_links = []
    
    # Get the master pages (exclude entries with TAG: mb)
    master_pages = [entry for entry in entries if 'UNDER' not in entry and entry.get('TAG') != 'mb']
    
    for master_entry in master_pages:
        master_title = master_entry['TITLE']
        master_file_name = f"{master_title.replace(' ', '_').lower()}.html"

        # Add master page link
        nav_links.append(f'<li><a href="{master_file_name}">{master_title}</a></li>')

        # If the current page is a master page, show its subpages
        if master_entry == current_entry:  # Check if we are on a master page
            sub_nav_links = [
                f'<li style="margin-left:20px;"><a href="{entry["TITLE"].replace(" ", "_").lower()}.html">{entry["TITLE"]}</a></li>'
                for entry in entries if entry.get('UNDER') == master_title and entry.get('TAG') != 'mb'
            ]
            
            if sub_nav_links:
                nav_links.append('<ul>' + ''.join(sub_nav_links) + '</ul>')
    
    return "\n".join(nav_links)


def generate_search_index(entries, output_dir):
    search_index = []
    for entry in entries:
        title = entry.get('TITLE', 'Untitled')
        description = entry.get('DESCRIPTION', '')
        url = f"{title.replace(' ', '_').lower()}.html" if entry.get('TAG') != 'mb' else "microblog.html"

        search_index.append({
            'title': title,
            'url': url
        })

    # Write the search index to a JSON file
    with open(os.path.join(output_dir, 'search_index.json'), 'w') as json_file:
        json.dump(search_index, json_file, indent=4)


# Example usage
generate_html_from_taia('elements.taia', 'microblog.taia', 'output_pages')
