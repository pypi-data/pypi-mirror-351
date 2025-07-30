import datetime
import typing as t

import httpx
import pydantic as p

from .errors import CheckRegistrationError, MultipleRecordsFoundError
from .tool import (
    CheckRegistrationDetails,
    CheckRegistrationResult,
    CheckRegistrationTool,
    SupportedFeatures,
)

# ------------------------------------------------------------------------
# Wisconsin API Data Structures
# ------------------------------------------------------------------------


class SearchResponseVoter(p.BaseModel, frozen=True):
    """An individual voter data structure for the search response."""

    voter_id: str = p.Field(alias="voterRegNumber")
    voter_status: str = p.Field(alias="voterStatusName")
    registration_date: datetime.date = p.Field(alias="registrationDate")

    @p.field_validator("voter_status", mode="after")
    def validate_status(cls, value: str) -> str:
        """Validate the voter status."""
        return value.lower()

    @p.field_validator("registration_date", mode="before")
    def validate_dt(cls, value: str) -> datetime.date:
        """Validate the registration date."""
        return datetime.datetime.strptime(value, "%m/%d/%Y").date()


class SearchResponseVoters(p.BaseModel, frozen=True):
    """The voters data structure for the search response."""

    values: t.Sequence[SearchResponseVoter] = p.Field(alias="$values")


class SearchResponseData(p.BaseModel, frozen=True):
    """The inner data structure for the search response."""

    voters: SearchResponseVoters


class SearchResponse(p.BaseModel, frozen=True):
    """The response structure for the search API."""

    data: SearchResponseData = p.Field(alias="Data")
    success: bool = p.Field(alias="Success")
    error_message: str | None = p.Field(alias="ErrorMessage")
    warning_message: str | None = p.Field(alias="WarningMessage")


# ------------------------------------------------------------------------
# CheckRegistrationTool implementation for WI
# ------------------------------------------------------------------------


class WisconsinCheckRegistrationTool(CheckRegistrationTool):
    """A tool for checking voter registration in Wisconsin."""

    SEARCH_URL: t.ClassVar[str] = (
        "https://myvote.wi.gov/DesktopModules/GabMyVoteModules/api/voter/search"
    )

    state: t.ClassVar[str] = "WI"
    features: t.ClassVar[SupportedFeatures] = SupportedFeatures(details=True)

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
                self.SEARCH_URL,
                json={
                    "firstName": first_name,
                    "lastName": last_name,
                    "birthDate": birth_date.strftime("%m/%d/%Y"),
                },
            )
            request.raise_for_status()
        except httpx.HTTPError as e:
            raise CheckRegistrationError("Failed to check voter registration.") from e

        try:
            response = SearchResponse.model_validate(request.json())
        except Exception as e:
            raise CheckRegistrationError("Failed to parse response.") from e

        if not response.success:
            raise CheckRegistrationError(response.error_message or "Unknown error.")

        if not response.data.voters.values:
            return CheckRegistrationResult(registered=False)

        if len(list(response.data.voters.values)) > 1:
            raise MultipleRecordsFoundError()

        if not details:
            return CheckRegistrationResult(registered=True)

        voter = response.data.voters.values[0]
        return CheckRegistrationResult(
            registered=True,
            details=CheckRegistrationDetails(
                state_id=voter.voter_id,
                registration_date=voter.registration_date,
                status=voter.voter_status,
            ),
        )
