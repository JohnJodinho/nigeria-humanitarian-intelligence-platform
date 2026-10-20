import pandas as pd
from shapely.geometry import Point

from src.geospatial.spatial_processor import SpatialProcessor


def test_find_admin1_match_applies_fct_alias():
    boundaries = pd.DataFrame(
        [{"shapeName": "Abuja", "geometry": Point(7.5, 9.0)}]
    )

    match = SpatialProcessor._find_admin1_match(
        "Federal Capital Territory", boundaries, {"federalcapitalterritory": "abuja", "fct": "abuja"}
    )

    assert match["shapeName"] == "Abuja"


def test_find_admin2_match_uses_fuzzy_name_when_exact_match_is_missing():
    boundaries = pd.DataFrame(
        [{"shapeName": "Maiduguri", "geometry": Point(13.1, 11.8)}]
    )

    match = SpatialProcessor._find_admin2_match(
        "Maiduguri LGA", boundaries, ["Maiduguri"]
    )

    assert match["shapeName"] == "Maiduguri"
