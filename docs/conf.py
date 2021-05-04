# Configuration file for the Sphinx documentation builder.
#
# This file only contains a selection of the most common options. For a full
# list see the documentation:
# http://www.sphinx-doc.org/en/master/config

# -- Path setup --------------------------------------------------------------

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.

import os
import sys

from recommonmark.transform import AutoStructify

import sanic_openapi

docs_directory = os.path.dirname(os.path.abspath(__file__))
root_directory = os.path.dirname(docs_directory)
sys.path.insert(0, root_directory)


# -- Project information -----------------------------------------------------

project = "Sanic-OpenAPI"
copyright = "2019, Sanic Community"
author = "Sanic Community"

version = sanic_openapi.__version__
release = sanic_openapi.__version__

# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = ["recommonmark", "sphinx.ext.autodoc"]

# Add any paths that contain templates here, relative to this directory.
templates_path = ["_templates"]

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]

master_doc = "index"

# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
html_theme = "sphinx_rtd_theme"

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ["_static"]
html_css_files = ["css/custom.css"]



def setup(app):
    app.add_config_value(
        "recommonmark_config",
        {
            "enable_eval_rst": True,
            "enable_auto_toc_tree": True,
            # "auto_toc_tree_section": "Contents",
        },
        True,
    )
    app.add_transform(AutoStructify)
