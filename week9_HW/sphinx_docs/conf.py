# Configuration file for the Sphinx documentation builder.

# -- Project information -----------------------------------------------------
project = 'Week9 고전역학 시뮬레이션'
copyright = '2026, 202312140 윤서영'
author = '202312140 윤서영'
release = '1.0'

# -- General configuration ---------------------------------------------------
extensions = [
    'myst_parser',
]

source_suffix = {
    '.rst': 'restructuredtext',
    '.md': 'markdown',
}

templates_path = ['_templates']
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']

language = 'ko'

# -- Options for HTML output -------------------------------------------------
html_theme = 'alabaster'
html_static_path = ['_static']

html_theme_options = {
    'page_width': '1100px',
    'sidebar_width': '260px',
}
