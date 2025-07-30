# Copyright 2025 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0

from django.test import TestCase
from uw_person_client.tests import ModelTest
from uw_person_client.models import (
    PersonQueue, EnrolledStudentQueue, InvalidNetID, InvalidStudentSystemKey)


class PersonQueueTest(TestCase):
    def test_add_to_queue(self):
        self.assertTrue(PersonQueue.objects.add_to_queue('jadviser'))
        self.assertTrue(PersonQueue.objects.add_to_queue('nobody'))
        self.assertRaises(
            InvalidNetID, PersonQueue.objects.add_to_queue, '1javerage')


class EnrolledStudentQueueTest(TestCase):
    def test_add_to_queue(self):
        self.assertTrue(EnrolledStudentQueue.objects.add_to_queue('123456789'))
        self.assertRaises(
            InvalidStudentSystemKey, EnrolledStudentQueue.objects.add_to_queue,
            '12345678')
