"""
Visualization utilities for the dwdpollen package.
"""

from typing import Dict, Any, Optional
from io import BytesIO


def generate_chart(
    data: Dict[str, Any],
    *,
    allergen_name: Optional[str] = None,
    date_str: Optional[str] = None,
    title: Optional[str] = None,
    output_path: Optional[str] = None
) -> Optional[BytesIO]:
    """
    Generate a chart for pollen data.
    
    In this JSON-only version, the visualization is a stub.
    
    Args:
        data: Pollen data for a region from DwdPollenApi.get_pollen()
        allergen_name: If provided, show this specific allergen over time
        date_str: If provided, show all allergens for this specific date
        title: Custom chart title (auto-generated if None)
        output_path: If provided, save the chart to this file path
    
    Returns:
        A BytesIO object containing the chart image data if output_path is None,
        otherwise None (the chart is saved to file)
    """
    # This is a stub implementation for the JSON-only version
    # Silence unused parameter warnings - this is a stub function
    _ = data, allergen_name, date_str, title

    if output_path:
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write("This is a stub visualization in the JSON-only version")
        return None

    # If no output path, return an empty BytesIO object
    return BytesIO(b"Stub visualization")
