# Copyright 2025 Center for Digital Humanities, Princeton University
# SPDX-License-Identifier: Apache-2.0

from importlib import resources
from lxml import etree
import os
import re
import pytest
from pytest_socket import disable_socket
from unittest.mock import patch

import neuxml.schema_data
from neuxml import xmlmap


def pytest_runtest_setup():
    """Disable external network requests from tests"""
    disable_socket()


def get_xmlcatalog_dict():
    """map URLs in tests to local files (via our XML catalog) as a dict"""
    # get the base path for schema_data from anywhere in the package
    base_path = resources.files(neuxml.schema_data)

    # parse the XML catalog to extract name (URL), uri (local filename) attrs
    tree = etree.parse(str(base_path / "catalog.xml"))
    root = tree.getroot()
    # use the "c" namespace mapping from the xml catalog
    ns = {"c": "urn:oasis:names:tc:entity:xmlns:xml:catalog"}
    catalog_dict = {
        uri.get("name"): str(base_path / uri.get("uri"))
        for uri in root.findall("c:uri", ns)
    }

    return catalog_dict


# mark fixture as autouse so that it is opt-out instead of opt-in
@pytest.fixture(autouse=True)
def mock_loadSchema():
    """Mock loadSchema to prevent ever making requests to real web servers.
    Instead use local file mappings to load schemas for tests. Raise an error
    if the URL does not appear in the local file mapping."""

    # store the real function to call on files and filepaths
    loadSchema = xmlmap.loadSchema

    # xml catalog as a dict
    xml_catalog = get_xmlcatalog_dict()

    def mock_load_url(uri, *args, **kwargs):
        # if uri is bytes or path, not web address: use the real function
        if isinstance(uri, (bytes, os.PathLike)) or not re.match(r"^https?://", uri):
            return loadSchema(uri, *args, **kwargs)

        # uri is a web address, check if it's mapped to a local file
        if uri not in xml_catalog:
            raise ValueError(f"URI {uri} not found in XML catalog")

        # call real function on the local file
        return loadSchema(xml_catalog[uri], *args, **kwargs)

    with patch.object(xmlmap, "loadSchema", side_effect=mock_load_url):
        # after side effect, unapply patch
        yield
