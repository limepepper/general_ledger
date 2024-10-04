# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

import os
import sys
import django


sys.path.insert(0, os.path.abspath(os.path.join(os.pardir, os.pardir)))
from general_ledger import __version__ as release  # noqa
os.environ['DJANGO_SETTINGS_MODULE'] = 'dashboard.settings'
django.setup()

project = 'Lime Pepper General Ledger'
copyright = '2024, Tom Hodder'
author = 'Tom Hodder'
release = '0.0.1'

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.napoleon',
    'sphinx.ext.viewcode',
]

templates_path = ['_templates']
exclude_patterns = []



# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

# html_theme = 'alabaster'
html_theme = 'furo'

html_static_path = ['_static']
