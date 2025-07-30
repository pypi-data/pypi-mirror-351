# Copyright 2025 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0

from uw_person_client.tests import ModelTest
from uw_person_client.models import Adviser, Employee
from uw_person_client.exceptions import AdviserNotFoundException


class AdviserTest(ModelTest):
    def test_get_adviser_by_uwnetid(self):
        self.assertRaises(AdviserNotFoundException,
                          Adviser.objects.get_adviser_by_uwnetid,
                          'nobody')
        self.assertRaises(AdviserNotFoundException,
                          Adviser.objects.get_adviser_by_uwnetid,
                          'javerage')

        a = Adviser.objects.get_adviser_by_uwnetid('jadviser')
        self.assertEqual(a.advising_email, 'jadviser@uw.edu')

    def test_get_adviser_by_prior_uwnetid(self):
        a = Adviser.objects.get_adviser_by_uwnetid('jadviser1')
        self.assertEqual(a.advising_email, 'jadviser@uw.edu')

    def test_adviser_to_dict(self):
        a = Adviser.objects.get_adviser_by_uwnetid('jadviser')
        data = a.to_dict()
        self.assertEqual(data['advising_program'], 'OMAD Advising')
        self.assertEqual(data['employee']['employee_number'], '200000000')
        self.assertEqual(data['employee']['person']['first_name'], 'Jay')
