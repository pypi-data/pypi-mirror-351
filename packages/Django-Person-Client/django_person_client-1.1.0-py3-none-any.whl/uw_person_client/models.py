# Copyright 2025 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0

from django.db import models
from django.db.models import Q
from django.contrib.postgres.fields import ArrayField
from django.forms import model_to_dict
from uw_person_client.exceptions import (
    PersonNotFoundException, AdviserNotFoundException)
from uw_pws import PWS, InvalidNetID, InvalidStudentSystemKey


class PersonQueueManager(models.Manager):
    def add_to_queue(self, uwnetid):
        if PWS().valid_uwnetid(uwnetid):
            pq, _ = PersonQueue.objects.get_or_create(uwnetid=uwnetid)
            return True
        else:
            raise InvalidNetID(uwnetid)


class PersonQueue(models.Model):
    uwnetid = models.TextField(unique=True)

    class Meta:
        db_table = 'person_queue'
        managed = False

    objects = PersonQueueManager()


class EnrolledStudentQueueManager(models.Manager):
    def add_to_queue(self, system_key):
        if PWS().valid_student_system_key(system_key):
            esq, _ = EnrolledStudentQueue.objects.get_or_create(
                system_key=system_key)
            return True
        else:
            raise InvalidStudentSystemKey(system_key)


class EnrolledStudentQueue(models.Model):
    system_key = models.TextField(unique=True)

    class Meta:
        db_table = 'enrolled_student_queue'
        managed = False

    objects = EnrolledStudentQueueManager()


class PersonManager(models.Manager):
    def _include(self, **kwargs):
        related_fields = []
        if kwargs.get('include_employee'):
            related_fields.append('employee_set')
        if kwargs.get('include_student'):
            related_fields.append('student_set')
            if kwargs.get('include_student_transcripts'):
                related_fields.append('transcript_set')
            if kwargs.get('include_student_transfers'):
                related_fields.append('transfer_set')
            if kwargs.get('include_student_holds'):
                related_fields.append('studenthold_set')
            if kwargs.get('include_student_degrees'):
                related_fields.append('degree_set')
        return related_fields

    def _assemble(self, person, **kwargs):
        if kwargs.get('include_employee'):
            try:
                person.employee = person.employee_set.get()
            except Employee.DoesNotExist:
                pass

        if kwargs.get('include_student'):
            try:
                person.student = person.student_set.get()
            except Student.DoesNotExist:
                return person

            if kwargs.get('include_student_transcripts'):
                person.student.transcripts = person.student.transcript_set
            if kwargs.get('include_student_transfers'):
                person.student.transfers = person.student.transfer_set
            if kwargs.get('include_student_holds'):
                person.student.holds = person.student.studenthold_set
            if kwargs.get('include_student_degrees'):
                person.student.degrees = person.student.degree_set

        return person

    def _get_person(self, queryset, **kwargs):
        related_fields = self._include(**kwargs)

        if len(related_fields):
            queryset.prefetch_related(*related_fields)

        return self._assemble(queryset.get(), **kwargs)

    def get_person_by_uwnetid(self, uwnetid, **kwargs):
        queryset = super().get_queryset().filter(
            Q(uwnetid=uwnetid) | Q(prior_uwnetids__contains=[uwnetid]))

        try:
            return self._get_person(queryset, **kwargs)
        except Person.DoesNotExist:
            raise PersonNotFoundException(uwnetid)

    def get_person_by_uwregid(self, uwregid, **kwargs):
        queryset = super().get_queryset().filter(
            Q(uwregid=uwregid) | Q(prior_uwregids__contains=[uwregid]))

        try:
            return self._get_person(queryset, **kwargs)
        except Person.DoesNotExist:
            raise PersonNotFoundException(uwregid)

    def get_person_by_system_key(self, system_key, **kwargs):
        queryset = super().get_queryset().filter(system_key=system_key)

        try:
            return self._get_person(queryset, **kwargs)
        except Person.DoesNotExist:
            raise PersonNotFoundException(system_key)

    def get_person_by_student_number(self, student_number, **kwargs):
        queryset = super().get_queryset().filter(
            student__student_number=student_number)

        try:
            return self._get_person(queryset, **kwargs)
        except Person.DoesNotExist:
            raise PersonNotFoundException(student_number)

    def get_active_students(self, **kwargs):
        queryset = super().get_queryset().filter(is_active_student=True)

        related_fields = self._include(**kwargs)
        if len(related_fields):
            queryset.prefetch_related(*related_fields)

        persons = []
        for person in queryset:
            persons.append(self._assemble(person, **kwargs))
        return persons

    def get_active_employees(self, **kwargs):
        queryset = super().get_queryset().filter(is_active_employee=True)

        related_fields = self._include(**kwargs)
        if len(related_fields):
            queryset.prefetch_related(*related_fields)

        persons = []
        for person in queryset:
            persons.append(self._assemble(person, **kwargs))
        return persons


class Person(models.Model):
    uwnetid = models.TextField(unique=True, blank=True, null=True)
    uwregid = models.TextField(unique=True, blank=True, null=True)
    pronouns = models.TextField(blank=True, null=True)
    full_name = models.TextField(blank=True, null=True)
    display_name = models.TextField(blank=True, null=True)
    first_name = models.TextField(blank=True, null=True)
    surname = models.TextField(blank=True, null=True)
    preferred_first_name = models.TextField(blank=True, null=True)
    preferred_middle_name = models.TextField(blank=True, null=True)
    preferred_surname = models.TextField(blank=True, null=True)
    whitepages_publish = models.BooleanField(blank=True, null=True)
    is_active_student = models.BooleanField(
        db_column='_is_active_student', blank=True, null=True)
    is_active_employee = models.BooleanField(
        db_column='_is_active_employee', blank=True, null=True)
    last_changed = models.DateTimeField(
        db_column='_last_changed', blank=True, null=True)
    system_key = models.TextField(blank=True, null=True)
    prior_uwnetids = ArrayField(models.CharField(max_length=24))
    prior_uwregids = ArrayField(models.CharField(max_length=32))

    objects = PersonManager()

    class Meta:
        db_table = 'person'
        managed = False

    @property
    def employee(self):
        try:
            return self._employee
        except AttributeError:
            pass

    @employee.setter
    def employee(self, value):
        self._employee = value

    @property
    def student(self):
        try:
            return self._student
        except AttributeError:
            pass

    @student.setter
    def student(self, value):
        self._student = value

    def to_dict(self):
        data = model_to_dict(self)
        if self.employee is not None:
            data['employee'] = self.employee.to_dict()

        if self.student is not None:
            data['student'] = self.student.to_dict()

        return data


class Employee(models.Model):
    person = models.ForeignKey(Person, models.DO_NOTHING)
    employee_number = models.TextField()
    employee_affiliation_state = models.TextField(blank=True, null=True)
    email_addresses = ArrayField(models.CharField(max_length=100))
    home_department = models.TextField(blank=True, null=True)
    title = models.TextField(blank=True, null=True)
    department = models.TextField(blank=True, null=True)
    last_changed = models.DateTimeField(
        db_column='_last_changed', blank=True, null=True)

    class Meta:
        db_table = 'employee'
        managed = False

    def to_dict(self):
        data = model_to_dict(self)
        data['person'] = self.person.to_dict()
        return data


class AdviserManager(models.Manager):
    def get_adviser_by_uwnetid(self, uwnetid):
        queryset = super().get_queryset().filter(
            Q(employee__person__uwnetid=uwnetid) | Q(
                employee__person__prior_uwnetids__contains=[uwnetid]))
        try:
            return queryset.get()
        except Adviser.DoesNotExist:
            raise AdviserNotFoundException(uwnetid)


class Adviser(models.Model):
    employee = models.ForeignKey(Employee, models.DO_NOTHING)
    is_dept_adviser = models.BooleanField(blank=True, null=True)
    advising_email = models.TextField(blank=True, null=True)
    advising_phone_number = models.TextField(blank=True, null=True)
    advising_program = models.TextField(blank=True, null=True)
    advising_pronouns = models.TextField(blank=True, null=True)
    booking_url = models.TextField(blank=True, null=True)
    last_changed = models.DateTimeField(
        db_column='_last_changed', blank=True, null=True)

    objects = AdviserManager()

    class Meta:
        db_table = 'adviser'
        managed = False

    def to_dict(self):
        data = model_to_dict(self)
        data['employee'] = self.employee.to_dict()
        return data


class Term(models.Model):
    year = models.SmallIntegerField()
    quarter = models.SmallIntegerField()

    class Meta:
        db_table = 'term'
        managed = False
        unique_together = (('year', 'quarter'),)

    def to_dict(self):
        return model_to_dict(self)


class Major(models.Model):
    major_abbr_code = models.TextField(blank=True, null=True)
    major_full_name = models.TextField(blank=True, null=True)
    major_name = models.TextField(blank=True, null=True)
    major_short_name = models.TextField(blank=True, null=True)
    major_branch = models.SmallIntegerField(blank=True, null=True)
    major_cip_code = models.IntegerField(blank=True, null=True)
    major_concur_cc = models.BooleanField(blank=True, null=True)
    major_dept = models.TextField(blank=True, null=True)
    major_desc = models.TextField(blank=True, null=True)
    major_dist_learn = models.BooleanField(blank=True, null=True)
    major_evening = models.BooleanField(blank=True, null=True)
    major_first_qtr = models.SmallIntegerField(blank=True, null=True)
    major_first_yr = models.SmallIntegerField(blank=True, null=True)
    major_gnm = models.BooleanField(blank=True, null=True)
    major_grad_certif = models.BooleanField(blank=True, null=True)
    major_graduate = models.BooleanField(blank=True, null=True)
    major_home_url = models.TextField(blank=True, null=True)
    major_last_qtr = models.SmallIntegerField(blank=True, null=True)
    major_last_yr = models.SmallIntegerField(blank=True, null=True)
    major_measles_ex = models.BooleanField(blank=True, null=True)
    major_minor = models.BooleanField(blank=True, null=True)
    major_non_degree = models.BooleanField(blank=True, null=True)
    major_nonmatric = models.BooleanField(blank=True, null=True)
    major_not_termin = models.BooleanField(blank=True, null=True)
    major_osfa_inelig = models.BooleanField(blank=True, null=True)
    major_pathway = models.SmallIntegerField(blank=True, null=True)
    major_premaj = models.BooleanField(blank=True, null=True)
    major_premaj_ext = models.BooleanField(blank=True, null=True)
    major_professional = models.BooleanField(blank=True, null=True)
    major_ss_inelig = models.BooleanField(blank=True, null=True)
    major_ss_std_act = models.BooleanField(blank=True, null=True)
    major_ug_certif = models.BooleanField(blank=True, null=True)
    major_undergrad = models.BooleanField(blank=True, null=True)
    college = models.TextField(blank=True, null=True)
    major_branch_name = models.TextField(blank=True, null=True)
    major_college_name = models.TextField(blank=True, null=True)

    class Meta:
        db_table = 'major'
        managed = False

    def to_dict(self):
        return model_to_dict(self)


class Sport(models.Model):
    sport_code = models.TextField(blank=True, null=True)
    short_sport_name = models.TextField(blank=True, null=True)
    sport_descrip = models.TextField(blank=True, null=True)
    sport_reg_pr_aut = models.BooleanField(blank=True, null=True)
    sport_reg_pr_spr = models.BooleanField(blank=True, null=True)
    sport_reg_pr_sum = models.BooleanField(blank=True, null=True)
    sport_reg_pr_win = models.BooleanField(blank=True, null=True)

    class Meta:
        db_table = 'sport'
        managed = False

    def to_dict(self):
        return model_to_dict(self)


class Student(models.Model):
    person = models.ForeignKey(Person, models.DO_NOTHING)
    academic_term = models.ForeignKey(
        Term, models.DO_NOTHING, blank=True, null=True)
    advisers = models.ManyToManyField(Adviser, through='StudentToAdviser')
    sports = models.ManyToManyField(Sport, through='StudentToSport')
    system_key = models.TextField(unique=True)
    student_number = models.TextField(blank=True, null=True)
    birthdate = models.DateField(blank=True, null=True)
    student_email = models.TextField(blank=True, null=True)
    external_email = models.TextField(blank=True, null=True)
    local_phone_number = models.TextField(blank=True, null=True)
    gender = models.TextField(blank=True, null=True)
    cumulative_gpa = models.TextField(blank=True, null=True)
    campus_code = models.SmallIntegerField(blank=True, null=True)
    campus_desc = models.TextField(blank=True, null=True)
    perm_addr_line1 = models.TextField(blank=True, null=True)
    perm_addr_line2 = models.TextField(blank=True, null=True)
    perm_addr_city = models.TextField(blank=True, null=True)
    perm_addr_state = models.TextField(blank=True, null=True)
    perm_addr_5digit_zip = models.TextField(blank=True, null=True)
    perm_addr_4digit_zip = models.TextField(blank=True, null=True)
    perm_addr_postal_code = models.TextField(blank=True, null=True)
    perm_addr_country = models.TextField(blank=True, null=True)
    perm_phone_number = models.TextField(blank=True, null=True)
    last_changed = models.DateTimeField(
        db_column='_last_changed', blank=True, null=True)
    class_code = models.SmallIntegerField(blank=True, null=True)
    class_desc = models.TextField(blank=True, null=True)
    registered_in_quarter = models.BooleanField(blank=True, null=True)
    resident_code = models.SmallIntegerField(blank=True, null=True)
    resident_desc = models.TextField(blank=True, null=True)
    total_credits = models.TextField(blank=True, null=True)
    total_deductible_credits = models.TextField(blank=True, null=True)
    total_extension_credits = models.TextField(blank=True, null=True)
    total_grade_attempted = models.TextField(blank=True, null=True)
    total_grade_points = models.TextField(blank=True, null=True)
    total_lower_div_transfer_credits = models.TextField(blank=True, null=True)
    total_non_graded_credits = models.TextField(blank=True, null=True)
    total_registered_credits = models.TextField(blank=True, null=True)
    total_transfer_credits = models.TextField(blank=True, null=True)
    total_uw_credits = models.TextField(blank=True, null=True)
    total_upper_div_transfer_credits = models.TextField(blank=True, null=True)
    veteran_benefit_code = models.SmallIntegerField(blank=True, null=True)
    veteran_benefit_desc = models.TextField(blank=True, null=True)
    veteran_desc = models.TextField(blank=True, null=True)
    admitted_for_yr_qtr_desc = models.TextField(blank=True, null=True)
    admitted_for_yr_qtr_id = models.TextField(blank=True, null=True)
    application_status_code = models.SmallIntegerField(blank=True, null=True)
    application_status_desc = models.TextField(blank=True, null=True)
    application_type_code = models.TextField(blank=True, null=True)
    application_type_desc = models.TextField(blank=True, null=True)
    applied_to_graduate_yr_qtr_desc = models.TextField(blank=True, null=True)
    applied_to_graduate_yr_qtr_id = models.TextField(blank=True, null=True)
    asuwind = models.BooleanField(blank=True, null=True)
    directory_release_ind = models.BooleanField(blank=True, null=True)
    disability_ind = models.BooleanField(blank=True, null=True)
    enroll_status_code = models.SmallIntegerField(blank=True, null=True)
    exemption_code = models.SmallIntegerField(blank=True, null=True)
    exemption_desc = models.TextField(blank=True, null=True)
    first_generation_4yr_ind = models.BooleanField(blank=True, null=True)
    first_generation_ind = models.BooleanField(blank=True, null=True)
    high_school_gpa = models.TextField(blank=True, null=True)
    high_school_graduation_date = models.TextField(blank=True, null=True)
    honors_program_code = models.TextField(blank=True, null=True)
    honors_program_ind = models.BooleanField(blank=True, null=True)
    jr_col_gpa = models.TextField(blank=True, null=True)
    last_enrolled_yr_qtr_desc = models.TextField(blank=True, null=True)
    last_enrolled_yr_qtr_id = models.TextField(blank=True, null=True)
    local_addr_4digit_zip = models.TextField(blank=True, null=True)
    local_addr_5digit_zip = models.TextField(blank=True, null=True)
    local_addr_city = models.TextField(blank=True, null=True)
    local_addr_country = models.TextField(blank=True, null=True)
    local_addr_line1 = models.TextField(blank=True, null=True)
    local_addr_line2 = models.TextField(blank=True, null=True)
    local_addr_postal_code = models.TextField(blank=True, null=True)
    local_addr_state = models.TextField(blank=True, null=True)
    new_continuing_returning_code = models.SmallIntegerField(
        blank=True, null=True)
    new_continuing_returning_desc = models.TextField(blank=True, null=True)
    previous_institution_name = models.TextField(blank=True, null=True)
    previous_institution_type = models.TextField(blank=True, null=True)
    previous_institution_type_desc = models.TextField(blank=True, null=True)
    record_load_dttm = models.TextField(blank=True, null=True)
    record_update_dttm = models.TextField(blank=True, null=True)
    reg_first_yr_qtr_desc = models.TextField(blank=True, null=True)
    reg_first_yr_qtr_id = models.TextField(blank=True, null=True)
    registration_hold_ind = models.BooleanField(blank=True, null=True)
    special_program_code = models.TextField(blank=True, null=True)
    special_program_desc = models.TextField(blank=True, null=True)
    sr_col_gpa = models.TextField(blank=True, null=True)
    birth_city = models.TextField(blank=True, null=True)
    birth_country = models.TextField(blank=True, null=True)
    birth_state = models.TextField(blank=True, null=True)
    child_of_alumni = models.BooleanField(blank=True, null=True)
    citizen_country = models.TextField(blank=True, null=True)
    emergency_email = models.TextField(blank=True, null=True)
    emergency_name = models.TextField(blank=True, null=True)
    emergency_phone = models.TextField(blank=True, null=True)
    iss_perm_resident_country = models.TextField(blank=True, null=True)
    parent_name = models.TextField(blank=True, null=True)
    parent_phone_number = models.TextField(blank=True, null=True)
    parent_addr_line1 = models.TextField(blank=True, null=True)
    parent_addr_line2 = models.TextField(blank=True, null=True)
    parent_addr_city = models.TextField(blank=True, null=True)
    parent_addr_state = models.TextField(blank=True, null=True)
    parent_addr_5digit_zip = models.TextField(blank=True, null=True)
    parent_addr_4digit_zip = models.TextField(blank=True, null=True)
    parent_addr_postal_code = models.TextField(blank=True, null=True)
    parent_addr_country = models.TextField(blank=True, null=True)
    visa_type = models.TextField(blank=True, null=True)
    intended_major1_code = models.TextField(blank=True, null=True)
    intended_major2_code = models.TextField(blank=True, null=True)
    intended_major3_code = models.TextField(blank=True, null=True)
    requested_major1_code = models.TextField(blank=True, null=True)
    requested_major2_code = models.TextField(blank=True, null=True)
    requested_major3_code = models.TextField(blank=True, null=True)
    major_1 = models.ForeignKey(
        Major, models.DO_NOTHING, related_name='student_major_1_set',
        blank=True, null=True)
    major_2 = models.ForeignKey(
        Major, models.DO_NOTHING, related_name='student_major_2_set',
        blank=True, null=True)
    major_3 = models.ForeignKey(
        Major, models.DO_NOTHING, related_name='student_major_3_set',
        blank=True, null=True)
    pending_major_1 = models.ForeignKey(
        Major, models.DO_NOTHING, related_name='student_pending_major_1_set',
        blank=True, null=True)
    pending_major_2 = models.ForeignKey(
        Major, models.DO_NOTHING, related_name='student_pending_major_2_set',
        blank=True, null=True)
    pending_major_3 = models.ForeignKey(
        Major, models.DO_NOTHING, related_name='student_pending_major_3_set',
        blank=True, null=True)
    enroll_status_request_code = models.TextField(blank=True, null=True)
    enroll_status_desc = models.TextField(blank=True, null=True)
    spp_qtrs_allowed = models.SmallIntegerField(blank=True, null=True)
    spp_qtrs_used = models.SmallIntegerField(blank=True, null=True)
    spp_qtrs_used_dt = models.DateTimeField(blank=True, null=True)
    spp_status = models.SmallIntegerField(blank=True, null=True)
    spp_status_dt = models.DateTimeField(blank=True, null=True)
    spp_category = models.SmallIntegerField(blank=True, null=True)
    spp_category_dt = models.DateTimeField(blank=True, null=True)
    ethnic_code = models.TextField(blank=True, null=True)
    ethnic_desc = models.TextField(blank=True, null=True)
    ethnic_long_desc = models.TextField(blank=True, null=True)
    ethnic_group_code = models.TextField(blank=True, null=True)
    hispanic_code = models.TextField(blank=True, null=True)
    hispanic_desc = models.TextField(blank=True, null=True)
    hispanic_long_desc = models.TextField(blank=True, null=True)
    hispanic_group_code = models.TextField(blank=True, null=True)
    deceased_date = models.DateField(blank=True, null=True)
    ethnic_group_desc = models.TextField(blank=True, null=True)
    hispanic_group_desc = models.TextField(blank=True, null=True)
    ethnic_under_rep = models.BooleanField(blank=True, null=True)
    hispanic_under_rep = models.BooleanField(blank=True, null=True)

    class Meta:
        db_table = 'student'
        managed = False

    @property
    def majors(self):
        try:
            return self._majors
        except AttributeError:
            self._majors = []
            if self.major_1:
                self._majors.append(self.major_1)
            if self.major_2:
                self._majors.append(self.major_2)
            if self.major_3:
                self._majors.append(self.major_3)
            return self._majors

    @majors.setter
    def majors(self, value):
        self._majors = value

    @property
    def pending_majors(self):
        try:
            return self._pending_majors
        except AttributeError:
            self._pending_majors = []
            if self.pending_major_1:
                self._pending_majors.append(self.pending_major_1)
            if self.pending_major_2:
                self._pending_majors.append(self.pending_major_2)
            if self.pending_major_3:
                self._pending_majors.append(self.pending_major_3)
            return self._pending_majors

    @pending_majors.setter
    def pending_majors(self, value):
        self._pending_majors = value

    @property
    def requested_majors(self):
        try:
            return self._requested_majors
        except AttributeError:
            self._requested_majors = []
            if self.requested_major1_code:
                self._requested_majors.append(self.requested_major1_code)
            if self.requested_major2_code:
                self._requested_majors.append(self.requested_major2_code)
            if self.requested_major3_code:
                self._requested_majors.append(self.requested_major3_code)
            return self._requested_majors

    @requested_majors.setter
    def requested_majors(self, value):
        self._requested_majors = value

    @property
    def intended_majors(self):
        try:
            return self._intended_majors
        except AttributeError:
            self._intended_majors = []
            if self.intended_major1_code:
                self._intended_majors.append(self.intended_major1_code)
            if self.intended_major2_code:
                self._intended_majors.append(self.intended_major2_code)
            if self.intended_major3_code:
                self._intended_majors.append(self.intended_major3_code)
            return self._intended_majors

    @intended_majors.setter
    def intended_majors(self, value):
        self._intended_majors = value

    @property
    def transcripts(self):
        try:
            return self._transcripts
        except AttributeError:
            pass

    @transcripts.setter
    def transcripts(self, value):
        self._transcripts = value

    @property
    def transfers(self):
        try:
            return self._transfers
        except AttributeError:
            pass

    @transfers.setter
    def transfers(self, value):
        self._transfers = value

    @property
    def holds(self):
        try:
            return self._holds
        except AttributeError:
            pass

    @holds.setter
    def holds(self, value):
        self._holds = value

    @property
    def degrees(self):
        try:
            return self._degrees
        except AttributeError:
            pass

    @degrees.setter
    def degrees(self, value):
        self._degrees = value

    def to_dict(self):
        data = model_to_dict(self)
        data['academic_term'] = self.academic_term.to_dict()
        data['majors'] = [m.to_dict() for m in self.majors]
        data['pending_majors'] = [m.to_dict() for m in self.pending_majors]
        data['requested_majors'] = self.requested_majors
        data['intended_majors'] = self.intended_majors

        if self.advisers is not None:
            data['advisers'] = [a.to_dict() for a in self.advisers.all()]

        if self.sports is not None:
            data['sports'] = [s.to_dict() for s in self.sports.all()]

        if self.transcripts is not None:
            data['transcripts'] = [t.to_dict() for t in self.transcripts.all()]

        if self.transfers is not None:
            data['transfers'] = [t.to_dict() for t in self.transfers.all()]

        if self.holds is not None:
            data['holds'] = [h.to_dict() for h in self.holds.all()]

        if self.degrees is not None:
            data['degrees'] = [d.to_dict() for d in self.degrees.all()]

        return data


class StudentHold(models.Model):
    student = models.ForeignKey(Student, models.DO_NOTHING)
    seq = models.SmallIntegerField()
    hold_dt = models.DateTimeField(blank=True, null=True)
    hold_office = models.TextField(blank=True, null=True)
    hold_office_desc = models.TextField(blank=True, null=True)
    hold_reason = models.TextField(blank=True, null=True)
    hold_type = models.SmallIntegerField(blank=True, null=True)
    hold_type_desc = models.TextField(blank=True, null=True)

    class Meta:
        db_table = 'student_hold'
        managed = False
        unique_together = (('student', 'seq'),)
        ordering = ['seq']

    def to_dict(self):
        return model_to_dict(self)


class StudentToAdviser(models.Model):
    student = models.ForeignKey(Student, models.DO_NOTHING)
    adviser = models.ForeignKey(Adviser, models.DO_NOTHING)

    class Meta:
        db_table = 'student_to_adviser'
        managed = False
        unique_together = (('student', 'adviser'),)


class StudentToSport(models.Model):
    student = models.ForeignKey(Student, models.DO_NOTHING)
    sport = models.ForeignKey(Sport, models.DO_NOTHING)

    class Meta:
        db_table = 'student_to_sport'
        managed = False
        unique_together = (('student', 'sport'),)


class Degree(models.Model):
    student = models.ForeignKey(Student, models.DO_NOTHING)
    degree_term = models.ForeignKey(
        Term, models.DO_NOTHING, blank=True, null=True)
    campus_code = models.SmallIntegerField(blank=True, null=True)
    degree_abbr_code = models.TextField(blank=True, null=True)
    degree_pathway_num = models.SmallIntegerField(blank=True, null=True)
    degree_level_code = models.TextField(blank=True, null=True)
    degree_level_desc = models.TextField(blank=True, null=True)
    degree_type_code = models.TextField(blank=True, null=True)
    degree_level_type_desc = models.TextField(blank=True, null=True)
    degree_desc = models.TextField(blank=True, null=True)
    degree_uw_credits = models.DecimalField(
        max_digits=6, decimal_places=2, blank=True, null=True)
    degree_transfer_credits = models.DecimalField(
        max_digits=6, decimal_places=2, blank=True, null=True)
    degree_extension_credits = models.DecimalField(
        max_digits=6, decimal_places=2, blank=True, null=True)
    degree_gpa = models.TextField(blank=True, null=True)
    fin_org_key = models.TextField(blank=True, null=True)
    primary_fin_org_key = models.TextField(blank=True, null=True)
    degree_college_code = models.TextField(blank=True, null=True)
    degree_status_code = models.TextField(blank=True, null=True)
    degree_status_desc = models.TextField(blank=True, null=True)
    degree_date = models.DateField(blank=True, null=True)
    degree_grad_honor = models.SmallIntegerField(blank=True, null=True)
    degree_index = models.SmallIntegerField(blank=True, null=True)
    degree_major_index = models.SmallIntegerField(blank=True, null=True)
    campus_name = models.TextField(blank=True, null=True)
    degree_college_name = models.TextField(blank=True, null=True)
    degree_grad_honor_desc = models.TextField(blank=True, null=True)

    class Meta:
        db_table = 'degree'
        managed = False
        unique_together = ((
            'student', 'degree_term', 'campus_code', 'degree_abbr_code',
            'degree_pathway_num'),)

    def to_dict(self):
        data = model_to_dict(self)
        if self.degree_term is not None:
            data['degree_term'] = self.degree_term.to_dict()
        return data


class Transcript(models.Model):
    student = models.ForeignKey(Student, models.DO_NOTHING)
    tran_term = models.ForeignKey(
        Term, models.DO_NOTHING, blank=True, null=True)
    leave_ends_term = models.ForeignKey(
        Term, models.DO_NOTHING, related_name='transcript_leave_ends_term_set',
        blank=True, null=True)
    veteran = models.SmallIntegerField(blank=True, null=True)
    veteran_benefit = models.SmallIntegerField(blank=True, null=True)
    resident = models.SmallIntegerField(blank=True, null=True)
    resident_cat = models.TextField(blank=True, null=True)
    qtr_grade_points = models.DecimalField(
        max_digits=5, decimal_places=2, blank=True, null=True)
    qtr_graded_attmp = models.DecimalField(
        max_digits=3, decimal_places=1, blank=True, null=True)
    qtr_nongrd_attmp = models.DecimalField(
        max_digits=3, decimal_places=1, blank=True, null=True)
    class_code = models.SmallIntegerField(blank=True, null=True)
    honors_program = models.SmallIntegerField(blank=True, null=True)
    special_program = models.SmallIntegerField(blank=True, null=True)
    scholarship_type = models.SmallIntegerField(blank=True, null=True)
    yearly_honor_type = models.SmallIntegerField(blank=True, null=True)
    exemption_code = models.SmallIntegerField(blank=True, null=True)
    num_ind_study = models.SmallIntegerField(blank=True, null=True)
    num_courses = models.SmallIntegerField(blank=True, null=True)
    enroll_status = models.SmallIntegerField(blank=True, null=True)
    tenth_day_credits = models.DecimalField(
        max_digits=3, decimal_places=1, blank=True, null=True)
    tr_en_stat_dt = models.DateTimeField(blank=True, null=True)
    last_changed = models.DateTimeField(
        db_column='_last_changed', blank=True, null=True)
    over_qtr_deduct = models.DecimalField(
        max_digits=3, decimal_places=1, blank=True, null=True)
    over_qtr_grade_at = models.DecimalField(
        max_digits=3, decimal_places=1, blank=True, null=True)
    over_qtr_grade_pt = models.DecimalField(
        max_digits=5, decimal_places=2, blank=True, null=True)
    over_qtr_nongrd = models.DecimalField(
        max_digits=3, decimal_places=1, blank=True, null=True)
    qtr_comment = models.TextField(blank=True, null=True)
    qtr_deductible = models.DecimalField(
        max_digits=3, decimal_places=1, blank=True, null=True)
    qtr_nongrd_earned = models.DecimalField(
        max_digits=3, decimal_places=1, blank=True, null=True)
    add_to_cum = models.BooleanField(blank=True, null=True)
    scholarship_abbr = models.TextField(blank=True, null=True)
    scholarship_desc = models.TextField(blank=True, null=True)
    enroll_status_request_code = models.TextField(blank=True, null=True)
    enroll_status_desc = models.TextField(blank=True, null=True)
    special_program_desc = models.TextField(blank=True, null=True)
    cmp_qtr_deductible_credits = models.DecimalField(
        max_digits=3, decimal_places=1, blank=True, null=True)
    cmp_qtr_grade_points = models.DecimalField(
        max_digits=5, decimal_places=2, blank=True, null=True)
    cmp_qtr_graded_attempted = models.DecimalField(
        max_digits=3, decimal_places=1, blank=True, null=True)
    cmp_qtr_nongraded_earned = models.DecimalField(
        max_digits=3, decimal_places=1, blank=True, null=True)
    cmp_qtr_total_attempted = models.DecimalField(
        max_digits=3, decimal_places=1, blank=True, null=True)
    cmp_qtr_total_earned = models.DecimalField(
        max_digits=3, decimal_places=1, blank=True, null=True)
    cmp_qtr_gpa = models.TextField(blank=True, null=True)
    cmp_cum_total_attempted = models.DecimalField(
        max_digits=3, decimal_places=1, blank=True, null=True)
    cmp_cum_graded_attempted = models.DecimalField(
        max_digits=3, decimal_places=1, blank=True, null=True)
    cmp_cum_grade_points = models.DecimalField(
        max_digits=5, decimal_places=2, blank=True, null=True)
    cmp_cum_gpa = models.TextField(blank=True, null=True)
    cmp_cum_uw_earned = models.DecimalField(
        max_digits=3, decimal_places=1, blank=True, null=True)
    cmp_cum_total_earned = models.DecimalField(
        max_digits=3, decimal_places=1, blank=True, null=True)

    class Meta:
        db_table = 'transcript'
        managed = False
        ordering = ['-tran_term__year', '-tran_term__quarter']

    def to_dict(self):
        data = model_to_dict(self)
        if self.tran_term is not None:
            data['tran_term'] = self.tran_term.to_dict()
        if self.leave_ends_term is not None:
            data['leave_ends_term'] = self.leave_ends_term.to_dict()
        return data


class Transfer(models.Model):
    student = models.ForeignKey(Student, models.DO_NOTHING)
    institution_code = models.TextField(blank=True, null=True)
    year_ending = models.SmallIntegerField(blank=True, null=True)
    year_beginning = models.SmallIntegerField(blank=True, null=True)
    transfer_gpa = models.DecimalField(
        max_digits=3, decimal_places=2, blank=True, null=True)
    trans_updt_dt = models.DateTimeField(blank=True, null=True)
    trans_updt_id = models.TextField(blank=True, null=True)
    degree_earned = models.TextField(blank=True, null=True)
    degree_earned_yr = models.SmallIntegerField(blank=True, null=True)
    degree_earned_mo = models.SmallIntegerField(blank=True, null=True)
    credential_lvl = models.SmallIntegerField(blank=True, null=True)
    credential_yr = models.SmallIntegerField(blank=True, null=True)
    transfer_comment = models.TextField(blank=True, null=True)
    institution_name = models.TextField(blank=True, null=True)
    inst_addr_line_1 = models.TextField(blank=True, null=True)
    inst_addr_line_2 = models.TextField(blank=True, null=True)
    inst_city = models.TextField(blank=True, null=True)
    inst_state = models.TextField(blank=True, null=True)
    inst_zip_5 = models.TextField(blank=True, null=True)
    inst_zip_filler = models.TextField(blank=True, null=True)
    inst_country = models.TextField(blank=True, null=True)
    inst_postal_cd = models.TextField(blank=True, null=True)
    inst_record_stat = models.BooleanField(blank=True, null=True)
    two_year = models.BooleanField(blank=True, null=True)
    wa_cc = models.BooleanField(blank=True, null=True)

    class Meta:
        db_table = 'transfer'
        managed = False

    def to_dict(self):
        return model_to_dict(self)
