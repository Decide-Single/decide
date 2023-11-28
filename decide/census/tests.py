import json
import os
import tempfile
from datetime import datetime
from datetime import timedelta

import openpyxl
from base.tests import BaseTestCase
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
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


# Export Censuss tests

class BaseExportTestCase(TestCase):
    def setUp(self):
        self.census_data = [
            {
                'voting_id': 1,
                'voter_id': 1,
                'creation_date': timezone.now(),
                'additional_info': 'Test Info 1',
            },
            {
                'voting_id': 2,
                'voter_id': 2,
                'creation_date': timezone.now() - timedelta(days=1),
                'additional_info': 'Test Info 2',
            },
            {
                'voting_id': 3,
                'voter_id': 3,
                'creation_date': timezone.now() - timedelta(days=2),
                'additional_info': 'Test Info 3',
            },
            {
                'voting_id': 4,
                'voter_id': 4,
                'creation_date': timezone.now() - timedelta(days=3),
                'additional_info': 'Test Info 4',
            },
            {
                'voting_id': 5,
                'voter_id': 5,
                'creation_date': timezone.now() - timedelta(days=4),
                'additional_info': 'Test Info 5',
            },
        ]

        self.census_instances = [Census.objects.create(**data) for data in self.census_data]

    def tearDown(self):
        Census.objects.all().delete()


class ExportCensusToCSVTest(BaseExportTestCase):

    def test_export_to_csv(self):
        url = reverse('export_census_to_csv')

        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)

        response_lines = response.content.decode('utf-8').splitlines()

        expected_headers = ['Voting ID', 'Voter ID', 'Creation Date', 'Additional Info']
        self.assertEqual(response_lines[0].split(','), expected_headers)

        for i, census in enumerate(self.census_data):
            if i + 1 < len(response_lines):  # Check if there is a corresponding line in the response
                expected_data = [
                    str(census['voting_id']),
                    str(census['voter_id']),
                    census['creation_date'].strftime('%Y-%m-%d %H:%M:%S'),
                    census['additional_info']
                ]
                actual_data = response_lines[i + 1].split(',')

                for j in [2]:
                    self.assertEqual(actual_data[j].split('.')[0], expected_data[j].split('.')[0])

                # Verificar el resto de los datos
                self.assertEqual(actual_data[:2] + actual_data[3:], expected_data[:2] + expected_data[3:])

        with tempfile.NamedTemporaryFile(mode='w+', suffix='.csv', delete=False) as temp_file:
            response = self.client.get(url)
            temp_file.write(response.content.decode('utf-8'))

        try:
            self.assertEqual(response.status_code, 200)

            with open(temp_file.name, 'r') as file:
                file_content = file.read().splitlines()

            expected_headers = ['Voting ID', 'Voter ID', 'Creation Date', 'Additional Info']
            self.assertEqual(file_content[0].split(','), expected_headers)

            for i, census in enumerate(self.census_data):
                if i + 1 < len(file_content):  # Check if there is a corresponding line in the file
                    expected_data = [
                        str(census['voting_id']),
                        str(census['voter_id']),
                        census['creation_date'].strftime('%Y-%m-%d %H:%M:%S'),
                        census['additional_info']
                    ]
                    actual_data = file_content[i + 1].split(',')

                    for j in [2]:
                        self.assertEqual(actual_data[j].split('.')[0], expected_data[j].split('.')[0])

                    self.assertEqual(actual_data[:2] + actual_data[3:], expected_data[:2] + expected_data[3:])
        finally:
            os.remove(temp_file.name)





