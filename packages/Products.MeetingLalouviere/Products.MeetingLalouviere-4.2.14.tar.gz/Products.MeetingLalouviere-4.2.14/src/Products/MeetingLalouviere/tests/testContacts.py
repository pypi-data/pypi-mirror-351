# -*- coding: utf-8 -*-
#
# File: testMeetingGroup.py
#
# GNU General Public License (GPL)
#

from collective.contact.plonegroup.utils import get_own_organization
from plone import api
from Products.MeetingCommunes.tests.testContacts import testContacts as mctc
from Products.MeetingLalouviere.config import DG_GROUP_ID
from Products.MeetingLalouviere.config import INTREF_GROUP_ID
from Products.MeetingLalouviere.tests.MeetingLalouviereTestCase import MeetingLalouviereTestCase
from Products.PloneMeeting.Extensions.imports import import_contacts

import os
import Products


class testContacts(mctc, MeetingLalouviereTestCase):
    """Tests the contacts related methods."""

    def test_pm_ImportContactsCSV(self):
        """ """
        self.changeUser("pmManager")
        contacts = self.portal.contacts
        # initialy, we have 4 persons and 4 held_positions
        own_org = get_own_organization()
        self.assertIsNone(own_org.acronym)
        # 5 internal and 2 external organizations
        self.assertEqual(len(api.content.find(context=contacts, portal_type="organization")), 8)
        self.assertEqual(len(api.content.find(context=contacts, portal_type="person")), 4)
        self.assertEqual(len(api.content.find(context=contacts, portal_type="held_position")), 4)
        path = os.path.join(os.path.dirname(Products.PloneMeeting.__file__), "profiles/testing")
        output = import_contacts(self.portal, path=path)
        self.assertEqual(output, "You must be a zope manager to run this script")
        self.changeUser("siteadmin")
        output = import_contacts(self.portal, path=path)
        self.assertEqual(output, "You must be a zope manager to run this script")

        # import contacts as Zope admin
        self.changeUser("admin")
        import_contacts(self.portal, path=path)
        # we imported 10 organizations and 15 persons/held_positions
        self.assertEqual(len(api.content.find(context=contacts, portal_type="organization")), 17)
        self.assertEqual(len(api.content.find(context=contacts, portal_type="person")), 19)
        self.assertEqual(len(api.content.find(context=contacts, portal_type="held_position")), 19)
        # organizations are imported with an acronym
        self.assertEqual(own_org.acronym, u"OwnOrg")
        org_gc = contacts.get("groupe-communes")
        self.assertEqual(org_gc.acronym, u"GComm")
        # hp of agent-interne is correctly linked to plonegroup-organization
        own_org = get_own_organization()
        agent_interne_hp = contacts.get("agent-interne").objectValues()[0]
        self.assertEqual(agent_interne_hp.portal_type, "held_position")
        self.assertEqual(agent_interne_hp.get_organization(), own_org)
        # we can import organizations into another, we imported 4 orgs under my org
        self.assertListEqual(
            [org.id for org in own_org.objectValues()],
            [
                "developers",
                "vendors",
                "endUsers",
                DG_GROUP_ID,
                INTREF_GROUP_ID,
                "service-1",
                "service-2",
                "service-associe-1",
                "service-associe-2",
            ],
        )


def test_suite():
    from unittest import TestSuite, makeSuite

    suite = TestSuite()
    suite.addTest(makeSuite(testContacts, prefix="test_"))
    return suite
