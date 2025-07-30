import datetime
import typing as t
from abc import ABC, abstractmethod

import pydantic as p


class CheckRegistrationDetails(p.BaseModel, frozen=True):
    """Details about a voter's registration status."""

    state_id: str
    """The voter's state ID number."""

    registration_date: datetime.date
    """The date the voter registered."""

    status: str
    """The voter's registration status (active, inactive, suspended, etc.)."""


class CheckRegistrationResult(p.BaseModel, frozen=True):
    """The result of a voter registration check."""

    registered: bool
    """True if the voter is or was at one point registered to vote."""

    details: CheckRegistrationDetails | None = None
    """Details about the voter's registration, if available."""


class SupportedFeatures(p.BaseModel, frozen=True):
    """Features supported by a voter tool."""

    details: bool
    """True if the tool provides detailed registration information."""


class CheckRegistrationTool(ABC):
    """Base class for working with voter registration data."""

    state: t.ClassVar[str]
    """The two-letter state abbreviation for this tool."""

    features: t.ClassVar[SupportedFeatures]
    """Features supported by this tool."""

    @abstractmethod
    def check_registration(
        self,
        first_name: str,
        last_name: str,
        zipcode: str,
        birth_date: datetime.date,
        details: bool = False,
    ) -> CheckRegistrationResult:
        """
        Check whether a voter is registered to vote.

        If details are requested and available, include them in the result.
        (Not all states provide detailed registration information.)

        Raises a CheckRegistrationError if there is an unexpected failure.
        """
        ...


# TODO: as we support online voter registration in more states, consider if
# there's anything like a unified interface to build for them. For now,
# let's not bother.
