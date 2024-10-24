import os
import shutil
import json

def generate_html_from_taia(elements_file_path, microblog_file_path, output_dir):
    os.makedirs(output_dir, exist_ok=True)  # Create output directory if it doesn't exist
    entries = read_taia_file(elements_file_path)
    microblog_entries = read_taia_file(microblog_file_path)

    # Copy the style.css and script.js files to the output directory
    if os.path.exists('style.css'):
        shutil.copy('style.css', os.path.join(output_dir, 'style.css'))

    if os.path.exists('script.js'):
        shutil.copy('script.js', os.path.join(output_dir, 'script.js'))

    # Generate each HTML file based on the entries (excluding microblog entries for separate generation)
    for entry in entries:
        generate_html_file(entry, entries, output_dir)

    # Generate the microblog page (now as index.html)
    generate_microblog_page(microblog_entries, entries, output_dir)

    # Generate the search index JSON file
    generate_search_index(entries, output_dir)


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
    <link rel="stylesheet" type="text/css" href="style.css">
</head>
<body>
<button class="toggle-btn" aria-label="Toggle Sidebar">☰</button>
<div class="sidebar">
    <nav>
        <ul>
            {generate_master_navigation(entries, entry)}
        </ul>
    </nav>
</div>
<div class="content">
    <h1>{title}</h1>
    {description}
</div>
<script src="script.js"></script>
</body>
</html>
"""
    # Save the HTML file with the title as the filename
    file_name = f"{title.replace(' ', '_').lower()}.html"
    with open(os.path.join(output_dir, file_name), 'w') as html_file:
        html_file.write(html_content)


def generate_microblog_page(microblog_entries, all_entries, output_dir):
    posts_per_page = 16
    total_pages = (len(microblog_entries) + posts_per_page - 1) // posts_per_page  # Ceiling division

    for page_num in range(1, total_pages + 1):
        html_content = f"""<html>
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Microblog - Page {page_num}</title>
<link rel="stylesheet" type="text/css" href="style.css">
</head>
<body>
<button class="toggle-btn" aria-label="Toggle Sidebar">☰</button>
<div class="sidebar">
    <nav>
        <ul>
            {generate_master_navigation(all_entries, None)}
        </ul>
    </nav>
</div>
<div class="content">
    <h1>Microblog - Page {page_num}</h1>
    <div class="microblog-feed">
        {generate_microblog_feed(microblog_entries, page_num, posts_per_page)}
    </div>
    <div class="pagination">
        {generate_pagination_controls(page_num, total_pages)}
    </div>
</div>
<div class="search">
    <input type="text" id="searchInput" placeholder="Search...">
    <div id="searchResults"></div>
</div>
<script src="script.js"></script>
</body>
</html>
"""

        # Save the first page as index.html (the homepage)
        file_name = "index.html" if page_num == 1 else f"microblog_page_{page_num}.html"
        with open(os.path.join(output_dir, file_name), 'w') as html_file:
            html_file.write(html_content)


def generate_microblog_feed(entries, page_num, posts_per_page):
    feed_content = ''
    start_index = (page_num - 1) * posts_per_page
    end_index = start_index + posts_per_page
    paginated_entries = entries[start_index:end_index]

    for entry in paginated_entries:
        title = entry.get('TITLE', 'Untitled')
        description = entry.get('DESCRIPTION', 'No content available.')

        feed_content += f"""<div class="microblog-entry">
        <h3>{title}</h3>
        <p>{description}</p>
        </div>
        <hr>
        """

    return feed_content


def generate_pagination_controls(current_page, total_pages):
    pagination_html = '<div class="pagination-controls">'

    # Previous button
    if current_page > 1:
        prev_page = "index.html" if current_page - 1 == 1 else f"microblog_page_{current_page - 1}.html"
        pagination_html += f'<a href="{prev_page}">Previous</a> '

    # Page numbers
    for page in range(1, total_pages + 1):
        if page == current_page:
            pagination_html += f'<span class="current-page">{page}</span> '
        else:
            page_link = "index.html" if page == 1 else f"microblog_page_{page}.html"
            pagination_html += f'<a href="{page_link}">{page}</a> '

    # Next button
    if current_page < total_pages:
        next_page = f"microblog_page_{current_page + 1}.html"
        pagination_html += f'<a href="{next_page}">Next</a>'

    pagination_html += '</div>'
    return pagination_html


def generate_master_navigation(entries, current_entry):
    nav_links = []
    
    # Get the master pages (excluding microblog TAG entries)
    master_pages = [entry for entry in entries if 'UNDER' not in entry and entry.get('TAG') != 'mb']
    
    for master_entry in master_pages:
        master_title = master_entry['TITLE']
        master_file_name = f"{master_title.replace(' ', '_').lower()}.html"

        # Add master page link
        nav_links.append(f'<li><a href="{master_file_name}">{master_title}</a></li>')

        # Add subpages for the master page
        sub_nav_links = [
            f'<li style="margin-left:20px;"><a href="{entry["TITLE"].replace(" ", "_").lower()}.html">{entry["TITLE"]}</a></li>'
            for entry in entries if entry.get('UNDER') == master_title and entry.get('TAG') != 'mb'
        ]
        
        if sub_nav_links:
            nav_links.append('<ul>' + ''.join(sub_nav_links) + '</ul>')
    
    # Add link to Microblog (which is now the home page, index.html)
    nav_links.append(f'<li><a href="index.html">Microblog</a></li>')

    return "\n".join(nav_links)


def generate_search_index(entries, output_dir):
    search_index = []
    for entry in entries:
        search_index.append({
            'title': entry.get('TITLE', 'Untitled'),
            'url': f"{entry.get('TITLE', 'Untitled').replace(' ', '_').lower()}.html"
        })

    # Save the search index as a JSON file
    search_index_path = os.path.join(output_dir, 'search_index.json')
    with open(search_index_path, 'w') as json_file:
        json.dump(search_index, json_file, indent=4)


# Example usage
generate_html_from_taia('elements.taia', 'microblog.taia', 'output_pages')
