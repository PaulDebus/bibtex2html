from collections import defaultdict
import bibtexparser
from datetime import datetime
import re
import argparse

HTML_TEMPLATE_START = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Publications</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            max-width: 1000px;
            margin: 0 auto;
            padding: 20px;
            line-height: 1.6;
        }
        .publication {
            margin-bottom: 20px;
            padding: 15px;
            border: 1px solid #eee;
            border-radius: 5px;
        }
        .year-section {
            margin-top: 30px;
        }
        .year-heading {
            color: #333;
            border-bottom: 2px solid #333;
            margin-bottom: 20px;
        }
        .copy-button {
            background-color: #4CAF50;
            border: none;
            color: white;
            padding: 8px 16px;
            text-align: center;
            text-decoration: none;
            display: inline-block;
            font-size: 14px;
            margin: 4px 2px;
            cursor: pointer;
            border-radius: 4px;
        }
        .copy-button:hover {
            background-color: #45a049;
        }
        .hidden-bibtex {
            display: none;
        }
        .profile-section {
            margin-bottom: 40px;
            padding: 20px;
            background-color: #f5f5f5;
            border-radius: 5px;
        }
        .profile-links {
            margin-top: 10px;
        }
        .profile-links a {
            margin-right: 15px;
            color: #4CAF50;
            text-decoration: none;
        }
        .profile-links a:hover {
            text-decoration: underline;
        }
        .button-group {
            display: flex;
            gap: 10px;
        }
        .download-button {
            background-color: #2196F3;
            border: none;
            color: white;
            padding: 8px 16px;
            text-align: center;
            text-decoration: none;
            display: inline-block;
            font-size: 14px;
            margin: 4px 2px;
            cursor: pointer;
            border-radius: 4px;
        }
        .download-button:hover {
            background-color: #1976D2;
        }
        .download-button.disabled {
            background-color: #cccccc;
            cursor: not-allowed;
        }
        .author-highlight {
            font-weight: bold;
            color: #2196F3;
        }
        .publication-title {
            font-size: 1.1em;
            margin-bottom: 5px;
        }
        .publication-authors {
            margin-bottom: 5px;
        }
        .publication-info {
            color: #666;
        }
    </style>
</head>
<body>
    <div class="profile-section">
        <h1>Paul Debus</h1>
        <div class="profile-links">
            <a href="https://www.researchgate.net/profile/Paul-Debus" target="_blank">ResearchGate</a>
            <a href="https://scholar.google.com/citations?user=yh2m7bUAAAAJ&hl=en" target="_blank">Google Scholar</a>
            <a href="https://orcid.org/0000-0001-6228-588X" target="_blank">ORCID: 0000-0001-6228-588X</a>
        </div>
    </div>
'''

HTML_TEMPLATE_END = '''
    <script>
        async function copyBibtex(button) {
            const bibtex = button.parentElement.nextElementSibling.textContent;
            try {
                await navigator.clipboard.writeText(bibtex);
                const originalText = button.textContent;
                button.textContent = 'Copied!';
                setTimeout(() => {
                    button.textContent = originalText;
                }, 2000);
            } catch (err) {
                console.error('Failed to copy text: ', err);
            }
        }
    </script>
</body>
</html>
'''

def latex_to_unicode(text):
    """Convert LaTeX special characters to Unicode."""
    replacements = {
        r'\"a': 'ä',
        r'\"o': 'ö',
        r'\"u': 'ü',
        r'\"A': 'Ä',
        r'\"O': 'Ö',
        r'\"U': 'Ü',
        r'\ss': 'ß',
        r'\'e': 'é',
        r'\`e': 'è',
        r'\^e': 'ê',
        r'\'a': 'á',
        r'\`a': 'à',
        r'\^a': 'â',
        r'\'i': 'í',
        r'\`i': 'ì',
        r'\^i': 'î',
        r'\'o': 'ó',
        r'\`o': 'ò',
        r'\^o': 'ô',
        r'\'u': 'ú',
        r'\`u': 'ù',
        r'\^u': 'û',
        r'\&': '&',
        r'---': '—',
        r'--': '–',
        r'``': '"',
        r"''": '"',
        r'\textendash': '–',
        r'\textemdash': '—',
        r'\"{a}': 'ä',
        r'\"{o}': 'ö',
        r'\"{u}': 'ü',
        r'\"{A}': 'Ä',
        r'\"{O}': 'Ö',
        r'\"{U}': 'Ü',
        r'{\ss}': 'ß',
        r"\'{\i}": 'í',
        r'\copyright': '©',
        r'\%': '%',
        r'\$': '$',
        r'\#': '#',
        r'\_': '_',
        r'\{': '{',
        r'\}': '}',
    }
    
    for latex, unicode in replacements.items():
        text = text.replace(latex, unicode)
    
    # Remove any remaining curly braces
    text = re.sub(r'{([^{}]*)}', r'\1', text)
    
    return text

def format_authors(authors_str, highlight_name="Debus"):
    """Format authors list and highlight specific author."""
    # Convert LaTeX special characters before processing
    authors_str = latex_to_unicode(authors_str)
    
    authors = [author.strip() for author in authors_str.split(" and ")]
    formatted_authors = []
    
    for author in authors:
        if highlight_name in author:
            formatted_authors.append(f'<span class="author-highlight">{author}</span>')
        else:
            formatted_authors.append(author)
    
    if len(formatted_authors) > 1:
        return ", ".join(formatted_authors[:-1]) + ", & " + formatted_authors[-1]
    return formatted_authors[0]

def format_venue_info(entry):
    """Format publication venue information."""
    venue_info = []
    
    if entry.get('journal'):
        venue_info.append(latex_to_unicode(entry['journal']))
    elif entry.get('booktitle'):
        venue_info.append(f"In {latex_to_unicode(entry['booktitle'])}")
    
    if entry.get('volume'):
        venue_info.append(f"{entry['volume']}")
    
    if entry.get('number'):
        venue_info.append(f"({entry['number']})")
    
    if entry.get('pages'):
        venue_info.append(f"{entry['pages'].replace('--', '–')}")
    
    if entry.get('year'):
        venue_info.append(f"({entry['year']})")
    
    if entry.get('publisher'):
        venue_info.append(latex_to_unicode(entry['publisher']))
    
    return ", ".join(venue_info)

def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description='Generate an HTML publications page from a BibTeX file.',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
  %(prog)s -i publications.bib -o publications.html
  %(prog)s --highlight "Smith" --input refs.bib --output pubs.html
  %(prog)s --no-profile --input publications.bib
        '''
    )
    
    parser.add_argument('-i', '--input', 
                        default='publications.bib',
                        help='Input BibTeX file (default: publications.bib)')
    
    parser.add_argument('-o', '--output',
                        default='publications.html',
                        help='Output HTML file (default: publications.html)')
    
    parser.add_argument('--highlight',
                        default='Debus',
                        help='Author name to highlight (default: Debus)')
    
    parser.add_argument('--no-profile',
                        action='store_true',
                        help='Exclude the profile section from the output')
    
    return parser.parse_args()

def generate_html(*, input_file='publications.bib', 
                 output_file='publications.html',
                 highlight_name='Debus',
                 include_profile=True):
    """
    Generate HTML file from BibTeX entries.
    
    Args:
        input_file (str): Path to input BibTeX file
        output_file (str): Path to output HTML file
        highlight_name (str): Author name to highlight
        include_profile (bool): Whether to include the profile section
    """
    # Read BibTeX file
    try:
        bib_database = bibtexparser.parse_file(input_file)
    except FileNotFoundError:
        print(f"Error: Input file '{input_file}' not found")
        return
    except Exception as e:
        print(f"Error reading BibTeX file: {e}")
        return
    
    # Group by year
    years = defaultdict(list)
    for entry in bib_database.entries:
        year = entry.get('year', '').value if entry.get('year') else ''
        if year:  # Only include entries with a year
            years[year].append(entry)
    
    # Generate HTML
    html_content = []
    
    # Add the template start, optionally excluding profile section
    if not include_profile:
        # Remove profile section from template
        template_parts = HTML_TEMPLATE_START.split('<div class="profile-section">')
        profile_end = template_parts[1].find('</div>') + 6
        html_content.append(template_parts[0] + template_parts[1][profile_end:])
    else:
        html_content.append(HTML_TEMPLATE_START)
    
    # Add publications by year
    for year in sorted(years.keys(), reverse=True):
        html_content.append(f'    <div class="year-section">\n        <h2 class="year-heading">{year}</h2>')
        
        for entry in years[year]:
            html_content.append('''        <div class="publication">
            <p class="publication-title">{title}</p>
            <p class="publication-authors">{authors}</p>
            <p class="publication-info">{venue}</p>
            <div class="button-group">
                <button class="copy-button" onclick="copyBibtex(this)">Copy BibTeX</button>
                <button class="download-button disabled" onclick="alert('PDF not available yet')">Access PDF</button>
            </div>
            <div class="hidden-bibtex">{bibtex}</div>
        </div>'''.format(
                title=latex_to_unicode(entry['title']),
                authors=format_authors(entry['author'], highlight_name),
                venue=format_venue_info(entry),
                bibtex=entry.raw
            ))
        
        html_content.append('    </div>')
    
    html_content.append(HTML_TEMPLATE_END)
    
    # Write to file
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write('\n'.join(html_content))
        print(f"Successfully generated {output_file}")
    except Exception as e:
        print(f"Error writing output file: {e}")

if __name__ == "__main__":
    args = parse_args()
    generate_html(
        input_file=args.input,
        output_file=args.output,
        highlight_name=args.highlight,
        include_profile=not args.no_profile
    ) 