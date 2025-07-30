"""
Asynchronous API client implementation for DWD pollen data.
"""

import asyncio
import datetime
from typing import Dict, Any, Union, Optional, List, Tuple
import pytz
import aiohttp

from .exceptions import DwdPollenError
from .client import build_legend

DWD_URL = 'https://opendata.dwd.de/climate_environment/health/alerts/s31fg.json'


async def get_data_async(url: str, timeout: int = 30) -> Dict[str, Any]:
    """
    Fetch the data via HTTP asynchronously and return it as a dictionary.

    Args:
        url: The API URL.
        timeout: Request timeout in seconds.

    Returns:
        The API response as a dictionary.

    Raises:
        DwdPollenError: If the request fails.
    """
    try:
        timeout_obj = aiohttp.ClientTimeout(total=timeout)
        async with aiohttp.ClientSession(timeout=timeout_obj) as session:
            async with session.get(url) as response:
                await response.raise_for_status()  # type: ignore[func-returns-value]  # Only for side effects
                return await response.json()
    except Exception as e:
        # Catch all exceptions and wrap them in DwdPollenError
        raise DwdPollenError(f"Failed to fetch data: {str(e)}") from e


class AsyncDwdPollenApi:
    """Asynchronous API client object to get the current pollen load in Germany."""

    def __init__(self, auto_update: bool = False):
        """
        Initialize the asynchronous DWD pollen API client.

        Args:
            auto_update: Whether to update data on initialization.
        """
        self.last_update: Optional[datetime.datetime] = None
        self.next_update: Optional[datetime.datetime] = None
        self.content = None
        self.data: Dict[str, Dict[str, Any]] = {}
        self.legend: Optional[Dict[str, str]] = None
        # Will be set if auto_update is called
        self._initialization_task = None
        if auto_update:
            self._initialization_task = asyncio.create_task(self.update())

    async def build_pollen(self, allergen: Dict[str, str]) -> Dict[str, Dict[str, Any]]:
        """
        Transform the pollen load of one allergen into something useful.

        Args:
            allergen: One allergen dictionary as it is returned by the API.

        Returns:
            A dictionary of dictionaries with dates as keys and allergen values as values.
        """

        def build_values(value: str) -> Dict[str, Union[float, str]]:
            if self.legend is None:
                raise DwdPollenError("Legend data not available")
            return {
                'value': calculate_value(value),
                'raw': value,
                'human': self.legend[value],
                'color': get_color_for_value(calculate_value(value))
            }

        def calculate_value(value: str) -> float:
            items = value.split('-')
            result = 0
            for item in items:
                result += int(item)
            return result / len(items)

        def get_color_for_value(value: float) -> str:
            """Return a color representation for the value."""
            if value <= 0.0:
                return '#00FF00'  # Green - No load
            if value <= 1.0:
                return '#ADFF2F'  # GreenYellow - Low load
            if value <= 2.0:
                return '#FFFF00'  # Yellow - Medium load
            if value <= 2.5:
                return '#FFA500'  # Orange - Medium-high load
            return '#FF0000'  # Red - High load

        new_pollen: Dict[str, Dict[str, Any]] = {}
        today = datetime.datetime.now(pytz.timezone('Europe/Berlin'))
        tomorrow = today + datetime.timedelta(days=1)
        day_after_tomorrow = today + datetime.timedelta(days=2)

        if today.weekday() < 4:  # Monday - Thursday
            new_pollen = {
                today.strftime('%Y-%m-%d'): build_values(allergen['today']),
                tomorrow.strftime('%Y-%m-%d'): build_values(allergen['tomorrow'])
            }
        elif today.weekday() == 4:  # Friday
            new_pollen = {
                today.strftime('%Y-%m-%d'): build_values(allergen['today']),
                tomorrow.strftime('%Y-%m-%d'): build_values(allergen['tomorrow'])
            }
            if allergen['dayafter_to'] != '-1':
                new_pollen[day_after_tomorrow.strftime('%Y-%m-%d')] = \
                    build_values(allergen['dayafter_to'])
        elif today.weekday() == 5:  # Saturday
            new_pollen = {
                today.strftime('%Y-%m-%d'): build_values(allergen['tomorrow']),
            }
            if allergen['dayafter_to'] != '-1':
                new_pollen[day_after_tomorrow.strftime('%Y-%m-%d')] = \
                    build_values(allergen['dayafter_to'])
        elif today.weekday() == 6:  # Sunday
            new_pollen = {}
            if allergen['dayafter_to'] != '-1':
                new_pollen[day_after_tomorrow.strftime('%Y-%m-%d')] = \
                    build_values(allergen['dayafter_to'])
        return new_pollen

    async def update(self) -> None:
        """Update all pollen data."""
        data = await get_data_async(DWD_URL)
        self.last_update = datetime.datetime.strptime(
            data['last_update'], '%Y-%m-%d %H:%M Uhr')
        self.next_update = datetime.datetime.strptime(
            data['next_update'], '%Y-%m-%d %H:%M Uhr')
        self.legend = build_legend(data['legend'])

        for region in data['content']:
            new_region = {
                'region_id': region['region_id'],
                'region_name': region['region_name'],
                'partregion_id': region['partregion_id'],
                'partregion_name': region['partregion_name'],
                'last_update': self.last_update,
                'next_update': self.next_update,
                'pollen': {}
            }
            for allergen, pollen in region['Pollen'].items():
                new_pollen = await self.build_pollen(pollen)
                new_region['pollen'][allergen] = new_pollen
            self.data[f"{region['region_id']}-{region['partregion_id']}"] = new_region

    async def get_pollen(self, region_id: Union[int, str],
                         partregion_id: Union[int, str]) -> Dict[str, Any]:
        """
        Get the pollen load of the requested region and partregion.

        Args:
            region_id: API ID of the region.
            partregion_id: API ID of the partregion.

        Returns:
            A dictionary with all pollen information of the requested (part)region.

        Raises:
            KeyError: If the region is not found.
        """
        # Wait for initialization if it's still running
        if self._initialization_task is not None:
            await self._initialization_task
            self._initialization_task = None

        key = f'{region_id}-{partregion_id}'
        if key not in self.data:
            # Try to update once if the key is not found
            await self.update()

        return self.data[key]

    async def get_region_names(self) -> List[Tuple[int, int, str, str]]:
        """
        Get a list of available regions and their IDs.

        Returns:
            List of tuples with (region_id, partregion_id, region_name, partregion_name)
        """
        # Wait for initialization if it's still running
        if self._initialization_task is not None:
            await self._initialization_task
            self._initialization_task = None

        result = []
        for _, region in self.data.items():
            result.append((
                region['region_id'],
                region['partregion_id'],
                region['region_name'],
                region['partregion_name']
            ))
        return sorted(result)

    async def get_allergen_names(self) -> List[str]:
        """
        Get a list of all allergen names in the data.

        Returns:
            List of allergen names.
        """
        # Wait for initialization if it's still running
        if self._initialization_task is not None:
            await self._initialization_task
            self._initialization_task = None

        allergens = set()
        for _, region in self.data.items():
            for allergen in region['pollen'].keys():
                allergens.add(allergen)
        return sorted(list(allergens))

    async def get_allergen_for_region(
        self,
        region_id: Union[int, str],
        partregion_id: Union[int, str],
        allergen_name: str
    ) -> Dict[str, Any]:
        """
        Get a specific allergen's data for a region.

        Args:
            region_id: API ID of the region.
            partregion_id: API ID of the partregion.
            allergen_name: Name of the allergen.

        Returns:
            Dictionary with the allergen data.

        Raises:
            KeyError: If the region or allergen is not found.
        """
        region_data = await self.get_pollen(region_id, partregion_id)
        return region_data['pollen'][allergen_name]
