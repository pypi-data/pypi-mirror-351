"""Unit Test for Catalog.py. Tests for download of schemas and catalog generation"""

# file test_xmlmap/test_core.py
#
#   Copyright 2025 Center for Digital Humanities, Princeton University
#   Copyright 2011 Emory University Libraries (eulxml)
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

#!/usr/bin/env python

import os
import unittest
from unittest.mock import patch
import tempfile
import glob
import shutil
from datetime import date
import neuxml
from lxml import etree
from neuxml import catalog
from requests.exceptions import HTTPError


CORRECT_SCHEMA = "http://www.loc.gov/standards/mods/v3/mods-3-4.xsd"
WRONG_SCHEMA = "http://www.loc.gov/standards/mods/v3/mods34.xsd"


def mocked_requests_get(*args, **kwargs):
    class MockResponse:
        def __init__(self, status_code):
            self.status_code = status_code

        def iter_content(self, chunk_size):
            with open("test/fixtures/mods-3-4.xsd", "rb") as file:
                while True:
                    chunk = file.read(chunk_size)
                    if not chunk:
                        break
                    yield chunk

        def raise_for_status(self):
            if self.status_code != 200:
                raise HTTPError(response=self)

    if args[0] == CORRECT_SCHEMA:
        return MockResponse(200)
    return MockResponse(404)


class TestGenerateSchema(unittest.TestCase):
    """:class:`TestGenerateSchema` class for Catalog testing"""

    def setUp(self):
        self.comment = "Downloaded by neuxml %s on %s" % (
            neuxml.__version__,
            date.today().isoformat(),
        )
        # parseString wants a url. let's give it a proper one.
        self.path = tempfile.mkdtemp()

    def tearDown(self):
        if os.path.isdir(self.path):
            shutil.rmtree(self.path)

    @patch("requests.get", side_effect=mocked_requests_get)
    def test_download_xml_schemas(self, mock_get):
        """Check if xsd schemas exist and download fresh copies"""
        filename = os.path.basename(CORRECT_SCHEMA)
        schema_path = os.path.join(self.path, filename)
        # do files already exist
        check_xsds = len(glob.glob("".join([self.path, "*.xsd"])))
        self.assertEqual(0, check_xsds)

        # downloading the wrong schema
        response_wrong = catalog.download_schema(
            WRONG_SCHEMA, schema_path, comment=None
        )
        self.assertFalse(response_wrong)

        # downloading the right schemas
        response_correct = catalog.download_schema(
            CORRECT_SCHEMA, schema_path, comment=None
        )
        self.assertTrue(response_correct)

        tree = etree.parse(schema_path)

        # Does comment exist?
        schema_string_no_comment = etree.tostring(tree)
        self.assertFalse(b"by neuxml" in schema_string_no_comment)

        # Add comment and check if it is there now
        catalog.download_schema(CORRECT_SCHEMA, schema_path, comment=self.comment)
        tree = etree.parse(schema_path)
        schema_string_with_comment = etree.tostring(tree)
        self.assertTrue(b"by neuxml" in schema_string_with_comment)

        # check if all files were downloaded
        self.assertEqual(1, len(glob.glob("".join([self.path, "/*.xsd"]))))

    def test_generate_xml_catalog(self):
        """Check if the catalog exists and import xml files into data files"""

        # check if catalog already exists
        check_catalog = len(glob.glob("".join([self.path, "/catalog.xml"])))
        self.assertEqual(0, check_catalog)
        catalog_file = os.path.join(self.path, "catalog.xml")
        filename = os.path.basename(CORRECT_SCHEMA)
        # generate empty catalog xml object
        with patch.object(catalog, "download_schema", return_value=True):
            gen_catalog = catalog.refresh_catalog(
                xsd_schemas=[CORRECT_SCHEMA],
                xmlcatalog_dir=self.path,
                xmlcatalog_file=catalog_file,
            )

        # check if catalog was generated
        check_catalog = len(glob.glob("".join([self.path, "/catalog.xml"])))
        self.assertEqual(1, check_catalog)

        # check elements of generated catalog
        self.assertEqual("catalog", gen_catalog.ROOT_NAME)
        self.assertEqual(
            "urn:oasis:names:tc:entity:xmlns:xml:catalog", gen_catalog.ROOT_NS
        )
        self.assertEqual({"c": gen_catalog.ROOT_NS}, gen_catalog.ROOT_NAMESPACES)
        self.assertEqual(1, len(gen_catalog.uri_list))

        # check correct name attribute
        self.assertEqual(CORRECT_SCHEMA, gen_catalog.uri_list[0].name)
        # check correct uri attribute
        self.assertEqual(filename, gen_catalog.uri_list[0].uri)

        # check how many uris we have in catalog
        self.assertEqual(len(gen_catalog.uri_list), 1)
