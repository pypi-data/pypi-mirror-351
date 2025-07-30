"""
dwdpollen - API client for the "Deutscher Wetterdienst" to get the current pollen load in Germany
Copyright (C) 2019-2025  Sascha Triller

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""

import logging

# Import submodules
from .client import DwdPollenApi
from .async_client import AsyncDwdPollenApi
from .exceptions import DwdPollenError
from .constants import REGIONS, ALLERGENS

# Setup logging
logging.basicConfig(level=logging.ERROR)
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.DEBUG)

__version__ = '0.4.1'
__all__ = ['DwdPollenApi', 'AsyncDwdPollenApi', 'DwdPollenError', 'REGIONS', 'ALLERGENS']
