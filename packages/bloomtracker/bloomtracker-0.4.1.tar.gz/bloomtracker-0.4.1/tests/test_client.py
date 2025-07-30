"""
Tests for the client module.
"""

import unittest
from unittest.mock import patch, MagicMock, mock_open
import datetime
import json
import os
import tempfile
import requests

from bloomtracker.client import DwdPollenApi, get_data, build_legend
from bloomtracker.exceptions import DwdPollenError


class TestClient(unittest.TestCase):
    def setUp(self):
        # Create a sample response file
        self.test_data = {
            'last_update': '2025-05-31 11:00 Uhr',
            'next_update': '2025-06-01 11:00 Uhr',
            'legend': {
                'id1': '0',
                'id1_desc': 'keine Belastung',
                'id2': '0-1',
                'id2_desc': 'keine bis geringe Belastung',
                'id3': '1',
                'id3_desc': 'geringe Belastung',
                'id4': '1-2',
                'id4_desc': 'geringe bis mittlere Belastung',
                'id5': '2',
                'id5_desc': 'mittlere Belastung',
                'id6': '2-3',
                'id6_desc': 'mittlere bis hohe Belastung',
                'id7': '3',
                'id7_desc': 'hohe Belastung'
            },
            'content': [
                {
                    'region_id': 50,
                    'region_name': 'Brandenburg und Berlin',
                    'partregion_id': -1,
                    'partregion_name': '',
                    'Pollen': {
                        'Birke': {
                            'today': '3',
                            'tomorrow': '2',
                            'dayafter_to': '1'
                        },
                        'Hasel': {
                            'today': '0',
                            'tomorrow': '0',
                            'dayafter_to': '0'
                        }
                    }
                }
            ]
        }
        
    @patch('bloomtracker.client.requests.get')
    def test_get_data(self, mock_get):
        # Configure the mock
        mock_response = MagicMock()
        mock_response.json.return_value = self.test_data
        mock_get.return_value = mock_response
        
        # Call the function
        result = get_data("https://example.com/api")
        
        # Check the result
        self.assertEqual(result, self.test_data)
        mock_get.assert_called_once_with("https://example.com/api", timeout=30)
        
    @patch('bloomtracker.client.requests.get')
    def test_get_data_with_retry(self, mock_get):
        # Configure the mock to fail twice then succeed
        mock_response = MagicMock()
        mock_response.json.return_value = self.test_data
        
        mock_get.side_effect = [
            requests.RequestException("Connection error"),  # First attempt fails
            requests.RequestException("Timeout"),           # Second attempt fails
            mock_response                   # Third attempt succeeds
        ]
        
        # Call the function (should succeed on third try)
        result = get_data("https://example.com/api", retry_count=3, retry_delay=0)
        
        # Check the result
        self.assertEqual(result, self.test_data)
        self.assertEqual(mock_get.call_count, 3)
        
    @patch('bloomtracker.client.requests.get')
    def test_get_data_all_retries_fail(self, mock_get):
        # Configure the mock to fail all attempts with requests.RequestException
        mock_get.side_effect = requests.RequestException("Connection error")
        
        # Call the function (should raise an exception)
        with self.assertRaises(DwdPollenError):
            get_data("https://example.com/api", retry_count=3, retry_delay=0)
            
        # Check the mock was called the expected number of times
        self.assertEqual(mock_get.call_count, 3)
        
    def test_build_legend(self):
        # Test the legend builder
        legend = self.test_data['legend']
        result = build_legend(legend)
        
        # Check the result
        self.assertEqual(result['0'], 'keine Belastung')
        self.assertEqual(result['1'], 'geringe Belastung')
        self.assertEqual(result['2'], 'mittlere Belastung')
        self.assertEqual(result['3'], 'hohe Belastung')
        self.assertEqual(result['0-1'], 'keine bis geringe Belastung')
        self.assertEqual(result['1-2'], 'geringe bis mittlere Belastung')
        self.assertEqual(result['2-3'], 'mittlere bis hohe Belastung')
    
    @patch('bloomtracker.client.get_data')
    @patch('bloomtracker.client.os.path.exists')
    @patch('bloomtracker.client.os.path.getmtime')
    @patch('builtins.open', new_callable=mock_open)
    def test_load_from_cache(self, mock_file, mock_getmtime, mock_exists, mock_get_data):
        # Configure the mocks
        mock_exists.return_value = True
        mock_getmtime.return_value = datetime.datetime.now().timestamp()  # Recent timestamp
        
        cache_data = {
            'data': {'50--1': {'region_id': 50, 'region_name': 'Test Region'}},
            'legend': {'0': 'keine Belastung'},
            'last_update': '2025-05-31T11:00:00',
            'next_update': '2025-06-01T11:00:00',
        }
        
        mock_file.return_value.read.return_value = json.dumps(cache_data)
        
        # Create API with auto_update=False so it doesn't try to fetch data
        api = DwdPollenApi(auto_update=False)
        
        # Test loading from cache
        result = api.load_from_cache()
        
        # Check the result
        self.assertTrue(result)
        self.assertEqual(api.data, cache_data['data'])
        self.assertEqual(api.legend, cache_data['legend'])
        mock_get_data.assert_not_called()  # Should not call the API
        
    @patch('bloomtracker.client.os.path.exists')
    def test_load_from_cache_no_cache_file(self, mock_exists):
        # Configure the mock to return False (no cache file)
        mock_exists.return_value = False
        
        # Create API with auto_update=False
        api = DwdPollenApi(auto_update=False)
        
        # Test loading from cache
        result = api.load_from_cache()
        
        # Check the result
        self.assertFalse(result)
        
    @patch('bloomtracker.client.get_data')
    def test_get_pollen(self, mock_get_data):
        # Configure the mock
        mock_get_data.return_value = self.test_data
        
        # Create API
        api = DwdPollenApi()
        
        # Get pollen data
        result = api.get_pollen(50, -1)
        
        # Check the result
        self.assertEqual(result['region_id'], 50)
        self.assertEqual(result['region_name'], 'Brandenburg und Berlin')
        self.assertIn('Birke', result['pollen'])
        self.assertIn('Hasel', result['pollen'])
        
    @patch('bloomtracker.client.get_data')
    @patch('bloomtracker.client.DwdPollenApi.load_from_cache', return_value=False)
    def test_get_region_names(self, mock_load_cache, mock_get_data):
        # Configure the mock
        mock_get_data.return_value = self.test_data
        
        # Create API
        api = DwdPollenApi()
        
        # Get region names
        result = api.get_region_names()
        
        # Check the result
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0][0], 50)  # region_id
        self.assertEqual(result[0][1], -1)  # partregion_id
        self.assertEqual(result[0][2], 'Brandenburg und Berlin')  # region_name
        
    @patch('bloomtracker.client.get_data')
    @patch('bloomtracker.client.DwdPollenApi.load_from_cache', return_value=False)
    def test_get_allergen_names(self, mock_load_cache, mock_get_data):
        # Configure the mock
        mock_get_data.return_value = self.test_data
        
        # Create API
        api = DwdPollenApi()
        
        # Get allergen names
        result = api.get_allergen_names()
        
        # Check the result
        self.assertEqual(len(result), 2)
        self.assertIn('Birke', result)
        self.assertIn('Hasel', result)
        
    @patch('bloomtracker.client.get_data')
    def test_get_allergen_for_region(self, mock_get_data):
        # Configure the mock
        mock_get_data.return_value = self.test_data
        
        # Create API
        api = DwdPollenApi()
        
        # Get allergen data
        result = api.get_allergen_for_region(50, -1, 'Birke')
        
        # Check the result
        self.assertTrue(len(result) > 0)
        
    @patch('bloomtracker.client.get_data')
    def test_get_forecast_summary(self, mock_get_data):
        # Configure the mock
        mock_get_data.return_value = self.test_data
        
        # Create API
        api = DwdPollenApi()
        
        # Get forecast summary
        result = api.get_forecast_summary(50, -1)
        
        # Check the result
        self.assertTrue(len(result) > 0)
        # Each date should have allergen summaries
        for date_str, allergens in result.items():
            self.assertTrue(isinstance(date_str, str))
            self.assertTrue(isinstance(allergens, dict))
