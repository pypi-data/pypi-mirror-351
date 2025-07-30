"""
Constants and helper data for the dwdpollen package.
"""

from typing import Dict, List, Tuple

# Map of regions and partregions
REGIONS: Dict[int, Tuple[str, Dict[int, str]]] = {
    10: ("Schleswig-Holstein und Hamburg", {
        11: "Inseln und Marschen",
        12: "Geest, Schleswig-Holstein und Hamburg"
    }),
    20: ("Mecklenburg-Vorpommern", {
        -1: ""
    }),
    30: ("Niedersachsen und Bremen", {
        31: "Westl. Niedersachsen/Bremen",
        32: "Östl. Niedersachsen"
    }),
    40: ("Nordrhein-Westfalen", {
        41: "Rhein.-Westfäl. Tiefland",
        42: "Ostwestfalen",
        43: "Mittelgebirge NRW"
    }),
    50: ("Brandenburg und Berlin", {
        -1: ""
    }),
    60: ("Sachsen-Anhalt", {
        61: "Tiefland Sachsen-Anhalt",
        62: "Harz"
    }),
    70: ("Thüringen", {
        71: "Tiefland Thüringen",
        72: "Mittelgebirge Thüringen"
    }),
    80: ("Sachsen", {
        81: "Tiefland Sachsen",
        82: "Mittelgebirge Sachsen"
    }),
    90: ("Hessen", {
        91: "Nordhessen und hess. Mittelgebirge",
        92: "Rhein-Main"
    }),
    100: ("Rheinland-Pfalz und Saarland", {
        101: "Rhein, Pfalz, Nahe und Mosel",
        102: "Mittelgebirgsbereich Rheinland-Pfalz",
        103: "Saarland"
    }),
    110: ("Baden-Württemberg", {
        111: "Oberrhein und unteres Neckartal",
        112: "Hohenlohe/mittlerer Neckar/Oberschwaben",
        113: "Mittelgebirge Baden-Württemberg"
    }),
    120: ("Bayern", {
        121: "Allgäu/Oberbayern/Bay. Wald",
        122: "Donauniederungen",
        123: "Bayern n. der Donau, o. Bayr. Wald, o. Mainfranken",
        124: "Mainfranken"
    })
}

# List of common allergens
ALLERGENS: List[str] = [
    "Ambrosia",
    "Beifuss",
    "Birke",
    "Erle",
    "Esche",
    "Gräser",
    "Hasel",
    "Roggen"
]

# Mapping of allergen names (as used in the API) to their botanical names
ALLERGEN_BOTANICAL_NAMES: Dict[str, str] = {
    "Ambrosia": "Ambrosia artemisiifolia",
    "Beifuss": "Artemisia vulgaris",
    "Birke": "Betula",
    "Erle": "Alnus",
    "Esche": "Fraxinus excelsior",
    "Gräser": "Poaceae",
    "Hasel": "Corylus",
    "Roggen": "Secale cereale"
}

# Seasons for allergens in Germany (month ranges)
ALLERGEN_SEASONS: Dict[str, List[int]] = {
    "Ambrosia": [7, 8, 9, 10],        # July-October
    "Beifuss": [7, 8, 9],             # July-September
    "Birke": [3, 4, 5],               # March-May
    "Erle": [1, 2, 3, 4],             # January-April
    "Esche": [3, 4, 5],               # March-May
    "Gräser": [5, 6, 7, 8, 9],        # May-September
    "Hasel": [1, 2, 3, 4],            # January-April
    "Roggen": [5, 6, 7]               # May-July
}
