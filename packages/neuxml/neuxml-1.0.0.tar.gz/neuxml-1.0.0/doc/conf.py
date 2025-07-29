# Copyright 2025 Center for Digital Humanities, Princeton University
# SPDX-License-Identifier: Apache-2.0

# Sphinx documentation build configuration file

import neuxml

extensions = ["sphinx.ext.autodoc", "sphinx.ext.intersphinx"]

templates_path = ["templates"]
exclude_trees = ["build"]
html_static_path = ["_static"]
source_suffix = ".rst"
master_doc = "index"

project = "neuxml"
copyright = "2025, Center for Digital Humanities at Princeton"
version = "%d.%d" % neuxml.__version_info__[:2]
release = neuxml.__version__
modindex_common_prefix = ["neuxml."]

html_theme = "alabaster"
html_style = "style.css"
html_theme_options = {
    # 'logo': 'logo.png',
    "github_user": "Princeton-CDH",
    "github_repo": "neuxml",
    "description": "Python library to read and write structured XML",
    # 'analytics_id':
}


html_sidebars = {
    "**": ["about.html", "navigation.html", "searchbox.html", "sidebar_footer.html"],
}


pygments_style = "sphinx"

# html_style = 'default.css'
# html_static_path = ['static']
htmlhelp_basename = "neuxmldoc"

latex_documents = [
    ("index", "neuxml.tex", "neuxml Documentation", "manual"),
]

# configuration for intersphinx: refer to the Python standard library
intersphinx_mapping = {
    "python": ("http://docs.python.org/", None),
}
