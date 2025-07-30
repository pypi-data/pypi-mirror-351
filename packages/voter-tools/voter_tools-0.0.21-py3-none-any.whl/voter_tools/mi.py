import datetime
import typing as t

import httpx
from bs4 import BeautifulSoup

from .errors import CheckRegistrationError, MultipleRecordsFoundError
from .soup_utils import find_attr_value
from .tool import (
    CheckRegistrationDetails,
    CheckRegistrationResult,
    CheckRegistrationTool,
    SupportedFeatures,
)

# ------------------------------------------------------------------------
# CheckRegistrationTool implementation for MI
# ------------------------------------------------------------------------


class MichiganCheckRegistrationTool(CheckRegistrationTool):
    """A tool for checking voter registration in Michigan."""

    state: t.ClassVar[str] = "MI"
    features: t.ClassVar[SupportedFeatures] = SupportedFeatures(details=True)

    SEARCH_BY_NAME_URL: t.ClassVar[str] = (
        "https://mvic.sos.state.mi.us/Voter/SearchByName"
    )

    def check_registration(
        self,
        first_name: str,
        last_name: str,
        zipcode: str,
        birth_date: datetime.date,
        details: bool = False,
    ) -> CheckRegistrationResult:
        """Check if a voter is registered in Michigan."""
        try:
            request = httpx.post(
                self.SEARCH_BY_NAME_URL,
                data={
                    "FirstName": first_name,
                    "LastName": last_name,
                    "NameBirthMonth": birth_date.strftime("%m"),
                    "NameBirthYear": birth_date.strftime("%Y"),
                    "ZipCode": zipcode,
                    "Dln": "",
                    "DlnBirthMonth": "",
                    "DlnBirthYear": "",
                    "DpaID": 0,
                    "Months": None,
                    "VoterNotFound": False,
                    "TransitionVoter": False,
                },
            )
            request.raise_for_status()
        except httpx.HTTPError as e:
            raise CheckRegistrationError("Failed to check voter registration.") from e

        # Parse the response
        soup = BeautifulSoup(request.text, "html.parser")

        # See if there are multiple voter records
        multiple_records_val = find_attr_value(
            soup, "input", "value", id="hfmultiplevoterrecords"
        )
        if (multiple_records_val or "").lower() == "true":
            raise MultipleRecordsFoundError()

        # Check if the voter was found
        voter_found_val = find_attr_value(soup, "input", "value", id="hfnotfound")
        if (voter_found_val or "").lower() == "true":
            return CheckRegistrationResult(registered=False)

        # Don't want details? We're done here.
        if not details:
            return CheckRegistrationResult(registered=True)

        # Get the registration details
        dpa_id_val = find_attr_value(soup, "input", "value", id="Voter_0__DpaID")
        if not dpa_id_val:
            raise CheckRegistrationError("Failed to find dpa id.")
        registration_date_val = find_attr_value(
            soup, "input", "value", id="Voter_0__EffectiveRegistrationDate"
        )
        if not registration_date_val:
            raise CheckRegistrationError("Failed to find registration date.")
        try:
            registration_date = datetime.datetime.strptime(
                registration_date_val.split(" ")[0], "%m/%d/%Y"
            ).date()
        except ValueError as e:
            raise CheckRegistrationError("Failed to parse registration date.") from e

        return CheckRegistrationResult(
            registered=True,
            details=CheckRegistrationDetails(
                state_id=dpa_id_val,
                registration_date=registration_date,
                status="active",  # TODO: are there alternatives?
            ),
        )
