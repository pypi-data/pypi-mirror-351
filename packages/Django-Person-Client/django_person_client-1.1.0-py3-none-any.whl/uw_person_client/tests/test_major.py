# Copyright 2025 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0

from uw_person_client.tests import ModelTest
from uw_person_client.models import Person, Major


class MajorTest(ModelTest):
    def test_get_set_majors(self):
        p = Person.objects.get_person_by_uwnetid(
            'javerage', include_student=True)
        self.assertEqual(len(p.student.majors), 2)

        p.student.majors.append(Major())
        self.assertEqual(len(p.student.majors), 3)

        new_majors = [Major(), Major(), Major()]
        p.student.majors = new_majors
        self.assertEqual(len(p.student.majors), 3)

    def test_get_set_pending_majors(self):
        p = Person.objects.get_person_by_uwnetid(
            'javerage', include_student=True)
        self.assertEqual(len(p.student.pending_majors), 0)

        p.student.pending_majors.append(Major())
        self.assertEqual(len(p.student.pending_majors), 1)

        new_majors = [Major(), Major()]
        p.student.pending_majors = new_majors
        self.assertEqual(len(p.student.majors), 2)
