import os
import shutil
import json
import re

def generate_html_from_taia(file_path, output_dir, microblog_file):
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

    # Generate tag pages
    generate_tag_pages(entries, output_dir)

    # Generate the microblog page with pagination
    generate_microblog_page(microblog_entries, entries, output_dir)

    # Generate search index file
    generate_search_index(entries, microblog_entries, output_dir)

    # Copy the first microblog page to index.html
    index_path = os.path.join(output_dir, 'index.html')
    first_microblog_page_path = os.path.join(output_dir, 'splash.html')
    
    if os.path.exists(first_microblog_page_path):
        shutil.copy(first_microblog_page_path, index_path)


def format_text(text):
    """
    Parses custom syntax in the text and returns HTML.
    """
    # Regex patterns for various syntax
    link_pattern = r'\(link "([^"]+)"(?: "([^"]+)")?\)'
    bold_pattern = r'\(bold "([^"]+)"\)'
    ital_pattern = r'\(ital "([^"]+)"\)'

    # Recursive replacement for nested formatting
    while re.search(link_pattern, text) or re.search(bold_pattern, text) or re.search(ital_pattern, text):
        text = re.sub(link_pattern, lambda m: f'<a href="{m.group(1)}">{m.group(2) if m.group(2) else m.group(1)}</a>', text)
        text = re.sub(bold_pattern, lambda m: f'<strong>{m.group(1)}</strong>', text)
        text = re.sub(ital_pattern, lambda m: f'<em>{m.group(1)}</em>', text)

    return text

def replace_internal_links(content):
    """
    Replaces internal link syntax (intl "page") with HTML links.
    """
    # Regex to match the internal link syntax
    pattern = r'\(intl\s+"([^"]+)"\)'
    
    # Replace the pattern with a proper link
    def link_replacer(match):
        page_title = match.group(1)  # Get the page title from the match
        link = f'{page_title.replace(" ", "_").lower()}.html'  # Create the link URL
        return f'<a href="{link}">{page_title}</a>'  # Return the HTML link
    
    # Substitute all matches in the content
    return re.sub(pattern, link_replacer, content)

def generate_tag_pages(entries, output_dir):
    # Create a set of unique tags
    all_tags = set()
    for entry in entries:
        tags = entry.get('TAGS', '')
        for tag in tags.split(','):
            all_tags.add(tag.strip().lower())  # Normalize and add to the set

    # Generate a page for each tag
    for tag in all_tags:
        html_content = f"""<html>
<!DOCTYPE html>
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{tag.capitalize()} Posts</title>
<link rel="stylesheet" type="text/css" href="style.css">
</head>
<body>
<input type="text" id="searchInput" placeholder="Search..." onkeyup="searchPages()">
<ul id="searchResults"></ul><button class="toggle-btn" aria-label="Toggle Sidebar">☰</button>
<div class="sidebar">
    <nav>
        <ul>
            <a href="microblog_page_1.html">Home</a>
            {generate_category_navigation(entries, None)}
        </ul>
    </nav>
</div>
<div class="content">
    <h1>Tagged with "{tag.capitalize()}"</h1>
    <ul>
        {generate_tagged_entries(entries, tag)}
    </ul>
</div>
<script src="script.js"></script>
 <div class="footer">
<p>TAIA</p>
      </div>
</body>
</html>
"""
        tag_file_name = f"tag_{tag}.html"
        with open(os.path.join(output_dir, tag_file_name), 'w') as html_file:
            html_file.write(html_content)


def generate_tagged_entries(entries, tag):
    # Find all entries that have the specified tag
    tagged_entries = [entry for entry in entries if tag in [t.strip().lower() for t in entry.get('TAGS', '').split(',')]]
    
    # Generate HTML links for each tagged entry
    entries_html = ''
    for entry in tagged_entries:
        title = entry.get('TITL', 'Untitled')
        file_name = f"{title.replace(' ', '_').lower()}.html"
        entries_html += f'<li><a href="{file_name}">{title}</a></li>\n'

    return entries_html


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
    title = entry.get('TITL', 'Untitled')
    description = format_text(entry.get('DESC', 'No content available.'))
    tags = entry.get('TAGS', '').split(',')  # Get tags, split by comma

    content_with_links = replace_internal_links(description)

    # Generate the navigation menu with dynamic visibility for second master and subpages
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
            <a href="microblog_page_1.html">Home</a>
            {generate_category_navigation(entries, entry)}
        </ul>
    </nav>
</div>
<div class="content">
    <h1>{title}</h1>
    <p>{description}</p>
    <p>Tags: {', '.join([f'<a href="tag_{tag.strip().lower()}.html">{tag.strip()}</a>' for tag in tags])}</p>  <!-- Clickable tags -->
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


def generate_category_navigation(entries, current_entry):
    nav_links = []
    current_master_title = None

    # If `current_entry` is not None, get its master title
    if current_entry:
        current_master_title = current_entry.get('UNDE')

    # Get all master pages
    master_pages = [entry for entry in entries if 'UNDE' not in entry]

    for master_entry in master_pages:
        master_title = master_entry['TITL']
        master_file_name = f"{master_title.replace(' ', '_').lower()}.html"

        # Add link for the master page
        nav_links.append(f'<li><a href="{master_file_name}">{master_title}</a></li>')

        # Check if this master page is the current page or its parent
        is_current_master = current_entry and (
            master_entry == current_entry or master_title == current_master_title
        )

        # Generate navigation for second-level masters and subpages
        if is_current_master:
            second_master_pages = [entry for entry in entries if entry.get('UNDE') == master_title]

            for second_master in second_master_pages:
                second_master_title = second_master['TITL']
                second_master_file_name = f"{second_master_title.replace(' ', '_').lower()}.html"
                nav_links.append(f'<li style="margin-left:20px;"><a href="{second_master_file_name}">{second_master_title}</a></li>')

                # Generate navigation for subpages
                sub_pages = [entry for entry in entries if entry.get('UNDE') == second_master_title]
                if sub_pages:
                    sub_nav_links = [
                        f'<li style="margin-left:40px;"><a href="{entry["TITL"].replace(" ", "_").lower()}.html">{entry["TITL"]}</a></li>'
                        for entry in sub_pages
                    ]
                    nav_links.append('<ul>' + ''.join(sub_nav_links) + '</ul>')

    return "\n".join(nav_links)


def generate_microblog_page(microblog_entries, entries, output_dir):
    pagination_size = 16  # Show 16 posts per page
    num_pages = (len(microblog_entries) + pagination_size - 1) // pagination_size  # Calculate total pages

    for page_num in range(1, num_pages + 1):
        start_idx = (page_num - 1) * pagination_size
        end_idx = start_idx + pagination_size
        page_entries = microblog_entries[start_idx:end_idx]

        html_content = f"""<html>
<!DOCTYPE html>       
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
            {generate_category_navigation(entries, None)}  <!-- Include all master pages -->
        </ul>
    </nav>
</div>
<div class="content">
    <h1><a href="microblog_page_1.html">Wunder</a></h1>
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
        title = entry.get('TITL', 'Untitled')
        description = entry.get('DESC', 'No content available.')
        sn = entry.get('SNNO', '0')  # Default to 0 if no SN is provided
        date = entry.get('DATE', 'Unknown Date')  # Default if no DATE is provided

        # Create a unique anchor link for each entry using the SN
        feed_content += f"""<div class="microblog-entry" id="post-{sn}">
        <h3>{title}</h3>
        <p class="microblog-date">{date}</p> <!-- Display the date -->
        <p>{description}</p>
        <a href="#post-{sn}" class="anchor-link">Ø</a> <!-- Anchor link -->
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
        title = entry.get('TITL', 'Untitled')
        file_name = f"{title.replace(' ', '_').lower()}.html" if entry.get('TAG') != 'mb' else "microblog.html"
        search_index.append({'title': title, 'url': file_name})

    # Save the search index as JSON
    with open(os.path.join(output_dir, 'search_index.json'), 'w') as json_file:
        json.dump(search_index, json_file, indent=2)


# Example usage
generate_html_from_taia('database/lexicon.taia', 'output_pages', 'database/microblog.taia')
