# file neuxml/__init__.py
#
#   Copyright 2025 Center for Digital Humanities, Princeton University
#   Copyright 2010,2011 Emory University Libraries (eulxml)
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.

import os

from importlib import resources
from contextlib import ExitStack

__version__ = "1.0.0"

# Paths for XML catalog file & directory

# NOTE: these paths are defined here so they can easily be included
# without requiring the import of other parts of the code (e.g.
# in setup.py, which could be run when neuxml isn't fully installed)

#: relative path for schema data directory
SCHEMA_DATA_DIR = "schema_data"

# use package resources if possible, so this will work from an egg
# http://peak.telecommunity.com/DevCenter/PythonEggs#accessing-package-resources
if resources.files(__name__).joinpath(SCHEMA_DATA_DIR).is_dir():
    file_manager = ExitStack()
    ref = resources.files(__name__) / SCHEMA_DATA_DIR
    XMLCATALOG_DIR = file_manager.enter_context(resources.as_file(ref))
    file_manager = ExitStack()
    ref = resources.files(__name__) / ("%s/catalog.xml" % SCHEMA_DATA_DIR)
    XMLCATALOG_FILE = str(file_manager.enter_context(resources.as_file(ref)))
else:
    XMLCATALOG_DIR = os.path.join(os.path.dirname(__file__), SCHEMA_DATA_DIR)
    XMLCATALOG_FILE = os.path.join(XMLCATALOG_DIR, "catalog.xml")

# Add local XML catalog file to the environment variable so
# it will automatically be used by libxml to resolve URIs.
# See http://xmlsoft.org/catalog.html for more details.
# Only add once, even if neuxml is loaded multiple times.
if XMLCATALOG_FILE not in os.environ.get("XML_CATALOG_FILES", ""):
    os.environ["XML_CATALOG_FILES"] = ":".join(
        [
            path
            for path in (os.environ.get("XML_CATALOG_FILES"), XMLCATALOG_FILE)
            if path
        ]
    )
