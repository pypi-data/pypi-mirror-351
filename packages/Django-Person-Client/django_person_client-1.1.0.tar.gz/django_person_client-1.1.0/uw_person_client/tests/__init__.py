# Copyright 2025 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0

from django.test import TestCase


class ModelTest(TestCase):
    fixtures = ['person.json', 'employee.json', 'term.json', 'major.json',
                'student.json', 'adviser.json', 'transfer.json',
                'transcript.json', 'hold.json', 'degree.json', 'sport.json']
