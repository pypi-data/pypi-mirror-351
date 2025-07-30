"""Module for looking up zip codes, states, and counties."""

import csv
import pathlib

_ZIP_TO_STATE: dict[str, str] = {}
_ZIP_TO_COUNTY: dict[str, str] = {}

_ZIP_PATH = pathlib.Path(__file__).parent / "zipcodes.us.csv"

_ZIPCODE_COLUMN = 1
_STATE_COLUMN = 4
_COUNTY_COLUMN = 5


def _load_zipcodes():
    global _ZIP_TO_STATE, _ZIP_TO_COUNTY
    if not _ZIP_TO_STATE or not _ZIP_TO_COUNTY:
        with open(_ZIP_PATH, "r") as f:
            reader = csv.reader(f)
            next(reader)
            for row in reader:
                _ZIP_TO_STATE[row[_ZIPCODE_COLUMN]] = row[_STATE_COLUMN]
                _ZIP_TO_COUNTY[row[_ZIPCODE_COLUMN]] = row[_COUNTY_COLUMN]


def _get_zip_to_state() -> dict[str, str]:
    """Return a dictionary mapping zip codes to state abbreviations."""
    _load_zipcodes()
    return _ZIP_TO_STATE


def _get_zip_to_county() -> dict[str, str]:
    """Return a dictionary mapping zip codes to county names."""
    _load_zipcodes()
    return _ZIP_TO_COUNTY


def get_state(zipcode: str) -> str | None:
    """Return the state abbreviation for a given zip code."""
    return _get_zip_to_state().get(zipcode)


def get_county(zipcode: str) -> str | None:
    """Return the county name for a given zip code."""
    return _get_zip_to_county().get(zipcode)
