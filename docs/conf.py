# Configuration file for the Sphinx documentation builder.
#
# This file only contains a selection of the most common options. For a full
# list see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Path setup --------------------------------------------------------------

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
#
# import os
# import sys
# sys.path.insert(0, os.path.abspath('.'))
import os
import sys

# -- Project information -----------------------------------------------------

project = 'nti.property'
copyright = '2023 Jason Madden'
author = 'OpenNTI'


# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.autosummary',
    'sphinx.ext.doctest',
    'sphinx.ext.intersphinx',
    'sphinx.ext.todo',
    'sphinx.ext.viewcode',
]



# Add any paths that contain templates here, relative to this directory.
templates_path = ['_templates']

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']

# If true, '()' will be appended to :func: etc. cross-reference text.
add_function_parentheses = True

# If true, the current module name will be prepended to all description
# unit titles (such as .. function::).
add_module_names = False

# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
# furo: A customizable theme. Intended for smaller datasets, so if we
# grow too large we may want something different, like
# sphinx_book_theme.
#
# Theme gallery:https://sphinx-themes.org/
# Furo docs:See https://pradyunsg.me/furo/
# With Furo, we don't need to have individual ``.. contents::`` directives;
# if we move away from it we might want to add them back.



# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ['_static']

html_css_files = [
    'custom.css',
]

html_theme = 'furo'
html_theme_options = {
    'light_css_variables': {
        'font-stack': '"SF Pro",-apple-system,BlinkMacSystemFont,"Segoe UI",Helvetica,Arial,sans-serif,"Apple Color Emoji","Segoe UI Emoji"',
        'font-stack--monospace': '"JetBrainsMono", "JetBrains Mono", "JetBrains Mono Regular", "JetBrainsMono-Regular", ui-monospace, profont, monospace',
    },
}


## sphinx.ext.todo
# Display .. todo:: in the output.
todo_include_todos = True

## sphinx.ext.intersphinx


intersphinx_mapping = {
    'sphinx': ('https://www.sphinx-doc.org/en/master/', None),
    'elasticsearch': ('https://elasticsearch-py.readthedocs.io/en/v7.17.0/', None),
    'python': ('http://docs.python.org/', None,),
    'sqlalchemy': ('https://docs.sqlalchemy.org', None,),
    'zodb': ('http://zodb.readthedocs.io/en/latest/', None,),
    'interface': ('http://zopeinterface.readthedocs.io/en/latest/', None,),
    'component': ('http://zopecomponent.readthedocs.io/en/latest/', None,),
    'annotation': ('http://zopeannotation.readthedocs.io/en/latest/', None,),
    'location': ('http://zopelocation.readthedocs.io/en/latest/', None,),
    'zconfig': ('http://zconfig.readthedocs.io/en/latest/', None,),
}

# Sphinx 1.8+ prefers this to `autodoc_default_flags`. It's documented that
# either True or None mean the same thing as just setting the flag, but
# only None works in 1.8 (True works in 2.0)
autodoc_default_options = {
    'members': None,
    'show-inheritance': None,
    'special-members': '__enter__, __exit__',
}
autodoc_member_order = 'bysource'
autoclass_content = 'both'

autodoc_mock_imports = [
    # We sadly do lots of things at import time that have side effects.
    # Until we fix that, mock some of them out.
    'multiprocessing',
    'boto3',
    # XXX: Internal circular dependencies
    #'data_model',
    #'mongo',
]

# The reST default role (used for this markup: `text`) to use for all documents.
# Using obj lets it create links automatically to code.
default_role = 'obj'
