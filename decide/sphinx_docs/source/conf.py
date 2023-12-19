# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

import os
import sys
import django

sys.path.insert(0, os.path.abspath('../../'))
os.environ['DJANGO_SETTINGS_MODULE'] = 'decide.settings'
django.setup()

project = 'decide'
copyright = '2023, Alejandro Medina Durán, Gonzalo Campos Mejías'
author = 'Alejandro Medina Durán, Gonzalo Campos Mejías'
release = '0.0.0'

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.viewcode',
    'sphinx.ext.napoleon'
]

templates_path = ['_templates']

exclude_patterns = [
    '*/migrations/*',
    '*/tests/*',
    '*/test/*',
    '*_test.py',
    '*tests.py',
    '*/static/*',
    '*/media/*',
    '*/admin.py',
    '__init__.py',
    'settings.py',
    'local_settings.py',
    '*/settings/*',
    'venv/',
    'env/',
    '*.git',
    '*.vscode'
    # ... other patterns you want to exclude
]


# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

master_doc = 'index'

html_theme = 'sphinx_book_theme'
html_static_path = ['_static']

html_theme_options = {
    "repository_url": "https://github.com/EGC-23-24/decide-part-lorca",
    "use_repository_button": True,
    "use_edit_page_button": True,
    "use_issues_button": True,
    "home_page_in_toc": True,
}

html_title = "decide-part-lorca"

autodoc_typehints = "description"

autodoc_class_signature = "separated"
