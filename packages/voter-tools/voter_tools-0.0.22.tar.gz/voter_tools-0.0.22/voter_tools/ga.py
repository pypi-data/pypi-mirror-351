import datetime
import json
import sys
import typing as t
from abc import abstractmethod

import httpx
import pydantic as p

from .errors import CheckRegistrationError
from .tool import (
    CheckRegistrationDetails,
    CheckRegistrationResult,
    CheckRegistrationTool,
    SupportedFeatures,
)
from .zipcodes import get_county

# ------------------------------------------------------------------------
# Utilities for issuing requests to Georgia's check voter registration site
# ------------------------------------------------------------------------


class ActionResult(p.BaseModel, frozen=True):
    """Base class for results of actions on the GA voter reg site."""

    pass


class Action(p.BaseModel, frozen=True):
    """
    A single action taken on the GA voter reg site.

    A request to the site is composed of one or more actions.

    Each action has an identifier that is used to match it with its
    response data.
    """

    method: t.ClassVar[str]
    class_name: t.ClassVar[str] = "vr_MvpDashboardController"
    result_class: t.ClassVar[type[ActionResult]]

    cacheable: t.ClassVar[bool | None] = False
    is_continuation: t.ClassVar[bool | None] = False

    @abstractmethod
    def params(self) -> dict:
        """Return params used as part of the action data."""
        ...

    def to_data(self) -> dict:
        """Return data used as part of the larger request structure."""
        return {
            "id": str(self.__class__.__name__),
            "descriptor": "aura://ApexActionController/ACTION$execute",
            "callingDescriptor": "UNKNOWN",
            "params": {
                "namespace": "",
                "classname": self.class_name,
                "method": self.method,
                "params": self.params(),
                **({"cacheable": self.cacheable} if self.cacheable is not None else {}),
                **(
                    {"isContinuation": self.is_continuation}
                    if self.is_continuation is not None
                    else {}
                ),
            },
        }


class CheckContactExistMessage(p.BaseModel, frozen=True):
    """Message data returned from checking if a contact exists."""

    has_data: bool = p.Field(alias="hasData")
    is_multiple: bool = p.Field(alias="isMultiple")
    contact_id: str = p.Field(alias="id")
    instance_of: str = p.Field(alias="instanceOf")


class CheckContactExistResult(ActionResult, frozen=True):
    """The result of checking if a contact exists in the GA voter reg system."""

    success: bool
    error: bool
    message: CheckContactExistMessage


class CheckContactExistAction(Action, frozen=True):
    """An action to check if a contact exists in the GA voter reg system."""

    first_name: str
    last_name: str
    zipcode: str
    birth_date: datetime.date

    result_class: t.ClassVar[type[ActionResult]] = CheckContactExistResult
    class_name: t.ClassVar[str] = "vr_MvpLandingPageController"
    method: t.ClassVar[str] = "checkContactExist"
    cacheable: t.ClassVar[bool | None] = None
    is_continuation: t.ClassVar[bool | None] = None

    def params(self) -> dict:
        """Return params used as part of the action data."""
        county_name = get_county(self.zipcode)
        if county_name is None:
            raise ValueError(f"Unknown county for zipcode: {self.zipcode}")
        county_name = county_name.upper()
        return {
            "requestMap": {
                "firstInitial": self.first_name.upper()[0],
                "lastName": self.last_name.upper(),
                "county": county_name,
                "georgiaId": "",
                "recaptchaResponse": '""',
                "version": "",
                "birthDate": self.birth_date.strftime("%Y-%m-%d"),
                "ssn": None,
            },
        }


class ContactIDAction(Action, frozen=True):
    """A base action for actions that require a contact ID."""

    contact_id: str

    def params(self) -> dict:
        """Return params used as part of the action data."""
        return {"contactId": self.contact_id}


class GetCurrentContactInformationResult(ActionResult, frozen=True):
    """The result of getting the current contact information for a user."""

    alternate_id: str = p.Field(alias="contactId")
    full_name: str = p.Field(alias="name")  # ALL CAPS


class GetCurrentContactInformationAction(ContactIDAction, frozen=True):
    """An action to get the current contact information for a user."""

    method: t.ClassVar[str] = "getCurrentContactInformation"
    result_class: t.ClassVar[type[ActionResult]] = GetCurrentContactInformationResult


class GetPersonalInformationResult(ActionResult, frozen=True):
    """The result of getting the personal information for a user."""

    # There is a *ton* of information returned by this action. Pydantic
    # happily ignores undeclared fields, so we can just declare the ones
    # we care about for now. But there's a lot!

    registration_date: datetime.date = p.Field(alias="createdDate")

    @p.field_validator("registration_date", mode="before")
    def validate_dt_or_none(cls, value: str) -> datetime.date:
        """Validate the registration date."""
        return datetime.datetime.strptime(value, "%Y-%m-%d").date()

    email: str | None = None
    first_name: str = p.Field(alias="firstName")
    last_name: str = p.Field(alias="lastName")
    middle_name: str | None = p.Field(alias="middleName", default=None)
    gender: str
    has_maiden_name: bool = p.Field(alias="hasMaidenName")
    has_middle_name: bool = p.Field(alias="hasMiddleName")
    phone: str | None = None

    status: str  # Like "Active"

    voter_reg_number: str = p.Field(alias="voterRegistrationNumber")

    @property
    def is_active(self) -> bool:
        """Return whether the registration is active."""
        return self.status.lower() == "active"


class GetPersonalInformationAction(ContactIDAction, frozen=True):
    """An action to get the personal information for a user."""

    result_class: t.ClassVar[type[ActionResult]] = GetPersonalInformationResult
    method: t.ClassVar[str] = "getPersonalInformation"

    def params(self) -> dict:
        """Return params used as part of the action data."""
        return {"conId": self.contact_id, "isBallotInfoRequired": True}


ACTIONS: list[type[Action]] = [
    CheckContactExistAction,
    GetCurrentContactInformationAction,
    GetPersonalInformationAction,
]


class GARequest(p.BaseModel, frozen=True):
    """An arbitrary request to the GA voter reg site."""

    actions: t.Sequence[Action]

    @classmethod
    def _get_current_fwuid(cls) -> str:
        """Return the current 'framework UID' used on the GA reg site."""
        # TODO FUTURE: Improve this.
        #
        # This constant seems to indicate the current "version" of the site.
        #
        # If it goes out of date, requests formed by this script will fail.
        #
        # It looks like I can explicitly find  the current version by visiting
        # https://mvp.sos.ga.gov/s/ and looking for a script tag whose `src`
        # attribute contains an `fwuid` query parameter.
        #
        # For today, let's just hardcode the value.
        return "ZDROWDdLOGtXcTZqSWZiU19ZaDJFdzk4bkk0bVJhZGJCWE9mUC1IZXZRbmcyNDguMTAuNS01LjAuMTA"  # noqa: E501

    @classmethod
    def _get_current_appid(cls) -> str:
        """Return the current 'app markup ID' used on the GA reg site."""
        # Same story as with fwuid.
        return "7766VpxH8B5ZgC8Vrgi-bQ"

    @classmethod
    def _get_secondary_loader_id(cls) -> str:
        """Return the current 'secondary loader ID' used on the GA reg site."""
        # Same story as with fwuid.
        return "nSN3-Xh18FbrdCVGqsWZnw"

    @classmethod
    def _build_aura_context(cls) -> dict:
        """Return the current 'aura context' used on the GA reg site."""
        # Same story as with fwuid.
        return {
            "mode": "PROD",
            "fwuid": cls._get_current_fwuid(),
            "app": "siteforce:communityApp",
            "loaded": {
                "APPLICATION@markup://siteforce:communityApp": cls._get_current_appid(),
                "COMPONENT@markup://instrumentation:o11ySecondaryLoader": cls._get_secondary_loader_id(),  # noqa: E501
            },
            "dn": [],
            "globals": {},
            "uad": False,
        }

    def to_data(self) -> dict:
        """Return the data used as part of the larger request structure."""
        message = {"actions": [action.to_data() for action in self.actions]}
        return {
            "message": json.dumps(message),
            "aura.context": json.dumps(self._build_aura_context()),
            "aura.token": None,
            "aura.pageURI": "/s/",
        }


# ------------------------------------------------------------------------
# Utilities for processing responses from the GA voter reg site
# ------------------------------------------------------------------------


def _build_action_result(action_data: dict) -> ActionResult | None:
    """
    Process data for a single action result and build a typed result struct.

    On failure, return None.
    """
    action_id = action_data.get("id")
    if not action_id:
        return None
    action_class = next((a for a in ACTIONS if a.__name__ == action_id), None)
    if not action_class:
        return None
    state = action_data.get("state")
    if state != "SUCCESS":
        return None
    outer_return_value = action_data.get("returnValue")
    if not isinstance(outer_return_value, dict):
        return None
    inner_return_value = outer_return_value.get("returnValue")
    if not isinstance(inner_return_value, dict):
        return None
    try:
        result = action_class.result_class.model_validate(inner_return_value)
    except p.ValidationError as e:
        # CONSIDER: look into pydantic support for empty dict in union w/ dict
        if action_id != "CheckContactExistAction":
            print("ERROR: cannot parse: ", e, file=sys.stderr)
            print(json.dumps(inner_return_value, indent=2), file=sys.stderr)
        return None
    return result


def _build_action_results(action_datas: t.Sequence[dict]) -> t.Sequence[ActionResult]:
    """Extract action result data and return a tuple of results."""
    return tuple(
        action_result
        for action_data in action_datas
        if (action_result := _build_action_result(action_data))
    )


class GAResponse(p.BaseModel, frozen=True):
    """A response from the GA voter reg site."""

    results: t.Sequence[ActionResult]

    @classmethod
    def for_response_data(cls, data: t.Any) -> t.Self:
        """Create a response from arbitrary response data."""
        if not isinstance(data, dict):
            return cls(results=())
        action_datas = data.get("actions")
        if not isinstance(action_datas, list):
            return cls(results=())
        results = _build_action_results(action_datas)
        return cls(results=results)

    def result_for_action(self, action: Action) -> ActionResult | None:
        """Return the result for a given action."""
        return self.result_for_class(action.__class__)

    def result_for_class(self, action_class: type[Action]) -> ActionResult | None:
        """Return the result for a given action ID."""
        for result in self.results:
            if isinstance(result, action_class.result_class):
                return result
        return None


# ------------------------------------------------------------------------
# Utilities for issuing requests to the GA site
# ------------------------------------------------------------------------

GA_URL = "https://mvp.sos.ga.gov/s/sfsites/aura"


def _invoke_ga_endpoint(request: GARequest) -> httpx.Response:
    """Invoke an endpoint on the GA voter reg site."""
    final_url = f"{GA_URL}?aura.ApexAction.execute={len(request.actions)}"
    response = httpx.post(
        final_url,
        data=request.to_data(),
    )
    response.raise_for_status()
    return response


def make_ga_request(request: GARequest) -> GAResponse:
    """Make a request to the GA voter reg site."""
    response = _invoke_ga_endpoint(request)
    try:
        data = response.json()
    except Exception:
        print("INVALID JSON: ", response.text, file=sys.stderr)
        return GAResponse(results=())
    ga_response = GAResponse.for_response_data(data)
    return ga_response


def _check_contact_exist(
    first_name: str, last_name: str, zipcode: str, birth_date: datetime.date
) -> CheckContactExistResult | None:
    """
    Check if the user is registered to vote in Georgia.

    If so, return the voter's "contact ID". Otherwise, return None.
    """
    check_action = CheckContactExistAction(
        first_name=first_name,
        last_name=last_name,
        zipcode=zipcode,
        birth_date=birth_date,
    )
    request = GARequest(actions=(check_action,))
    response = make_ga_request(request)
    check_result = t.cast(
        CheckContactExistResult | None, response.result_for_action(check_action)
    )
    return check_result


def _get_contact_details(contact_id: str) -> GetPersonalInformationResult | None:
    """Get the details of a registered voter, by contact ID, in Georgia."""
    personal_action = GetPersonalInformationAction(contact_id=contact_id)
    request = GARequest(actions=(personal_action,))
    response = make_ga_request(request)
    personal_result = t.cast(
        GetPersonalInformationResult | None, response.result_for_action(personal_action)
    )
    return personal_result


# ------------------------------------------------------------------------
# CheckRegistrationTool implementation for GA
# ------------------------------------------------------------------------


class GeorgiaCheckRegistrationTool(CheckRegistrationTool):
    """A tool for checking voter registration in Georgia."""

    state: t.ClassVar[str] = "GA"
    features: t.ClassVar[SupportedFeatures] = SupportedFeatures(details=True)

    def check_registration(
        self,
        first_name: str,
        last_name: str,
        zipcode: str,
        birth_date: datetime.date,
        details: bool = False,
    ) -> CheckRegistrationResult:
        """Check whether a voter is registered in Georgia."""
        try:
            check_result = _check_contact_exist(
                first_name, last_name, zipcode, birth_date
            )
        except Exception as e:
            raise CheckRegistrationError("Error checking voter registration") from e

        if check_result is None:
            return CheckRegistrationResult(registered=False, details=None)

        if not check_result.success:
            raise CheckRegistrationError("Error checking voter registration")

        if not details:
            return CheckRegistrationResult(registered=True, details=None)

        contact_id = check_result.message.contact_id

        try:
            personal_result = _get_contact_details(contact_id)
        except Exception as e:
            raise CheckRegistrationError("Error checking voter registration") from e

        if personal_result is None:
            return CheckRegistrationResult(registered=True, details=None)

        return CheckRegistrationResult(
            registered=True,
            details=CheckRegistrationDetails(
                state_id=personal_result.voter_reg_number,
                registration_date=personal_result.registration_date,
                status=personal_result.status.lower(),
            ),
        )
