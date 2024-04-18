from django.test import TestCase
from django.contrib.auth.models import User
from nicurx_app.models import MedicationProfile, Patient, Medication, Supervisor, MedicationDosage
import datetime


# Create your tests here.
class ModelTestCase(TestCase):
    def setUp(self):

        # Create a test user
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
            id_number=12345,
            guardian_name='Jane Doe',
            date_of_birth=datetime.date(1990, 5, 20),
            weight=70.0,
            height=180.0,
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

    # Test field creations by asserting their validity. Matching validity will mark the test as 'OK' in the command line
    # Test medication profile object creation
    def test_medication_profile_creation(self):
        self.assertEqual(self.medication_profile.title, 'Test profile')
        self.assertEqual(self.medication_profile.about, 'Test description')
        self.assertEqual(self.medication_profile.id_number, 999999)
        self.assertTrue(self.medication_profile.is_active)
        self.assertEqual(self.medication_profile.issues, 999)
        self.assertEqual(self.medication_profile.get_absolute_url(), '/profile/1')

    # Test patient object creation
    def test_patient_creation(self):
        self.assertTrue(self.patient.is_active)
        self.assertEqual(self.patient.first_name, 'John')
        self.assertEqual(self.patient.last_name, 'Doe')
        self.assertEqual(self.patient.id_number, 12345)
        self.assertEqual(self.patient.guardian_name, 'Jane Doe')
        self.assertEqual(self.patient.date_of_birth, datetime.date(1990, 5, 20))
        self.assertEqual(self.patient.weight, 70.0)
        self.assertEqual(self.patient.height, 180.0)
        self.assertEqual(self.patient.medication_profile, self.medication_profile)
        self.assertEqual(self.patient.get_absolute_url(), '/patient/1')

    # Test medication object creation
    def test_medication_creation(self):
        self.assertEqual(self.medication.calculation_unit, 'KG')
        self.assertEqual(self.medication.medication_name, 'Dextrose')
        self.assertEqual(self.medication.resource_link, 'https://www.mayoclinic.org/')
        self.assertEqual(self.medication.evidence_description, 'test text box')
        self.assertFalse(self.medication.high_risk)
        self.assertAlmostEqual(self.medication.dose_limit, 3.34555, places=5)
        self.assertEqual(self.medication.medication_profile, self.medication_profile)
        self.assertEqual(self.medication.get_absolute_url(), '/medication/1')

    # Test medication dose object creation
    def test_medication_dosage_creation(self):
        self.assertAlmostEqual(self.medication_dosage.dose, 999.9999, places=4)
        self.assertEqual(self.medication_dosage.medication, self.medication)
        self.assertEqual(self.medication_dosage.profile, self.medication_profile)

    # Test supervisor object creation
    def test_supervisor_creation(self):
        self.assertEqual(self.supervisor.user, self.user)
        self.assertEqual(self.supervisor.supervisor_name, 'Test supervisor')