# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = 'Polaris'
copyright = '2026, Heazo, VvSilv'
author = 'Heazo, VvSilv'

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.napoleon',      # Для Google/NumPy стиля docstring
    'sphinx.ext.viewcode',      # Ссылки на исходный код
    'sphinx.ext.intersphinx',   # Ссылки на другие проекты
    'sphinx.ext.todo'
]

templates_path = ['_templates']
exclude_patterns = []

language = 'ru'

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = 'sphinx_rtd_theme'    #sphinx_rtd_theme #alabaster
html_static_path = ['_static']
todo_include_todos = True  # показывать TODO в готовой документации