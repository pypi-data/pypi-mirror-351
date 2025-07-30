import unittest
from unittest.mock import patch, MagicMock
import datetime
import json
import os

import bloomtracker


class TestDwdPollenApi(unittest.TestCase):
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

    @patch('bloomtracker.client.get_data')
    def test_api(self, mock_get_data):
        # Mock the API response
        mock_get_data.return_value = self.test_data
        
        # Initialize the API
        api = bloomtracker.DwdPollenApi()
        
        # Get pollen data
        result = api.get_pollen(50, -1)
        
        # Check that the result contains expected values
        self.assertEqual(result['region_id'], 50)
        self.assertEqual(result['region_name'], 'Brandenburg und Berlin')
        self.assertIn('Birke', result['pollen'])
        self.assertIn('Hasel', result['pollen'])
        
        # Check that we have pollen data
        self.assertTrue(len(result['pollen']['Birke']) > 0, "No Birke data found")
        self.assertTrue(len(result['pollen']['Hasel']) > 0, "No Hasel data found")


if __name__ == '__main__':
    unittest.main()
