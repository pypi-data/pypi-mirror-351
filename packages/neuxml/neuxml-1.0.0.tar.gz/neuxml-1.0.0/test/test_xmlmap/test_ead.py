# file test_xmlmap/test_ead.py
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

import unittest
import os

from neuxml.xmlmap import eadmap
from neuxml.xmlmap.core import load_xmlobject_from_file, load_xmlobject_from_string


class TestEad(unittest.TestCase):
    FIXTURE_FILE = os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "fixtures", "heaney653.xml"
    )

    def setUp(self):
        self.ead = load_xmlobject_from_file(
            self.FIXTURE_FILE, eadmap.EncodedArchivalDescription
        )

    def test_init(self):
        self.assertTrue(isinstance(self.ead, eadmap.EncodedArchivalDescription))

    def test_basic_fields(self):
        self.assertEqual(str(self.ead.title), "Seamus Heaney collection, 1972-1997")
        self.assertEqual(str(self.ead.eadid), "heaney653")
        self.assertEqual(self.ead.id, "heaney653-011")
        self.assertEqual(
            self.ead.author,
            "Manuscript, Archives, and Rare Book Library, Emory University",
        )
        # whitespace makes fields with tags a bit messier...
        self.assertTrue("Seamus Heaney collection," in str(self.ead.unittitle))
        self.assertTrue("1972-2005" in str(self.ead.unittitle))
        # several different extents in the physical description;
        # FIXME: all smashed together
        self.assertTrue("1 linear ft." in self.ead.physical_desc)
        self.assertTrue("(3 boxes)" in self.ead.physical_desc)
        self.assertTrue("12 oversized papers (OP)" in self.ead.physical_desc)
        self.assertTrue(
            "materials relating to Irish poet Seamus Heaney" in str(self.ead.abstract)
        )

    def test_validation(self):
        # EAD objects can now be validated aginst XSD schema
        self.assertTrue(self.ead.schema_valid())

    def test_eadid(self):
        self.assertTrue(isinstance(self.ead.eadid, eadmap.EadId))
        eadid = self.ead.eadid
        self.assertEqual("heaney653", eadid.value)
        self.assertEqual("heaney653.xml", eadid.identifier)
        self.assertEqual("US", eadid.country)
        self.assertEqual("geu-s", eadid.maintenance_agency)
        self.assertEqual("http://some.pid.org/ark:/1234/567", eadid.url)

    def test_ArchivalDescription(self):
        self.assertTrue(isinstance(self.ead.archdesc, eadmap.ArchivalDescription))
        ad = self.ead.archdesc
        self.assertEqual("Heaney, Seamus, 1939-", ad.origination)
        self.assertTrue(isinstance(ad.unitid, eadmap.Unitid))
        self.assertEqual("Manuscript Collection No.653", ad.unitid.value)
        self.assertEqual("Manuscript Collection No.653", str(ad.unitid))
        self.assertEqual("US", ad.unitid.country_code)
        self.assertEqual("geu-s", ad.unitid.repository_code)
        self.assertEqual(653, ad.unitid.identifier)
        self.assertEqual("1 linear ft.", ad.extent[0])
        self.assertEqual("(3 boxes)", ad.extent[1])
        self.assertEqual("12 oversized papers (OP)", ad.extent[2])
        self.assertEqual("Materials entirely in English.", ad.langmaterial)
        self.assertEqual("In the Archives.", ad.location)
        self.assertTrue(isinstance(ad.access_restriction, eadmap.Section))
        self.assertEqual("Restrictions on access", str(ad.access_restriction.head))
        self.assertTrue(
            "Special restrictions apply" in str(ad.access_restriction.content[0])
        )
        self.assertTrue(isinstance(ad.use_restriction, eadmap.Section))
        self.assertEqual(
            "Terms Governing Use and Reproduction", str(ad.use_restriction.head)
        )
        self.assertTrue(
            "limitations noted in departmental policies"
            in str(ad.use_restriction.content[0])
        )
        self.assertTrue(isinstance(ad.alternate_form, eadmap.Section))
        self.assertEqual("Publication Note", str(ad.alternate_form.head))
        self.assertTrue("Published in" in str(ad.alternate_form.content[0]))
        self.assertTrue(isinstance(ad.originals_location, eadmap.Section))
        self.assertEqual("Location of Originals", str(ad.originals_location.head))
        self.assertTrue("Suppressed chapter" in str(ad.originals_location.content[0]))
        self.assertTrue(isinstance(ad.related_material, eadmap.Section))
        self.assertEqual(
            "Related Materials in This Repository", str(ad.related_material.head)
        )
        self.assertTrue("part of MSS" in str(ad.related_material.content[0]))
        self.assertTrue(isinstance(ad.separated_material, eadmap.Section))
        self.assertEqual(
            "Related Materials in This Repository", str(ad.separated_material.head)
        )
        self.assertTrue(
            "Ciaran Carson papers, Peter Fallon"
            in str(ad.separated_material.content[0])
        )
        self.assertTrue(isinstance(ad.acquisition_info, eadmap.Section))
        self.assertEqual("Source", str(ad.acquisition_info.head))
        self.assertTrue(
            "Collection assembled from various sources."
            in str(ad.acquisition_info.content[0])
        )
        self.assertTrue(isinstance(ad.custodial_history, eadmap.Section))
        self.assertEqual("Custodial History", str(ad.custodial_history.head))
        self.assertTrue(
            "Originally received as part of" in str(ad.custodial_history.content[0])
        )
        self.assertTrue(isinstance(ad.preferred_citation, eadmap.Section))
        self.assertEqual("Citation", str(ad.preferred_citation.head))
        self.assertTrue(
            "[after identification of item(s)" in str(ad.preferred_citation.content[0])
        )
        self.assertTrue(isinstance(ad.biography_history, eadmap.Section))
        self.assertEqual("Biographical Note", str(ad.biography_history.head))
        self.assertTrue("born on April 13" in str(ad.biography_history.content[0]))
        self.assertTrue("While at St. Joseph's" in str(ad.biography_history.content[1]))
        self.assertTrue(isinstance(ad.bibliography, eadmap.Section))
        self.assertEqual("Publication Note", str(ad.bibliography.head))
        self.assertTrue("Susan Jenkins Brown" in str(ad.bibliography.content[0]))
        self.assertTrue(isinstance(ad.scope_content, eadmap.Section))
        self.assertEqual("Scope and Content Note", str(ad.scope_content.head))
        self.assertTrue(
            "consists of materials relating" in str(ad.scope_content.content[0])
        )
        self.assertTrue(isinstance(ad.arrangement, eadmap.Section))
        self.assertEqual("Arrangement Note", str(ad.arrangement.head))
        self.assertTrue("five series" in str(ad.arrangement.content[0]))
        self.assertTrue(isinstance(ad.other, eadmap.Section))
        self.assertEqual("Finding Aid Note", str(ad.other.head))
        self.assertTrue("Index to selected correspondents" in str(ad.other.content[0]))

    def test_index_indexentry(self):
        ad = self.ead.archdesc
        # index and indexentry
        self.assertEqual(2, len(ad.index))
        index = ad.index[0]
        self.assertTrue(isinstance(index, eadmap.Index))
        self.assertEqual("Index of Selected Correspondents", str(index.head))
        self.assertEqual("index1", index.id)
        self.assertTrue(
            "relates to the correspondence in Series 1" in str(index.note.content[0])
        )
        self.assertEqual(2, len(index.entry))
        self.assertTrue(isinstance(index.entry[0], eadmap.IndexEntry))
        self.assertEqual("Batten, Guinn", str(index.entry[0].name))
        self.assertTrue(isinstance(index.entry[0].ptrgroup, eadmap.PointerGroup))
        self.assertEqual(3, len(index.entry[0].ptrgroup.ref))
        self.assertTrue(isinstance(index.entry[0].ptrgroup.ref[0], eadmap.Reference))
        self.assertEqual("simple", index.entry[0].ptrgroup.ref[0].type)
        self.assertTrue("1995 July" in str(index.entry[0].ptrgroup.ref[0].value))
        self.assertEqual("Belton, Neil", str(index.entry[1].name))
        self.assertTrue("1993 November 3" in str(index.entry[1].ptrgroup.ref[-1].value))

        # multiple indexes
        self.assertTrue(isinstance(ad.index[1], eadmap.Index))
        self.assertEqual("Second Index", str(ad.index[1].head))
        self.assertEqual("index2", ad.index[1].id)

    def test_ControlledAccessHeadings(self):
        ca = self.ead.archdesc.controlaccess
        self.assertTrue(isinstance(ca, eadmap.ControlledAccessHeadings))
        self.assertEqual("Selected Search Terms", str(ca.head))
        self.assertTrue(
            isinstance(ca.controlaccess[0], eadmap.ControlledAccessHeadings)
        )
        self.assertEqual("Personal Names", str(ca.controlaccess[0].head))
        self.assertTrue(isinstance(ca.controlaccess[0].person_name[0], eadmap.Heading))
        self.assertEqual("Barker, Sebastian.", ca.controlaccess[0].person_name[0].value)
        self.assertTrue(isinstance(ca.controlaccess[0].family_name[0], eadmap.Heading))
        self.assertEqual("Dozier family.", ca.controlaccess[0].family_name[0].value)
        self.assertEqual(
            "English poetry--Irish authors--20th century.",
            ca.controlaccess[1].subject[0].value,
        )
        self.assertEqual("Ireland.", ca.controlaccess[2].geographic_name[0].value)
        self.assertEqual("Manuscripts.", ca.controlaccess[3].genre_form[0].value)
        self.assertEqual("Poet.", ca.controlaccess[4].occupation[0].value)
        self.assertTrue(
            isinstance(ca.controlaccess[5].corporate_name[0], eadmap.Heading)
        )
        self.assertEqual(
            "Irish Academy of Letters", ca.controlaccess[5].corporate_name[0].value
        )
        self.assertTrue(isinstance(ca.controlaccess[6].function[0], eadmap.Heading))
        self.assertEqual("Law enforcing.", ca.controlaccess[6].function[0].value)
        self.assertTrue(isinstance(ca.controlaccess[7].title[0], eadmap.Heading))
        self.assertEqual(
            "New Yorker (New York, 1925-)", ca.controlaccess[7].title[0].value
        )

        # terms -  mapps to all types, mixed, in the order they appear
        all_terms = ca.controlaccess[8].terms
        self.assertEqual("title", all_terms[0].value)
        self.assertEqual("person", all_terms[1].value)
        self.assertEqual("family", all_terms[2].value)
        self.assertEqual("corp", all_terms[3].value)
        self.assertEqual("occupation", all_terms[4].value)
        self.assertEqual("subject", all_terms[5].value)
        self.assertEqual("geography", all_terms[6].value)
        self.assertEqual("genre", all_terms[7].value)
        self.assertEqual("function", all_terms[8].value)

    def test_SubordinateComponents(self):
        dsc = self.ead.dsc
        self.assertTrue(isinstance(dsc, eadmap.SubordinateComponents))
        self.assertEqual("combined", dsc.type)
        self.assertEqual("Description of Series", str(dsc.head))
        # c01 - series
        self.assertTrue(isinstance(dsc.c[0], eadmap.Component))
        self.assertEqual("series", dsc.c[0].level)
        self.assertTrue(isinstance(dsc.c[0].did, eadmap.DescriptiveIdentification))
        self.assertEqual("Series 1", dsc.c[0].did.unitid.value)
        self.assertEqual("Writings by Seamus Heaney", str(dsc.c[0].did.unittitle))
        self.assertEqual("Box 1: folders 1-12", dsc.c[0].did.physdesc)
        # c02 - file
        self.assertTrue(isinstance(dsc.c[0].c[0], eadmap.Component))
        self.assertEqual("file", dsc.c[0].c[0].level)
        self.assertTrue(isinstance(dsc.c[0].c[0].did, eadmap.DescriptiveIdentification))
        self.assertTrue("holograph manuscript" in str(dsc.c[0].c[0].did.unittitle))
        self.assertEqual("box", dsc.c[0].c[0].did.container[0].type)
        self.assertEqual("1", dsc.c[0].c[0].did.container[0].value)
        self.assertEqual("folder", dsc.c[0].c[0].did.container[1].type)
        self.assertEqual("1", dsc.c[0].c[0].did.container[1].value)

        self.assertTrue(dsc.hasSeries())
        self.assertFalse(dsc.c[0].hasSubseries())

        # second series has a subseries
        self.assertTrue(dsc.c[1].hasSubseries())
        # access c03 level item
        self.assertEqual("file", dsc.c[1].c[0].c[0].level)
        self.assertTrue("Hilary Boyle" in str(dsc.c[1].c[0].c[0].did.unittitle))

    def test_SubordinateComponents_noseries(self):
        # simple finding aid with no series but only a container list
        simple_dsc = """<dsc><c01 level="file"/></dsc>"""
        dsc = load_xmlobject_from_string(simple_dsc, eadmap.SubordinateComponents)
        self.assertFalse(dsc.hasSeries())

    def test_FileDescription(self):
        filedesc = self.ead.file_desc
        self.assertTrue(isinstance(filedesc, eadmap.FileDescription))
        self.assertTrue(isinstance(filedesc.publication, eadmap.PublicationStatement))
        self.assertTrue(isinstance(filedesc.publication.address, eadmap.Address))
        self.assertTrue(isinstance(filedesc.publication.date, eadmap.DateField))
        self.assertEqual("Emory University", filedesc.publication.publisher)
        self.assertEqual(
            "Robert W. Woodruff Library", filedesc.publication.address.lines[0]
        )
        self.assertEqual("404-727-6887", filedesc.publication.address.lines[3])
        self.assertEqual("marbl@emory.edu", filedesc.publication.address.lines[-1])

    def test_ProfileDescription(self):
        profiledesc = self.ead.profiledesc
        self.assertTrue(isinstance(profiledesc, eadmap.ProfileDescription))
        self.assertEqual("English", profiledesc.languages[0])
        self.assertEqual("eng", profiledesc.language_codes[0])
        # profile creation date
        self.assertTrue(isinstance(profiledesc.date, eadmap.DateField))
        self.assertEqual("May 5, 2005", str(profiledesc.date))
        self.assertEqual("2005-05-05", profiledesc.date.normalized)

    def test_DateField(self):
        date = self.ead.file_desc.publication.date
        self.assertTrue(isinstance(date, eadmap.DateField))
        self.assertEqual("2005-05-05", date.normalized)
        self.assertEqual("May 5, 2005", str(date))
        self.assertEqual("ce", date.era)
        self.assertEqual("gregorian", date.calendar)

        unitdate = self.ead.dsc.c[1].c[0].did.unitdate
        self.assertTrue(isinstance(unitdate, eadmap.DateField))
        self.assertEqual("1974/1986", unitdate.normalized)

    def test_unittitle(self):
        title = self.ead.unittitle
        self.assertTrue(isinstance(title, eadmap.UnitTitle))
        self.assertTrue(isinstance(title.short, eadmap.UnitTitle))
        self.assertTrue(isinstance(title.unitdate, eadmap.DateField))
        self.assertEqual("1972-2005", str(title.unitdate))
        # short title
        self.assertEqual("Seamus Heaney collection,", str(title.short))
        self.assertEqual(
            "Writings by Seamus Heaney", str(self.ead.dsc.c[0].did.unittitle.short)
        )

    def test_DigitalArchivalObject(self):
        # test dao inserted in did of first container-level item, series 1
        dao = self.ead.dsc.c[0].c[0].did.dao_list[0]
        self.assertTrue(isinstance(dao, eadmap.DigitalArchivalObject))
        self.assertEqual("internal", dao.audience)
        self.assertEqual("id1234", dao.id)
        self.assertEqual("Digitized Content", dao.title)
        self.assertEqual("http://some.url/item/id1234", dao.href)
