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