"""
Tests for the visualization module.
"""

import unittest
from unittest.mock import patch, MagicMock
import io
import sys

from bloomtracker.visualization import generate_chart


class TestVisualization(unittest.TestCase):
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
                    }
                }
            }
        }

    def test_generate_chart(self):
        # Call the function
        result = generate_chart(self.test_data)
        
        # Verify result is BytesIO object
        self.assertIsNotNone(result)
        self.assertEqual(type(result).__name__, 'BytesIO')


if __name__ == '__main__':
    unittest.main()
