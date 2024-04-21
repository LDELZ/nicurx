from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from nicurx_app.models import MedicationProfile, Patient, Medication, Supervisor, MedicationDosage
import datetime

# Create your tests here.
class ViewTestCase(TestCase):
    def setUp(self):

        # Create a test user - demonstration
        self.user = User.objects.create_user(username='testuser', password='password123')

        # Create a Medication Profile for testing
        self.medication_profile=MedicationProfile.objects.create(
            title='Test profile',
            about='Test description',
            id_number=999999,
            is_active=True,
            issues=999
        )

        # Create a Patient for testing
        self.patient=Patient.objects.create(
            is_active=True,
            first_name='John',
            last_name='Doe',
            id_number=99999,
            guardian_name='Jane Doe',
            date_of_birth=datetime.date(1990, 5, 20),
            weight=75,
            height=175,
            medication_profile=self.medication_profile
        )

        # Create a Medication for testing
        self.medication=Medication.objects.create(
            calculation_unit='KG',
            medication_name='Dextrose',
            resource_link='https://www.mayoclinic.org/',
            evidence_description='test text box',
            high_risk=False,
            dose_limit=3.34555,
            medication_profile=self.medication_profile
        )
        
        # Create Medication Dosage for testing
        self.medication_dosage=MedicationDosage.objects.create(
            dose=999.9999,
            medication=self.medication,
            profile=self.medication_profile
        )

        # Create a Supervisor for testing
        self.supervisor=Supervisor.objects.create(
            user=self.user,
            supervisor_name='Test supervisor'
        )

    # VALID CASE: Test the main index page view using valid view generation
    def test_index_view_valid(self):
        client = Client()
        response = client.get(reverse('index'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'nicurx_app/index.html')

    # INVALID CASE: Test the main user page view without being authenticated 
    def test_index_view_invalid_unauthenticated(self):
        client = Client()
        response = client.get(reverse('user_page'))
        self.assertEqual(response.status_code, 302)

    # VALID CASE: Test the view to update a patient object using the update form
    def test_update_patient_view_valid(self):
        client = Client()
        response = client.get(reverse('update-patient', kwargs={'patient_id': self.patient.id}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'nicurx_app/update_form.html')

        # Test a POST request
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
        response = client.post(reverse('update-patient', kwargs={'patient_id': self.patient.id}), data=data)
        self.assertEqual(response.status_code, 302)

        # Check if the patient was updated by comparing with the updated data
        self.assertEqual(self.patient.is_active, data['is_active'])
        self.assertEqual(self.patient.first_name, data['first_name'])
        self.assertEqual(self.patient.last_name, data['last_name'])
        self.assertEqual(self.patient.id_number, data['id_number'])
        self.assertEqual(self.patient.guardian_name, data['guardian_name'])
        self.assertEqual(self.patient.date_of_birth, datetime.datetime.strptime(data['date_of_birth'], '%Y-%m-%d').date())
        self.assertEqual(self.patient.weight, data['weight'])
        self.assertEqual(self.patient.height, data['height'])
        self.assertEqual(self.patient.medication_profile.id, data['medication_profile'])

    # INVALID CASE: Test the view to update a patient object using the update form but with invalid data
    def test_update_patient_view_invalid(self):
        client = Client()
        response = client.get(reverse('update-patient', kwargs={'patient_id': self.patient.id}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'nicurx_app/update_form.html')

        data = {
            'is_active': True,
            'first_name': '',
            'last_name': '',
            'id_number': 99999,
            'guardian_name': 'Jane Doe',
            'date_of_birth': '1990-05-20',
            'weight': 75,
            'height': 175,
            'medication_profile': self.medication_profile.id
        }

        response = client.post(reverse('update-patient', kwargs={'patient_id': self.patient.id}), data=data)
        self.assertNotEqual(response.status_code, 302)
        self.assertFormError(response, 'form', 'first_name', 'This field is required.')
        self.assertFormError(response, 'form', 'last_name', 'This field is required.')
        self.patient.refresh_from_db()
        self.assertNotEqual(self.patient.first_name, data['first_name'])
        self.assertNotEqual(self.patient.last_name, data['last_name'])