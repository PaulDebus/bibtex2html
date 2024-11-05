# Publication Page Generator

A Python script to generate a static HTML publications page from BibTeX data with copy-to-clipboard functionality for citations.

This tool was created mostly by Cursor as an experiment.

## Features

- Generates a HTML page from BibTeX entries
- Groups publications by year
- Highlights specified author names
- Provides BibTeX copy functionality
- Includes profile section with academic profile links
- Handles LaTeX special characters

## Requirements

```bash
pip install bibtexparser
```

## Usage

Basic usage with default settings:
```bash
python generate_publications.py
```

Custom input/output files:
```bash
python generate_publications.py -i refs.bib -o pubs.html
```

Additional options:
```bash
python generate_publications.py --highlight "Smith" --no-profile
```

## Arguments

- `-i, --input`: Input BibTeX file (default: publications.bib)
- `-o, --output`: Output HTML file (default: publications.html)
- `--highlight`: Author name to highlight (default: Debus)
- `--no-profile`: Exclude the profile section