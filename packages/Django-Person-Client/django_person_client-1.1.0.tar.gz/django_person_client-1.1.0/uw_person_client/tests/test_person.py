# Copyright 2025 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0

from uw_person_client.tests import ModelTest
from uw_person_client.models import Person
from uw_person_client.exceptions import PersonNotFoundException


class PersonTest(ModelTest):
    def test_get_person_by_prior_uwnetid(self):
        p = Person.objects.get_person_by_uwnetid('jadviser1')
        self.assertEqual(p.uwnetid, 'jadviser')

    def test_get_person_by_uwnetid(self):
        self.assertRaises(PersonNotFoundException,
                          Person.objects.get_person_by_uwnetid, 'nobody')

        p = Person.objects.get_person_by_uwnetid('javerage')
        self.assertEqual(p.uwnetid, 'javerage')
        self.assertEqual(p.uwregid, '9136CCB8F66711D5BE060004AC494FFE')
        self.assertEqual(p.system_key, '532353230')
        self.assertEqual(p.employee, None)
        self.assertEqual(p.student, None)

        p = Person.objects.get_person_by_uwnetid(
            'bill', include_employee=True)
        self.assertEqual(p.uwnetid, 'bill')
        self.assertEqual(p.employee.employee_number, '100000000')
        self.assertEqual(p.employee.employee_affiliation_state, 'current')
        self.assertEqual(p.student, None)

    def test_get_basic_student_by_uwnetid(self):
        p = Person.objects.get_person_by_uwnetid(
            'jbothell', include_student=True)
        self.assertEqual(p.uwnetid, 'jbothell')
        self.assertEqual(p.employee, None)
        self.assertEqual(p.student.student_number, '1233334')
        self.assertEqual(p.student.academic_term.year, 2013)
        self.assertEqual(p.student.academic_term.quarter, 3)
        self.assertEqual(p.student.major_1.major_name, 'INTERNATIONAL STUDIES')
        self.assertEqual(p.student.major_2, None)
        self.assertEqual(p.student.major_3, None)
        self.assertEqual(len(p.student.majors), 1)
        self.assertEqual(len(p.student.pending_majors), 1)
        self.assertEqual(len(p.student.sports.all()), 1)
        self.assertEqual(p.student.sports.all()[0].short_sport_name, 'GLF')
        self.assertEqual(len(p.student.advisers.all()), 1)
        self.assertEqual(p.student.transcripts, None)
        self.assertEqual(p.student.transfers, None)
        self.assertEqual(p.student.holds, None)
        self.assertEqual(p.student.degrees, None)

    def test_get_student_includes_by_uwnetid(self):
        p = Person.objects.get_person_by_uwnetid(
            'javerage', include_student=True, include_student_transfers=True)
        self.assertEqual(p.uwnetid, 'javerage')
        self.assertEqual(len(p.student.transfers.all()), 1)

        p = Person.objects.get_person_by_uwnetid(
            'javerage', include_student=True, include_student_holds=True)
        self.assertEqual(p.uwnetid, 'javerage')
        self.assertEqual(len(p.student.holds.all()), 2)
        self.assertEqual(p.student.holds.all()[0].hold_office, 'UWEXT')

        p = Person.objects.get_person_by_uwnetid(
            'javerage', include_student=True, include_student_degrees=True)
        self.assertEqual(p.uwnetid, 'javerage')
        self.assertEqual(len(p.student.degrees.all()), 1)
        self.assertEqual(p.student.degrees.all()[0].degree_abbr_code, 'STAT')

    def test_get_person_by_prior_uwregid(self):
        p = Person.objects.get_person_by_uwregid(
            '9136CCB8F66711D5BE060004AC494FF0')
        self.assertEqual(p.uwnetid, 'javerage')
        self.assertEqual(p.uwregid, '9136CCB8F66711D5BE060004AC494FFE')

    def test_get_person_by_uwregid(self):
        self.assertRaises(PersonNotFoundException,
                          Person.objects.get_person_by_uwregid,
                          '11111B8F66711D5BE060004AC494FFE')

        p = Person.objects.get_person_by_uwregid(
            '9136CCB8F66711D5BE060004AC494FFE')
        self.assertEqual(p.uwnetid, 'javerage')
        self.assertEqual(p.uwregid, '9136CCB8F66711D5BE060004AC494FFE')
        self.assertEqual(p.system_key, '532353230')
        self.assertEqual(p.employee, None)
        self.assertEqual(p.student, None)

    def test_get_full_student_by_uwregid(self):
        p = Person.objects.get_person_by_uwregid(
            '9136CCB8F66711D5BE060004AC494FFE',
            include_student=True,
            include_student_transcripts=True,
            include_student_transfers=True,
            include_student_holds=True,
            include_student_degrees=True)
        self.assertEqual(len(p.student.transcripts.all()), 3)
        self.assertEqual(len(p.student.transfers.all()), 1)
        self.assertEqual(len(p.student.holds.all()), 2)
        self.assertEqual(len(p.student.degrees.all()), 1)

    def test_get_person_by_system_key(self):
        self.assertRaises(PersonNotFoundException,
                          Person.objects.get_person_by_system_key,
                          '010101010')

        p = Person.objects.get_person_by_system_key('532353230')
        self.assertEqual(p.uwnetid, 'javerage')
        self.assertEqual(p.uwregid, '9136CCB8F66711D5BE060004AC494FFE')
        self.assertEqual(p.system_key, '532353230')
        self.assertEqual(p.employee, None)
        self.assertEqual(p.student, None)

    def test_get_student_by_system_key(self):
        p = Person.objects.get_person_by_system_key(
            '532353230',
            include_student=True,
            include_student_transcripts=True)
        self.assertEqual(p.student.major_1.major_name, 'PRE SOCIAL SCIENCE')
        self.assertEqual(len(p.student.transcripts.all()), 3)

    def test_get_person_by_student_number(self):
        self.assertRaises(PersonNotFoundException,
                          Person.objects.get_person_by_student_number,
                          '1000000')

        p = Person.objects.get_person_by_student_number('1033334')
        self.assertEqual(p.uwnetid, 'javerage')
        self.assertEqual(p.uwregid, '9136CCB8F66711D5BE060004AC494FFE')
        self.assertEqual(p.uwnetid, 'javerage')
        self.assertEqual(p.employee, None)
        self.assertEqual(p.student, None)

    def test_get_student_includes_by_student_number(self):
        p = Person.objects.get_person_by_student_number(
            '1033334',
            include_student=True,
            include_student_transcripts=True,
            include_student_transfers=True,
            include_student_holds=True,
            include_student_degrees=True)

        self.assertEqual(p.student.student_number, '1033334')
        self.assertEqual(p.student.major_1.major_name, 'PRE SOCIAL SCIENCE')
        self.assertEqual(len(p.student.majors), 2)
        self.assertEqual(len(p.student.pending_majors), 0)
        self.assertEqual(len(p.student.transcripts.all()), 3)

        data = p.to_dict().get('student')

        self.assertEqual(len(data['majors']), 2)
        self.assertEqual(len(data['pending_majors']), 0)
        self.assertEqual(len(data['requested_majors']), 2)
        self.assertEqual(len(data['intended_majors']), 2)
        self.assertEqual(len(data['transcripts']), 3)
        self.assertEqual(len(data['transfers']), 1)
        self.assertEqual(len(data['holds']), 2)
        self.assertEqual(len(data['degrees']), 1)

    def test_person_to_dict(self):
        p1 = Person.objects.get_person_by_uwnetid('javerage')
        data1 = p1.to_dict()

        p2 = Person(**data1)
        self.assertEqual(data1, p2.to_dict())

    def test_get_active_employees(self):
        results = Person.objects.get_active_employees()
        self.assertEqual(len(results), 2)

        results = Person.objects.get_active_employees(include_employee=True)
        self.assertEqual(len(results), 2)
        self.assertEqual(results[1].employee.employee_number, '200000000')

    def test_get_active_students(self):
        results = Person.objects.get_active_students()
        self.assertEqual(len(results), 2)

        results = Person.objects.get_active_students(include_student=True)
        self.assertEqual(len(results), 2)
        self.assertEqual(results[1].student.student_number, '1233334')
