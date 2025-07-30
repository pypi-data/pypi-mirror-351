"""
Tests for the async client module.
"""

import unittest
from unittest.mock import patch, MagicMock, AsyncMock
import datetime
import json
import asyncio
import aiohttp

from bloomtracker.async_client import AsyncDwdPollenApi, get_data_async
from bloomtracker.exceptions import DwdPollenError


class TestAsyncClient(unittest.IsolatedAsyncioTestCase):
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
        
    @patch('aiohttp.ClientSession.get')
    async def test_get_data_async(self, mock_get):
        # Configure the mock
        mock_response = AsyncMock()
        mock_response.raise_for_status = AsyncMock()
        # Use AsyncMock for json() to ensure it's properly awaited
        mock_response.json = AsyncMock(return_value=self.test_data)
        mock_get.return_value.__aenter__.return_value = mock_response
        
        # Call the function
        result = await get_data_async("https://example.com/api")
        
        # Check the result
        self.assertEqual(result, self.test_data)
        
        # Verify that our async methods were properly called
        # We don't use assert_awaited_once() since raise_for_status might be called directly
        # in older aiohttp versions and awaited in newer ones
        mock_response.raise_for_status.assert_called_once()
        mock_response.json.assert_called_once()
        
    @patch('aiohttp.ClientSession.get')
    async def test_get_data_async_error(self, mock_get):
        # Configure the mock to raise an exception
        mock_get.return_value.__aenter__.side_effect = Exception("Connection error")
        
        # Call the function and expect an exception
        with self.assertRaises(DwdPollenError):
            await get_data_async("https://example.com/api")
            
    @patch('aiohttp.ClientSession.get')
    async def test_get_data_async_http_error(self, mock_get):
        # Configure the mock to return an HTTP error
        mock_response = AsyncMock()
        mock_response.raise_for_status = AsyncMock(side_effect=aiohttp.ClientResponseError(
            request_info=AsyncMock(), history=(), status=404, message="Not Found"))
        mock_get.return_value.__aenter__.return_value = mock_response
        
        # Call the function and expect a DwdPollenError
        with self.assertRaises(DwdPollenError):
            await get_data_async("https://example.com/api")
        
    @patch('bloomtracker.async_client.get_data_async')
    async def test_async_api_update(self, mock_get_data):
        # Configure the mock
        mock_get_data.return_value = self.test_data
        
        # Create API
        api = AsyncDwdPollenApi()
        
        # Update data
        await api.update()
        
        # Check the result
        self.assertEqual(api.last_update.strftime('%Y-%m-%d %H:%M'), '2025-05-31 11:00')
        self.assertEqual(api.next_update.strftime('%Y-%m-%d %H:%M'), '2025-06-01 11:00')
        self.assertTrue(len(api.data) > 0)
        
    @patch('bloomtracker.async_client.get_data_async')
    async def test_get_pollen_async(self, mock_get_data):
        # Configure the mock
        mock_get_data.return_value = self.test_data
        
        # Create API
        api = AsyncDwdPollenApi()
        await api.update()
        
        # Get pollen data
        result = await api.get_pollen(50, -1)
        
        # Check the result
        self.assertEqual(result['region_id'], 50)
        self.assertEqual(result['region_name'], 'Brandenburg und Berlin')
        self.assertIn('Birke', result['pollen'])
        self.assertIn('Hasel', result['pollen'])
        
    @patch('bloomtracker.async_client.get_data_async')
    async def test_get_region_names_async(self, mock_get_data):
        # Configure the mock
        mock_get_data.return_value = self.test_data
        
        # Create API
        api = AsyncDwdPollenApi()
        await api.update()
        
        # Get region names
        result = await api.get_region_names()
        
        # Check the result
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0][0], 50)  # region_id
        self.assertEqual(result[0][1], -1)  # partregion_id
        self.assertEqual(result[0][2], 'Brandenburg und Berlin')  # region_name
        
    @patch('bloomtracker.async_client.get_data_async')
    async def test_get_allergen_names_async(self, mock_get_data):
        # Configure the mock
        mock_get_data.return_value = self.test_data
        
        # Create API
        api = AsyncDwdPollenApi()
        await api.update()
        
        # Get allergen names
        result = await api.get_allergen_names()
        
        # Check the result
        self.assertEqual(len(result), 2)
        self.assertIn('Birke', result)
        self.assertIn('Hasel', result)
        
    @patch('bloomtracker.async_client.get_data_async')
    async def test_get_allergen_for_region_async(self, mock_get_data):
        # Configure the mock
        mock_get_data.return_value = self.test_data
        
        # Create API
        api = AsyncDwdPollenApi()
        await api.update()
        
        # Get allergen data
        result = await api.get_allergen_for_region(50, -1, 'Birke')
        
        # Check the result
        self.assertTrue(len(result) > 0)
