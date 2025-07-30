"""
Main API client implementation for DWD pollen data.
"""

import datetime
import logging
from typing import Dict, Any, Union, List, Optional, Tuple
import json
import os
import time
from functools import lru_cache
import pytz
import requests

from .exceptions import DwdPollenError

LOGGER = logging.getLogger(__name__)

DWD_URL = 'https://opendata.dwd.de/climate_environment/health/alerts/s31fg.json'
CACHE_DURATION = 3600  # 1 hour in seconds


def get_data(url: str, timeout: int = 30, retry_count: int = 3,
             retry_delay: int = 2) -> Dict[str, Any]:
    """
    Fetch the data via HTTP and return it as a dictionary.

    Args:
        url: The API URL.
        timeout: Request timeout in seconds.
        retry_count: Number of retries on failure.
        retry_delay: Delay between retries in seconds.

    Returns:
        The API response as a dictionary.

    Raises:
        DwdPollenError: If the request fails after retries.
    """
    attempt = 0
    last_exception = None

    while attempt < retry_count:
        try:
            response = requests.get(url, timeout=timeout)
            response.raise_for_status()
            return response.json()
        except (requests.RequestException, ValueError, KeyError) as e:
            LOGGER.warning("Request attempt %d failed: %s", attempt+1, str(e))
            last_exception = e
            attempt += 1
            if attempt < retry_count:
                time.sleep(retry_delay)

    msg = f"Failed to fetch data after {retry_count} attempts"
    if last_exception:
        msg += f": {str(last_exception)}"
    raise DwdPollenError(msg)


def build_legend(legend: Dict[str, str]) -> Dict[str, str]:
    """
    Convert the API legend format to a more usable dictionary.

    Args:
        legend: The legend dictionary from the API.

    Returns:
        A dictionary mapping pollen values to their descriptions.
    """
    new_legend = {}
    for key, value in legend.items():
        if '_desc' not in key:
            new_legend[value] = legend[f'{key}_desc']
    return new_legend


class DwdPollenApi:
    """API client object to get the current pollen load in Germany."""

    def __init__(self, cache_duration: int = CACHE_DURATION, auto_update: bool = True):
        """
        Initialize the DWD pollen API client.

        Args:
            cache_duration: How long to cache data in seconds (default: 1 hour).
            auto_update: Whether to update data on initialization.
        """
        self.last_update: Optional[datetime.datetime] = None
        self.next_update: Optional[datetime.datetime] = None
        self.content = None
        self.data: Dict[str, Dict[str, Any]] = {}
        self.legend: Optional[Dict[str, str]] = None
        self.cache_duration = cache_duration

        if auto_update:
            self.update()

    def build_pollen(self, allergen: Dict[str, str]) -> Dict[str, Dict[str, Any]]:
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

    @lru_cache(maxsize=8)
    def get_cache_file_path(self) -> str:
        """Get the path to the cache file."""
        cache_dir = os.path.join(os.path.expanduser("~"), ".cache", "dwdpollen")
        os.makedirs(cache_dir, exist_ok=True)
        return os.path.join(cache_dir, "pollen_data.json")

    def load_from_cache(self) -> bool:
        """
        Try to load data from the cache file.

        Returns:
            True if data was successfully loaded from cache, False otherwise.
        """
        try:
            cache_file = self.get_cache_file_path()
            if not os.path.exists(cache_file):
                return False

            file_mod_time = os.path.getmtime(cache_file)
            if time.time() - file_mod_time > self.cache_duration:
                LOGGER.debug("Cache expired")
                return False

            with open(cache_file, 'r', encoding='utf-8') as f:
                cache_data = json.load(f)

            self.data = cache_data.get('data', {})
            self.legend = cache_data.get('legend', {})

            # Convert timestamp strings back to datetime objects
            last_update_str = cache_data.get('last_update')
            next_update_str = cache_data.get('next_update')

            if last_update_str:
                self.last_update = datetime.datetime.fromisoformat(last_update_str)
            if next_update_str:
                self.next_update = datetime.datetime.fromisoformat(next_update_str)

            LOGGER.debug("Loaded data from cache, last update: %s", self.last_update)
            return bool(self.data)
        except (IOError, json.JSONDecodeError) as e:
            LOGGER.warning("Failed to load from cache: %s", e)
            return False

    def save_to_cache(self) -> None:
        """Save the current data to the cache file."""
        try:
            cache_file = self.get_cache_file_path()

            cache_data = {
                'data': self.data,
                'legend': self.legend,
                'last_update': self.last_update.isoformat() if self.last_update else None,
                'next_update': self.next_update.isoformat() if self.next_update else None,
            }

            with open(cache_file, 'w', encoding='utf-8') as f:
                # Import DateTimeEncoder from cli module to ensure consistent datetime serialization
                from .cli import DateTimeEncoder
                json.dump(cache_data, f, ensure_ascii=False, indent=2, cls=DateTimeEncoder)

            LOGGER.debug("Saved data to cache: %s", cache_file)
        except IOError as e:
            LOGGER.warning("Failed to save to cache: %s", e)

    def update(self, force: bool = False) -> bool:
        """
        Update all pollen data.

        Args:
            force: If True, bypass the cache and force update from the API.

        Returns:
            True if update was successful, False otherwise.
        """
        if not force and self.load_from_cache():
            return True

        try:
            data = get_data(DWD_URL)
            self.last_update = datetime.datetime.strptime(
                data['last_update'], '%Y-%m-%d %H:%M Uhr')
            self.next_update = datetime.datetime.strptime(
                data['next_update'], '%Y-%m-%d %H:%M Uhr')
            self.legend = build_legend(data['legend'])

            self.data = {}
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
                    new_pollen = self.build_pollen(pollen)
                    new_region['pollen'][allergen] = new_pollen
                self.data[f"{region['region_id']}-{region['partregion_id']}"] = new_region

            self.save_to_cache()
            return True
        except (requests.RequestException, ValueError, KeyError, OSError) as e:
            LOGGER.error("Failed to update pollen data: %s", e)
            return False

    def get_pollen(
        self,
        region_id: Union[int, str],
        partregion_id: Union[int, str]
    ) -> Dict[str, Any]:
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
        key = f'{region_id}-{partregion_id}'
        if key not in self.data:
            # Try to update once if the key is not found
            self.update(force=True)

        return self.data[key]

    def get_region_names(self) -> List[Tuple[int, int, str, str]]:
        """
        Get a list of available regions and their IDs.

        Returns:
            List of tuples with (region_id, partregion_id, region_name, partregion_name)
        """
        result = []
        for _, region in self.data.items():
            result.append((
                region['region_id'],
                region['partregion_id'],
                region['region_name'],
                region['partregion_name']
            ))
        return sorted(result)

    def get_allergen_names(self) -> List[str]:
        """
        Get a list of all allergen names in the data.

        Returns:
            List of allergen names.
        """
        allergens = set()
        for _, region in self.data.items():
            for allergen in region['pollen'].keys():
                allergens.add(allergen)
        return sorted(list(allergens))

    def get_allergen_for_region(
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
        region_data = self.get_pollen(region_id, partregion_id)
        return region_data['pollen'][allergen_name]

    def get_forecast_summary(
        self,
        region_id: Union[int, str],
        partregion_id: Union[int, str]
    ) -> Dict[str, Dict[str, str]]:
        """
        Get a simplified forecast summary for a region.

        Args:
            region_id: API ID of the region.
            partregion_id: API ID of the partregion.

        Returns:
            Dictionary with date keys and allergen summaries.
        """
        region_data = self.get_pollen(region_id, partregion_id)
        dates = set()

        # Collect all available dates
        for _, allergen_data in region_data['pollen'].items():
            for date in allergen_data.keys():
                dates.add(date)

        result = {}
        for date in sorted(dates):
            date_summary = {}
            for allergen, allergen_data in region_data['pollen'].items():
                if date in allergen_data:
                    date_summary[allergen] = allergen_data[date]['human']
            result[date] = date_summary

        return result
