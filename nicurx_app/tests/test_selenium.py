from django.test import LiveServerTestCase
from nicurx_app.models import *


# Firefox webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver import Firefox

# Keyboard functions
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
import time

class SeleniumTests(LiveServerTestCase):
    
    # Setup the browser interface. In this case Mozilla Firefox is being used
    def setUp(self):
        options = Options()
        options.add_argument("--headless")
        self.browser = Firefox(options=options)

    # TEST 1: Test to ensure the main page is loaded correctly 
    def testHomePage(self):
        self.browser.get("http://127.0.0.1:8000")
        time.sleep(1)
        assert 'NICURx' in self.browser.title

    # TEST 2: Test to ensure navigation functions. This test navigates to the login page
    def testLoginNavigation(self):
        self.browser.get("http://127.0.0.1:8000")
        time.sleep(1)
        self.browser.find_element(By.XPATH, "//a[@href='/accounts/login/' and contains(@class, 'btn btn-primary custom-btn-primary')]").click()
        time.sleep(1)
        self.assertIn("/accounts/login/", self.browser.current_url)

    # TEST 3: Test inputting login information for a test user and logging into the supervisor role
    def testLoginForm(self):
        self.browser.get("http://127.0.0.1:8000/accounts/login")
        time.sleep(1)
        self.browser.find_element(By.XPATH, "//form//table//tr[1]//input").send_keys("test3")
        self.browser.find_element(By.XPATH, "//form//table//tr[2]//input").send_keys("zxcvbnm1234567")
        time.sleep(1)
        self.browser.find_element(By.XPATH, "//input[@type='submit']").click()
        time.sleep(1)
        self.assertEqual(self.browser.current_url, "http://127.0.0.1:8000/user/")
        
    # TEST 4: Test creating a patient, viewing the new profile, and deleting the patient
    # Note that the patient is deleted so that this test is repeatable without needing to delete the patient manually
    # Since a one-to-one relationship exists with the medication profile, the form will not submit if a duplicate patient exists
    def testCreatePatientForm(self):
        self.browser.get("http://127.0.0.1:8000")
        time.sleep(1)
        self.browser.find_element(By.XPATH, "//a[@href='/patient_list/' and contains(@class, 'btn btn-primary custom-btn-primary')]").click()
        time.sleep(1)
        self.browser.find_element(By.XPATH, "//a[@href='/patient/create_patient/' and contains(@class, 'btn btn-primary custom-btn-primary')]").click()
        time.sleep(1)
        self.browser.find_element(By.XPATH, "//form//table//tr[1]//input").send_keys("Space")
        self.browser.find_element(By.XPATH, "//form//table//tr[2]//input").send_keys("Boy")
        self.browser.find_element(By.XPATH, "//form//table//tr[3]//input").send_keys("AAA")
        self.browser.find_element(By.XPATH, "//form//table//tr[4]//input").send_keys("55555")
        self.browser.find_element(By.XPATH, "//form//table//tr[5]//input").send_keys("Guardian Name Test")
        select_element = self.browser.find_element(By.XPATH, "//form//table//tr[9]//select")
        dropdown = Select(select_element)
        dropdown.select_by_visible_text("Selenium Test")
        time.sleep(1)
        self.browser.find_element(By.XPATH, "//input[@type='submit']").click()
        patient_id = self.browser.current_url.split('/')[-1]
        time.sleep(1)
        self.browser.find_element(By.XPATH, "//a[@href='/patient_list/' and contains(@class, 'btn btn-primary custom-btn-primary')]").click()
        time.sleep(1)
        
        print("Patient ID is " + patient_id)
        self.browser.get("http://127.0.0.1:8000/patient/delete_patient/%s" % patient_id)
        time.sleep(1)
        self.browser.find_element(By.XPATH, "//input[@type='submit']").click()
        time.sleep(1)
        self.assertEqual(self.browser.current_url, "http://127.0.0.1:8000/patient_list/")

    # Close the server and browser. This function is an automatically recognized function under Django's unittest framework
    # This function is automatically called after each test above to ensure a clean environmnet exists for the test.
    # This modularizes the testing process to ensure tests are self contained.
    def tearDown(self):
        self.browser.quit()