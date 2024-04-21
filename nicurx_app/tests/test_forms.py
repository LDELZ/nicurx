from django.test import TestCase
from django.urls import reverse
from nicurx_app.forms import MedicationForm, PatientForm, ProfileForm
from django.contrib.auth.models import User
import datetime
from nicurx_app.models import MedicationProfile

# Create your tests here.
class PatientFormTestCase(TestCase):

    # SETUP: Create a Medication Profile for testing - test

    def setUp(self):

        self.medication_profile=MedicationProfile.objects.create(
            title='Test profile',
            about='Test description',
            id_number=999999,
            is_active=True,
            issues=999
        )

    # VALID CASE: Test a completely valid form
    def test_valid_form(self):
        data = {
            'is_active': True,
            'first_name': 'John',
            'last_name': 'Doe',
            'id_number': 99999,
            'guardian_name': 'Jane Doe',
            'date_of_birth': '1990-05-20',
            'weight': 75,
            'height': 175,
            'medication_profile': self.medication_profile.id
        }
        form = PatientForm(data=data)
        self.assertTrue(form.is_valid())

    # INVALID CASE: Test an invalid form that is missing the first_name of the patient
    def test_missing_name_invalid(self):
        data = {
            'is_active': True,
            'first_name': '',
            'last_name': 'Doe',
            'id_number': 99999,
            'guardian_name': 'Jane Doe',
            'date_of_birth': '1990-05-20',
            'weight': 75,
            'height': 175,
            'medication_profile': self.medication_profile.id
        }
        form = PatientForm(data=data)
        self.assertFalse(form.is_valid()) and self.assertIn('first_name', form.errors)

    # VALID_CASE: Test saving a form - I included this because I've been having issues getting forms to process save commands
    def test_form_save(self):
        data = {
            'is_active': True,
            'first_name': 'Jane',
            'last_name': 'Doe',
            'id_number': 444,
            'guardian_name': 'John Smith',
            'date_of_birth': '1985-12-15',
            'weight': 99999.99911,
            'height': 1.02,
            'medication_profile': self.medication_profile.id
        }
        form = PatientForm(data=data)
        if form.is_valid():
            patient = form.save()
            self.assertEqual(patient.first_name, 'Jane')
            self.assertEqual(patient.last_name, 'Doe')
            self.assertEqual(patient.id_number, 444)
            self.assertEqual(patient.guardian_name, 'John Smith')
            self.assertEqual(patient.date_of_birth, datetime.date(1985, 12, 15))
            self.assertEqual(patient.weight, 99999.99911)
            self.assertEqual(patient.height, 1.02)
            self.assertEqual(patient.medication_profile, self.medication_profile)
        else:
            self.fail('Invalid form')

class MedicationFormTestCase(TestCase):

    # Create a Medication Profile for testing
    def setUp(self):
        self.medication_profile=MedicationProfile.objects.create(
            title='Test profile',
            about='Test description',
            id_number=999999,
            is_active=True,
            issues=999
        )

    # VALID CASE: Test a completely valid form
    def test_valid_form(self):

        data = {
            'medication_name': 'Dextrose',
            'calculation_unit': 'KG',
            'medication_profile': self.medication_profile.id,
            'resource_link': 'https://mayoclinic.org',
            'evidence_description': 'Test a detailed description of the dextrose medication',
            'high_risk': False,
            'dose_limit': 10.111111
        }
        form = MedicationForm(data=data)
        self.assertTrue(form.is_valid())

    # INVALID CASE: Test an invalid form that is missing the first_name of the patient and some non-required fields
    def test_missing_fields_invalid(self):

        data = {
            'medication_name': '',
            'calculation_unit': 'KG',
            'resource_link': '',
            'evidence_description': '',
            'high_risk': False,
            'dose_limit': 0
        }
        form = MedicationForm(data=data)
        self.assertFalse(form.is_valid()) and self.assertIn('medication_name', form.errors)

    # VALID CASE: Test saving a form - I included this because I've been having issues getting forms to process save commands
    def test_form_save(self):

        data = {
            'medication_name': 'Dextrose',
            'calculation_unit': 'KG',
            'medication_profile': self.medication_profile.id,
            'resource_link': 'https://www.mayoclinic.org/',
            'evidence_description': 'Test medication',
            'high_risk': True,
            'dose_limit': 12
        }
        form = MedicationForm(data=data)
        if form.is_valid():
            medication = form.save()
            self.assertEqual(medication.medication_name, 'Dextrose')
            self.assertEqual(medication.calculation_unit, 'KG')
            self.assertEqual(medication.resource_link, 'https://www.mayoclinic.org/')
            self.assertEqual(medication.evidence_description, 'Test medication')
            self.assertTrue(medication.high_risk)
            self.assertEqual(medication.dose_limit, 12)
        else:
            self.fail('Invalid form')

class MedicationProfileFormTestCase(TestCase):

    # VALID CASE: Test a completely valid form
    def test_valid_form(self):

        data = {
            'title': 'Test a new med profile',
            'about': 'Test the new med profile detailed description',
            'id_number': 99999999999999999999999,
            'is_active': True,
            'issues': 4000
        }
        form = ProfileForm(data=data)
        self.assertTrue(form.is_valid())

    # INVALID CASE: Test an invalid form that is missing the ID number
    def test_missing_ID_invalid(self):

        data = {
            'title': 'Test a new med profile',
            'about': 'Test the new med profile detailed description',
            'id_number': '',
            'is_active': True,
            'issues': 0
        }
        form = ProfileForm(data=data)
        self.assertFalse(form.is_valid()) and self.assertIn('id_number', form.errors)

    # VALID CASE: Test saving a form - I included this because I've been having issues getting forms to process save commands
    def test_form_save(self):

        data = {
            'title': 'Test a new med profile',
            'about': 'Test the new med profile detailed description',
            'id_number': 888888,
            'is_active': True,
        }
        form = ProfileForm(data=data)
        if form.is_valid():
            profile = form.save()
            self.assertIsInstance(profile, MedicationProfile)
            self.assertEqual(profile.title, 'Test a new med profile')
            self.assertEqual(profile.about, 'Test the new med profile detailed description')
            self.assertEqual(profile.id_number, 888888)
            self.assertTrue(profile.is_active)
        else:
            self.fail('Invalid form')
