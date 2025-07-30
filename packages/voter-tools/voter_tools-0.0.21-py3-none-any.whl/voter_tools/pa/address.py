import re

_UNIT_TYPES = {
    "apartment": "APT",
    "basement": "BSM",
    "box #": "BOX",
    "building": "BLD",
    "department": "DEP",
    "floor": "FL",
    "front": "FRN",
    "hanger": "HNG",
    "lobby": "LBB",
    "lot": "LOT",
    "lower": "LOW",
    "office": "OFC",
    "penthouse": "PH",
    "pier": "PIE",
    "poll": "POL",
    "rear": "REA",
    "room": "RM",
    "side": "SID",
    "slip": "SLI",
    "space": "SPC",
    "stop": "STO",
    "suite": "STE",
    "trailer": "TRLR",
    "unit": "UNI",
    "upper": "UPP",
    "cabin": "CBN",
    "hub": "HUB",
    "student mailing center": "SMC",
    "townhouse": "TH",
}


_RE_BARE_NUMBER = re.compile(r"^#?(\d+)$")
_RE_BARE_UNIT_NUMBER = re.compile(r"^(\w+)\.? (\d+)$")
_RE_TRAILING_NUMBER = re.compile(r"^(.*) #(\d+)$")
_RE_TRAILING_UNIT_NUMBER = re.compile(r"^(.*) (\w+)\.? (\d+)$")


def get_unit_type_number(
    address1: str, address2: str | None
) -> tuple[str | None, str | None]:
    """
    Normalize a provided potentially multi-line address.

    Specifically, attempt to identify a unit type/number from the address,
    if a known type is found.

    If found, return a tuple of the unit type and number. Otherwise, return
    a tuple of None.
    """
    return None, None
