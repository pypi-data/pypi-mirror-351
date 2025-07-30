"""
CLI interface for the bloomtracker package.
JSON-only CLI tool for getting pollen data.
"""

import argparse
import json
import sys
import textwrap
import datetime
from typing import Dict, Any, Optional, List, TextIO

from .client import DwdPollenApi
from .constants import REGIONS


# Custom JSON encoder to handle datetime objects
class DateTimeEncoder(json.JSONEncoder):
    """Custom JSON encoder to handle datetime objects."""
    def default(self, o):
        if isinstance(o, (datetime.datetime, datetime.date)):
            return o.isoformat()
        return super().default(o)


def convert_datetime_recursive(obj):
    """Recursively convert datetime objects to ISO format strings."""
    if isinstance(obj, datetime.datetime):
        return obj.isoformat()
    if isinstance(obj, dict):
        return {key: convert_datetime_recursive(value) for key, value in obj.items()}
    if isinstance(obj, list):
        return [convert_datetime_recursive(item) for item in obj]
    return obj

def get_pollen_data(api: DwdPollenApi, region_id: int, partregion_id: int) -> Dict[str, Any]:
    """Get pollen data for a region and return it in a serializable format."""
    try:
        data = api.get_pollen(region_id, partregion_id)

        # Recursively convert all datetime objects to strings for JSON serialization
        serializable_data = convert_datetime_recursive(data)

        return serializable_data
    except KeyError:
        return {
            "error": f"Region {region_id}-{partregion_id} not found.",
            "status": "error",
            "code": 404
        }


def print_json(
    api: DwdPollenApi,
    region_id: int,
    partregion_id: int,
    output_file: Optional[TextIO] = None
) -> None:
    """Print pollen data as JSON."""
    data = get_pollen_data(api, region_id, partregion_id)

    # Use global DateTimeEncoder class for consistent datetime serialization
    output = json.dumps(data, ensure_ascii=False, indent=2, cls=DateTimeEncoder)

    if output_file:
        output_file.write(output)
    else:
        print(output)


def get_regions_data() -> Dict[str, Any]:
    """Get information about all available regions in JSON format."""
    regions_data: Dict[str, List[Dict[str, Any]]] = {
        "regions": []
    }

    for region_id, (region_name, partregions) in REGIONS.items():
        # pylint: disable-next=no-member
        for partregion_id, partregion_name in partregions.items():
            full_name = region_name
            if partregion_name:
                full_name += f" - {partregion_name}"

            regions_data["regions"].append({
                "region_id": region_id,
                "partregion_id": partregion_id,
                "name": full_name
            })

    return regions_data


def main() -> None:
    """Main entry point for the CLI."""
    parser = argparse.ArgumentParser(
        description="Get pollen load data from the Deutscher Wetterdienst (JSON output only)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=textwrap.dedent("""
        Examples:
          bloomtracker -r 10 -p 11  # Get data for Schleswig-Holstein (Inseln und Marschen)
          bloomtracker --list       # List all available regions
          bloomtracker -r 50 -o data.json  # Save data for Berlin/Brandenburg to JSON file
        """)
    )

    parser.add_argument(
        "-r", "--region",
        type=int,
        help="Region ID"
    )

    parser.add_argument(
        "-p", "--partregion",
        type=int,
        default=-1,
        help="Partregion ID (default: -1)"
    )

    parser.add_argument(
        "-o", "--output",
        type=argparse.FileType('w'),
        help="Output file (default: stdout)"
    )

    parser.add_argument(
        "--no-cache",
        action="store_true",
        help="Bypass cache and force data update"
    )

    parser.add_argument(
        "-l", "--list",
        action="store_true",
        help="List all available regions"
    )

    args = parser.parse_args()

    api = DwdPollenApi()

    if args.no_cache:
        api.update(force=True)

    if args.list:
        # Output the list of regions as JSON
        regions_data = get_regions_data()
        print(json.dumps(regions_data, ensure_ascii=False, indent=2, cls=DateTimeEncoder))
        return

    if args.region is None:
        # Output help as JSON
        help_data = {
            "status": "error",
            "error": "Missing required argument: region",
            "help": "Run with --help for usage information"
        }
        print(json.dumps(help_data, ensure_ascii=False, indent=2, cls=DateTimeEncoder))
        sys.exit(1)

    try:
        # Always print JSON
        print_json(api, args.region, args.partregion, args.output)
    except (KeyError, ValueError) as e:
        error_data = {
            "status": "error",
            "error": str(e),
            "code": 500
        }
        print(json.dumps(error_data, ensure_ascii=False, indent=2, cls=DateTimeEncoder))
        sys.exit(1)


if __name__ == "__main__":
    main()
