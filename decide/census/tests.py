import json
import os
import tempfile
from datetime import datetime
from datetime import timedelta

import openpyxl
from base.tests import BaseTestCase
from datetime import datetime
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from io import BytesIO
from openpyxl import Workbook
from operator import attrgetter
from selenium import webdriver
from selenium.webdriver.common.by import By

from .models import Census

class CensusTestCase(BaseTestCase):

    def setUp(self):
        super().setUp()
        self.census = Census(voting_id=1, voter_id=1)
        self.census.save()

    def tearDown(self):
        super().tearDown()
        self.census = None

    def test_check_vote_permissions(self):
        
        response = self.client.get('/census/{}/?voter_id={}'.format(1, 2), format='json')
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json().get('detail'), 'Not found.')

        response = self.client.get('/census/{}/?voter_id={}'.format(1, 1), format='json')
        self.assertEqual(response.status_code, 200)

    def test_list_voting(self):
        response = self.client.get('/census/?voting_id={}'.format(1), format='json')
        self.assertEqual(response.status_code, 401)

        self.login(user='noadmin')
        response = self.client.get('/census/?voting_id={}'.format(1), format='json')
        self.assertEqual(response.status_code, 403)

        self.login()
        response = self.client.get('/census/?voting_id={}'.format(1), format='json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()[0].get('voter_id'), 1)

    def test_add_new_voters_conflict(self):
        data = {'voting_id': 1, 'voters': [1]}
        response = self.client.post('/census/', data, format='json')
        self.assertEqual(response.status_code, 401)

        self.login(user='noadmin')
        response = self.client.post('/census/', data, format='json')
        self.assertEqual(response.status_code, 403)

        self.login()
        response = self.client.post('/census/', data, format='json')
        self.assertEqual(response.status_code, 409)

    def test_add_new_voters(self):
        data = {'voting_id': 2, 'voters': [1,2]}
        response = self.client.post('/census/', data, format='json')
        self.assertEqual(response.status_code, 401)

        self.login(user='noadmin')
        response = self.client.post('/census/', data, format='json')
        self.assertEqual(response.status_code, 403)

        self.login()
        response = self.client.post('/census/', data, format='json')
        self.assertEqual(response.status_code, 201)

        self.assertEqual(len(data.get('voters')), Census.objects.count())

    def test_destroy_voter(self):
        data = {'voters': [1]}
        response = self.client.delete('/census/{}/'.format(1), data, format='json')
        self.assertEqual(response.status_code, 204)
        self.assertEqual(0, Census.objects.count())

class CensusTest(StaticLiveServerTestCase):
    def setUp(self):
        #Load base test functionality for decide
        self.base = BaseTestCase()
        self.base.setUp()

        options = webdriver.ChromeOptions()
        options.headless = True
        self.driver = webdriver.Chrome(options=options)

        super().setUp()

    def tearDown(self):
        super().tearDown()
        self.driver.quit()

        self.base.tearDown()
    
    def createCensusSuccess(self):
        self.cleaner.get(self.live_server_url+"/admin/login/?next=/admin/")
        self.cleaner.set_window_size(1280, 720)

        self.cleaner.find_element(By.ID, "id_username").click()
        self.cleaner.find_element(By.ID, "id_username").send_keys("decide")

        self.cleaner.find_element(By.ID, "id_password").click()
        self.cleaner.find_element(By.ID, "id_password").send_keys("decide")

        self.cleaner.find_element(By.ID, "id_password").send_keys("Keys.ENTER")

        self.cleaner.get(self.live_server_url+"/admin/census/census/add")
        now = datetime.now()
        self.cleaner.find_element(By.ID, "id_voting_id").click()
        self.cleaner.find_element(By.ID, "id_voting_id").send_keys(now.strftime("%m%d%M%S"))
        self.cleaner.find_element(By.ID, "id_voter_id").click()
        self.cleaner.find_element(By.ID, "id_voter_id").send_keys(now.strftime("%m%d%M%S"))
        self.cleaner.find_element(By.NAME, "_save").click()

        self.assertTrue(self.cleaner.current_url == self.live_server_url+"/admin/census/census")

    def createCensusEmptyError(self):
        self.cleaner.get(self.live_server_url+"/admin/login/?next=/admin/")
        self.cleaner.set_window_size(1280, 720)

        self.cleaner.find_element(By.ID, "id_username").click()
        self.cleaner.find_element(By.ID, "id_username").send_keys("decide")

        self.cleaner.find_element(By.ID, "id_password").click()
        self.cleaner.find_element(By.ID, "id_password").send_keys("decide")

        self.cleaner.find_element(By.ID, "id_password").send_keys("Keys.ENTER")

        self.cleaner.get(self.live_server_url+"/admin/census/census/add")

        self.cleaner.find_element(By.NAME, "_save").click()

        self.assertTrue(self.cleaner.find_element_by_xpath('/html/body/div/div[3]/div/div[1]/div/form/div/p').text == 'Please correct the errors below.')
        self.assertTrue(self.cleaner.current_url == self.live_server_url+"/admin/census/census/add")

    def createCensusValueError(self):
        self.cleaner.get(self.live_server_url+"/admin/login/?next=/admin/")
        self.cleaner.set_window_size(1280, 720)

        self.cleaner.find_element(By.ID, "id_username").click()
        self.cleaner.find_element(By.ID, "id_username").send_keys("decide")

        self.cleaner.find_element(By.ID, "id_password").click()
        self.cleaner.find_element(By.ID, "id_password").send_keys("decide")

        self.cleaner.find_element(By.ID, "id_password").send_keys("Keys.ENTER")

        self.cleaner.get(self.live_server_url+"/admin/census/census/add")
        now = datetime.now()
        self.cleaner.find_element(By.ID, "id_voting_id").click()
        self.cleaner.find_element(By.ID, "id_voting_id").send_keys('64654654654654')
        self.cleaner.find_element(By.ID, "id_voter_id").click()
        self.cleaner.find_element(By.ID, "id_voter_id").send_keys('64654654654654')
        self.cleaner.find_element(By.NAME, "_save").click()

        self.assertTrue(self.cleaner.find_element_by_xpath('/html/body/div/div[3]/div/div[1]/div/form/div/p').text == 'Please correct the errors below.')
        self.assertTrue(self.cleaner.current_url == self.live_server_url+"/admin/census/census/add")


class CensusImportViewTest(TestCase):

    def tearDown(self):
        Census.objects.all().delete()

    def _assert_census_data(self, census_objects):
        census_objects = sorted(census_objects, key=attrgetter('voting_id'))

        self.assertEqual(census_objects[0].voting_id, 1)
        self.assertEqual(census_objects[0].voter_id, 1)
        self.assertEqual(census_objects[0].additional_info, 'Info1')

        self.assertEqual(census_objects[1].voting_id, 2)
        self.assertEqual(census_objects[1].voter_id, 2)
        self.assertEqual(census_objects[1].additional_info, 'Info2')

    def test_import_csv(self):
        csv_file = SimpleUploadedFile("test.csv", b"voting_id,voter_id,creation_date,additional_info\n1,1,22023-11-28 11:47:12.015914+00:00,Info1\n2,2,2023-11-28 11:47:12.015914+00:00,Info2", content_type="text/csv")
        url = reverse('import_census')
        response = self.client.post(url, {'file': csv_file}, format='multipart')

        self.assertEqual(response.status_code, 201)
        self.assertEqual(Census.objects.count(), 2)
        self._assert_census_data(Census.objects.all())

    def test_import_json(self):
        json_data = [{'voting_id': 1, 'voter_id': 1, 'creation_date': '2023-11-28 11:47:12.015914+00:00', 'additional_info': 'Info1'},
                     {'voting_id': 2, 'voter_id': 2, 'creation_date': '2023-11-28 11:47:12.015914+00:00', 'additional_info': 'Info2'}]
        json_file = SimpleUploadedFile("test.json", json.dumps(json_data).encode(), content_type="application/json")
        response = self.client.post(reverse('import_census'), {'file': json_file}, format='multipart')

        self.assertEqual(response.status_code, 201)
        self.assertEqual(Census.objects.count(), 2)
        self._assert_census_data(Census.objects.all())

    def test_import_excel(self):
        workbook = Workbook()
        sheet = workbook.active
        sheet.append(['voting_id', 'voter_id', 'creation_date', 'additional_info'])
        sheet.append([1, 1, '2023-11-28 11:47:12.015914+00:00', 'Info1'])
        sheet.append([2, 2, '2023-11-28 11:47:12.015914+00:00', 'Info2'])
        excel_buffer = BytesIO()
        workbook.save(excel_buffer)
        excel_buffer.seek(0)
        excel_file = SimpleUploadedFile("test.xlsx", excel_buffer.read(), content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
        response = self.client.post(reverse('import_census'), {'file': excel_file}, format='multipart')

        self.assertEqual(response.status_code, 201)
        self.assertEqual(Census.objects.count(), 2)
        self._assert_census_data(Census.objects.all())

    def test_invalid_file_format(self):
        invalid_file = SimpleUploadedFile("test.txt", b"Invalid file content", content_type="text/plain")
        response = self.client.post(reverse('import_census'), {'file': invalid_file}, format='multipart')

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), {'error': 'Unsupported file format'})

