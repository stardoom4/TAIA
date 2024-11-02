import os
import shutil
import json

def generate_html_from_taia(file_path, output_dir, microblog_file):
    os.makedirs(output_dir, exist_ok=True)  # Create output directory if it doesn't exist
    entries = read_taia_file(file_path)
    microblog_entries = read_taia_file(microblog_file)

    # Copy the style.css and script.js file to the output directory
    for file_name in ['style.css', 'script.js']:
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

    # Copy the first microblog page to index.html
    index_path = os.path.join(output_dir, 'index.html')
    first_microblog_page_path = os.path.join(output_dir, 'microblog_page_1.html')
    
    if os.path.exists(first_microblog_page_path):
        shutil.copy(first_microblog_page_path, index_path)


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
            <a href="index.html">Home</a>
            {generate_master_navigation(entries, entry)} <!-- Recursive navigation generation -->
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


def generate_master_navigation(entries, current_entry, parent_id=None, level=0):
    # Filter entries that are children of the current parent_id
    child_entries = [entry for entry in entries if entry.get('PARENT') == parent_id]
    
    if not child_entries:
        return ""  # If no children, return empty string

    nav_links = '<ul>' if level > 0 else ''  # Nest only if we are below the top level
    
    for child_entry in child_entries:
        title = child_entry['TITLE']
        file_name = f"{title.replace(' ', '_').lower()}.html"
        indent_style = f"margin-left:{level * 20}px;"  # Indent each level

        nav_links += f'<li style="{indent_style}"><a href="{file_name}">{title}</a>'

        # Recursively add sub-navigation for the current child entry
        nav_links += generate_master_navigation(entries, current_entry, parent_id=child_entry['ID'], level=level+1)
        
        nav_links += '</li>'

    nav_links += '</ul>' if level > 0 else ''  # Close nested <ul> only if below top level
    return nav_links


def generate_microblog_page(microblog_entries, entries, output_dir):
    pagination_size = 16  # Show 16 posts per page
    num_pages = (len(microblog_entries) + pagination_size - 1) // pagination_size  # Calculate total pages

    for page_num in range(1, num_pages + 1):
        start_idx = (page_num - 1) * pagination_size
        end_idx = start_idx + pagination_size
        page_entries = microblog_entries[start_idx:end_idx]

        html_content = f"""<html>
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Wunder</title>
<link rel="stylesheet" type="text/css" href="style.css">
</head>
<body>
<input type="text" id="searchInput" placeholder="Search..." onkeyup="searchPages()">
<ul id="searchResults"></ul><button class="toggle-btn" aria-label="Toggle Sidebar">☰</button>
<div class="sidebar">
    <nav>
        <ul>
            {generate_master_navigation(entries, None)}  <!-- Include all master pages -->
        </ul>
    </nav>
</div>
<div class="content">
    <h1><a href="index.html">Wunder</a></h1>
    <div class="microblog-feed">
        {generate_microblog_feed(page_entries)}
    </div>
    {generate_pagination(page_num, num_pages)}
</div>
<script src="script.js"></script>
 <div class="footer">
<p>TAIA</p>
      </div>
</body>
</html>
"""
        # Save the microblog page with pagination
        file_name = f"microblog_page_{page_num}.html"
        with open(os.path.join(output_dir, file_name), 'w') as html_file:
            html_file.write(html_content)


def generate_microblog_feed(entries):
    feed_content = ''
    for entry in entries:
        title = entry.get('TITLE', 'Untitled')
        description = entry.get('DESCRIPTION', 'No content available.')
        sn = entry.get('SN', '0')  # Default to 0 if no SN is provided
        date = entry.get('DATE', 'Unknown Date')  # Default if no DATE is provided

        # Create a unique anchor link for each entry using the SN
        feed_content += f"""<div class="microblog-entry" id="post-{sn}">
        <h3>{title}</h3>
        <p class="microblog-date">{date}</p> <!-- Display the date -->
        <p>{description}</p>
        <a href="#post-{sn}" class="anchor-link">Link to this post</a> <!-- Anchor link -->
        </div>
        <hr>
        """

    return feed_content


def generate_pagination(current_page, total_pages):
    pagination_html = '<div class="pagination">'

    if current_page > 1:
        pagination_html += f'<a href="microblog_page_{current_page - 1}.html">&laquo; Previous</a>'

    for page in range(1, total_pages + 1):
        if page == current_page:
            pagination_html += f'<span class="current-page">{page}</span>'
        else:
            pagination_html += f'<a href="microblog_page_{page}.html">{page}</a>'

    if current_page < total_pages:
        pagination_html += f'<a href="microblog_page_{current_page + 1}.html">Next &raquo;</a>'

    pagination_html += '</div>'
    return pagination_html


def generate_search_index(entries, microblog_entries, output_dir):
    # Prepare search index with title and URLs only (no description)
    search_index = []

    all_entries = entries + microblog_entries
    for entry in all_entries:
        title = entry.get('TITLE', 'Untitled')
        file_name = f"{title.replace(' ', '_').lower()}.html" if entry.get('TAG') != 'mb' else "microblog.html"
        search_index.append({'title': title, 'url': file_name})

    # Save the search index as JSON
    with open(os.path.join(output_dir, 'search_index.json'), 'w') as json_file:
        json.dump(search_index, json_file, indent=2)


# Example usage
generate_html_from_taia('elements.taia', 'output_pages', 'microblog.taia')
