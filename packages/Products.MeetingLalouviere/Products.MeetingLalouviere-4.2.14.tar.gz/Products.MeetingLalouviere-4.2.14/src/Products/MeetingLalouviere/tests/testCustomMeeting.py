# -*- coding: utf-8 -*-

from Products.MeetingCommunes.tests.testCustomMeeting import testCustomMeetingType as mctcm
from Products.MeetingLalouviere.tests.MeetingLalouviereTestCase import MeetingLalouviereTestCase


class testCustomMeetingType(mctcm, MeetingLalouviereTestCase):
    """
    Tests the Meeting adapted methods
    """


def test_suite():
    from unittest import TestSuite, makeSuite

    suite = TestSuite()
    suite.addTest(makeSuite(testCustomMeetingType, prefix="test_"))
    return suite
