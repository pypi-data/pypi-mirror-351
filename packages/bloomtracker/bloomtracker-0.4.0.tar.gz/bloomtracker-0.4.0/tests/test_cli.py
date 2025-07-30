"""
Tests for the CLI module.
"""

import unittest
from unittest.mock import patch, MagicMock
import io
import sys
import json
import datetime

from bloomtracker.cli import print_json, get_pollen_data, get_regions_data, main


class TestCli(unittest.TestCase):
    def setUp(self):
        # Create sample pollen data
        self.test_data = {
            'region_id': 50,
            'region_name': 'Brandenburg und Berlin',
            'partregion_id': -1,
            'partregion_name': '',
            'last_update': '2025-05-31T11:00:00', 
            'next_update': '2025-06-01T11:00:00',
            'pollen': {
                'Birke': {
                    '2025-05-31': {
                        'value': 3.0, 
                        'raw': '3', 
                        'human': 'hohe Belastung',
                        'color': '#FF0000'
                    },
                    '2025-06-01': {
                        'value': 2.0, 
                        'raw': '2', 
                        'human': 'mittlere Belastung',
                        'color': '#FFFF00'
                    }
                },
                'Hasel': {
                    '2025-05-31': {
                        'value': 0.0,
                        'raw': '0',
                        'human': 'keine Belastung',
                        'color': '#00FF00'
                    }
                }
            }
        }

    def test_get_pollen_data(self):
        # Configure mocks
        mock_api = MagicMock()
        
        # Mock the get_pollen method on the API
        mock_api.get_pollen.return_value = self.test_data
        
        # Call the function directly
        result = get_pollen_data(mock_api, 50, -1)
        
        # Check that data was returned correctly
        self.assertEqual(result['region_name'], 'Brandenburg und Berlin')
        self.assertEqual(result['region_id'], 50)

    @patch('sys.stdout', new_callable=io.StringIO)
    @patch('bloomtracker.cli.get_pollen_data')
    def test_print_json(self, mock_get_pollen_data, mock_stdout):
        # Configure mocks
        mock_api = MagicMock()
        mock_get_pollen_data.return_value = self.test_data
        
        # Call the function
        print_json(mock_api, 50, -1)
        
        # Check that JSON was printed to stdout
        output = mock_stdout.getvalue()
        self.assertTrue(len(output) > 0)
        
        # Verify it's valid JSON
        output_data = json.loads(output)
        self.assertIn('region_name', output_data)
        self.assertEqual(output_data['region_name'], 'Brandenburg und Berlin')
        
    def test_get_regions_data(self):
        # Call the function
        result = get_regions_data()
        
        # Check that it returns regions data
        self.assertIn('regions', result)
        self.assertTrue(isinstance(result['regions'], list))
        self.assertTrue(len(result['regions']) > 0)
        
    @patch('json.dumps')
    @patch('bloomtracker.cli.get_regions_data')
    @patch('bloomtracker.cli.argparse.ArgumentParser.parse_args')
    @patch('bloomtracker.cli.DwdPollenApi')
    def test_main_list_regions(self, mock_api_class, mock_parse_args, mock_get_regions_data, mock_json_dumps):
        # Configure mocks
        mock_args = MagicMock(list=True, region=None)
        mock_parse_args.return_value = mock_args
        
        mock_regions_data = {'regions': [{'region_id': 50, 'partregion_id': -1, 'name': 'Test Region'}]}
        mock_get_regions_data.return_value = mock_regions_data
        mock_json_dumps.return_value = '{"regions": [...]}'
        
        # Call the function
        main()
        
        # Check that get_regions_data was called
        mock_get_regions_data.assert_called_once()
        # Check that json.dumps was called with the regions data
        # Need to include the DateTimeEncoder class that was added to fix JSON serialization
        from bloomtracker.cli import DateTimeEncoder
        mock_json_dumps.assert_called_once_with(mock_regions_data, ensure_ascii=False, indent=2, cls=DateTimeEncoder)
        
    @patch('bloomtracker.cli.print_json')
    @patch('bloomtracker.cli.argparse.ArgumentParser.parse_args')
    @patch('bloomtracker.cli.DwdPollenApi')
    def test_main_print_json(self, mock_api_class, mock_parse_args, mock_print_json):
        # Configure mocks
        mock_args = MagicMock(list=False, region=50, partregion=-1, output=None, no_cache=False)
        mock_parse_args.return_value = mock_args
        
        # Call the function
        main()
        
        # Check that print_json was called with the correct arguments
        mock_print_json.assert_called_once_with(mock_api_class.return_value, 50, -1, None)


if __name__ == '__main__':
    unittest.main()
