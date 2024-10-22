import os
import shutil

def generate_html_from_taia(file_path, output_dir):
    os.makedirs(output_dir, exist_ok=True)  # Create output directory if it doesn't exist
    entries = read_taia_file(file_path)

    # Copy the style.css file to the output directory
    if os.path.exists('style.css'):
        shutil.copy('style.css', os.path.join(output_dir, 'style.css'))

    # Generate each HTML file based on the entries
    for entry in entries:
        generate_html_file(entry, entries, output_dir)

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
<input type="checkbox" id="sidebar-toggle">
    <label for="sidebar-toggle" class="toggle-btn" aria-label="Toggle Sidebar">☰</label>
    <nav>
    <div class="sidebar">
        <ul>
            {generate_master_navigation(entries, entry)}
        </ul>
    </nav>
    </div>
    <div class="content">
    <h1>{title}</h1>
    {description} </div> <!-- Description can contain HTML tags -->
</body>
</html>
"""
    # Save the HTML file with the title as the filename
    file_name = f"{title.replace(' ', '_').lower()}.html"
    with open(os.path.join(output_dir, file_name), 'w') as html_file:
        html_file.write(html_content)

def generate_master_navigation(entries, current_entry):
    nav_links = []
    
    # Get the master pages
    master_pages = [entry for entry in entries if 'UNDER' not in entry]
    
    for master_entry in master_pages:
        master_title = master_entry['TITLE']
        master_file_name = f"{master_title.replace(' ', '_').lower()}.html"

        # Add master page link
        nav_links.append(f'<li><a href="{master_file_name}">{master_title}</a></li>')

        # If the current page is a master page, show its subpages
        if master_entry == current_entry:  # Check if we are on a master page
            sub_nav_links = [
                f'<li style="margin-left:20px;"><a href="{entry["TITLE"].replace(" ", "_").lower()}.html">{entry["TITLE"]}</a></li>'
                for entry in entries if entry.get('UNDER') == master_title
            ]
            
            if sub_nav_links:
                nav_links.append('<ul>' + ''.join(sub_nav_links) + '</ul>')
    
    return "\n".join(nav_links)

# Example usage
generate_html_from_taia('elements.taia', 'output_pages')
