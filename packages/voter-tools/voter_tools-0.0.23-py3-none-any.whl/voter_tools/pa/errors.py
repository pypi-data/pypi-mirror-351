import typing as t

import pydantic as p

from ..errors import APIError


class ProgrammingError(APIError):
    """Raised when a something is broken with this library's code."""

    pass


class InvalidAccessKeyError(APIError):
    """
    Raised when an invalid access key is provided.

    The key may be invalid, or it may not have the necessary permissions.

    For instance, a read-only key may not be used to submit registrations.
    """

    _default_message: t.ClassVar[str] = """

    Invalid API access key. It may be *entirely* invalid, or it may simply not
    have the permissions necessary to fulfill the request. For instance, the
    PA SOS hands out read-only keys that can't be used to submit registrations,
    and also hands out keys that cannot be used for mail-in applications.
"""

    def __init__(self, message: str | None = None) -> None:
        """Initialize the error with the given message."""
        super().__init__(message or self._default_message)


class UnparsableResponseError(APIError):
    """The PA API returned a response that could not be parsed."""

    pass


class TimeoutError(APIError):
    """Raised when a request to the server times out."""

    pass


class ServiceUnavailableError(APIError):
    """Raised when the service is currently unavailable."""

    pass


class APIErrorDetails(p.BaseModel, frozen=True):
    """Details meant to mimic pydantic's internal ErrorDetails."""

    type: str
    msg: str
    loc: tuple[str, ...]


class APIValidationError(APIError):
    """Raised when the pennsylvania API returns one or more validation errors."""

    # This is intended to look similar to pydantic's ValidationError,
    # but building Pydantic ValidationErrors directly is somewhat annoying
    # (see

    _errors: tuple[APIErrorDetails, ...]

    def __init__(self, errors: t.Iterable[APIErrorDetails]) -> None:
        """Initialize the error with the given errors."""
        self._errors = tuple(errors)
        locs = ", ".join(str(error.loc) for error in errors)
        message = f"Validation errors on {locs}"
        if len(self._errors) == 1:
            message += f": {self._errors[0].msg}"
        super().__init__(message)

    def errors(self) -> tuple[APIErrorDetails, ...]:
        """Return the validation errors."""
        return self._errors

    def json(self) -> list:
        """Return the validation errors as a JSON-serializable dictionary."""
        return [error.model_dump(mode="json") for error in self._errors]

    def merge(self, other: "APIValidationError") -> "APIValidationError":
        """Merge this error with another and return the result."""
        # NOTE: This is different than python's list.append() method since
        # it returns a new object rather than modifying the existing one.
        return APIValidationError(self._errors + other._errors)

    @classmethod
    def simple(cls, field: str, type: str, msg: str) -> "APIValidationError":
        """Create a simple validation error with a single error."""
        return cls([APIErrorDetails(type=type, msg=msg, loc=(field,))])

    @classmethod
    def unexpected(cls, code: str | None = None) -> "APIValidationError":
        """Create a generic validation error for unexpected error codes."""
        code_f = f" ({code})" if code is not None else "(empty response)"
        details = APIErrorDetails(
            type="unexpected",
            msg=f"Unexpected error. Please correct your form and try again. {code_f}",
            loc=(),
        )
        return cls([details])


# -----------------------------------------------------------------------------
# Mapping of well-known API error codes to error behaviors
# -----------------------------------------------------------------------------

# The intent of all this code is to make it easy to map the weird error codes
# that the PA API returns into either:
#
# 1. A handful of special purpose exceptions (like InvalidAccessKeyError)
# 2. A validation error that looks very similar to a pydantic ValidationError


def merge_errors(errors: t.Iterable[APIError]) -> APIError | None:
    """
    Merge multiple errors into a single error.

    If no errors are provided, None is returned.

    If all errors derive from APIValidationError, they are merged into a single
    APIValidationError, which is returned. Otherwise, the first
    non-APIValidationError is returned.
    """
    accumulated: APIValidationError | None = None
    for error in errors:
        if not isinstance(error, APIValidationError):
            return error
        if accumulated is None:
            accumulated = error
        else:
            accumulated = accumulated.merge(error)
    return accumulated


def build_error_for_codes(codes: tuple[str, ...]) -> APIError | None:
    """
    Return the single most appropriate error for a collection of PA API codes.

    If no codes are provided, None is returned.
    """
    errors: list[APIError] = []
    for code in codes:
        error = ERROR_MAP.get(_simplify_error_code(code))
        if error is None:
            error = APIValidationError.unexpected(code)
        errors.append(error)
    return merge_errors(errors)


# A collection of mappings from known API error codes to error behaviors.
#
# We have two kinds of "behaviors": APIError classes and validation errors.
#
# APIErrors generally get directly raised when they are encountered.
#
# Validation errors mean that the API request succeeded, but the voter
# registration data was invalid in some way.
#
# Note that *most* of these, particularly the validation errors, should
# never happen in practice. That's because our own validation code should catch
# them *before* we ever make a request to the PA API. But we include them here
# just in case.
#
# A handful of validations *are* genuinely possible. For instance, only
# the API back-end knows how to validate a driver's license number, so we
# expect this *may* be returned by the API.
#
# It's worth noting that a handful of these errors are repeated. For instance,
# there are several different errors that all amount to "you didn't select
# a valid `political_party`.". Some errors are ambiguous or may be re-used
# for multiple fields. It's a mess, folks! So be it.
BASE_ERROR_MAP: dict[str, APIError] = {
    "VR_WAPI_InvalidAccessKey": InvalidAccessKeyError(),
    "VR_WAPI_InvalidAction": ProgrammingError("Action not found."),
    "VR_WAPI_InvalidAPIbatch": ProgrammingError("Batch value is invalid."),
    "VR_WAPI_InvalidOVRCounty": ProgrammingError(
        "Computed `county` field was invalid."
    ),
    "VR_WAPI_InvalidOVRDL": APIValidationError.simple(
        "drivers_license", "invalid", "Invalid driver's license."
    ),
    "VR_WAPI_InvalidOVRDLformat": APIValidationError.simple(
        "drivers_license", "invalid", "Invalid driver's license format."
    ),
    "VR_WAPI_InvalidOVRDOB": APIValidationError.simple(
        "birth_date", "invalid", "Invalid date of birth."
    ),
    "VR_WAPI_InvalidOVRemail": APIValidationError.simple(
        "email", "invalid", "Invalid email address."
    ),
    "VR_WAPI_InvalidOVRmailingzipcode": APIValidationError.simple(
        "mailing_zipcode", "invalid", "Please enter a valid 5 or 9-digit ZIP code."
    ),
    "VR_WAPI_InvalidOVRphone": APIValidationError.simple(
        "phone_number", "invalid", "Invalid phone number."
    ),
    "VR_WAPI_InvalidOVRPreviousCounty": APIValidationError.simple(
        "previous_county", "invalid", "Unknown county."
    ),
    "VR_WAPI_InvalidOVRPreviouszipcode": APIValidationError.simple(
        "previous_zip5", "invalid", "Please enter a valid 5-digit ZIP code."
    ),
    "VR_WAPI_InvalidOVRSSNformat": APIValidationError.simple(
        "ssn4", "invalid", "Please enter the last four digits of your SSN."
    ),
    "VR_WAPI_InvalidOVRzipcode": APIValidationError.simple(
        "zip5", "invalid", "Please enter a valid 5-digit ZIP code."
    ),
    "VR_WAPI_invalidpreviousregyear": APIValidationError.simple(
        "previous_year", "invalid", "Please enter a valid year."
    ),
    "VR_WAPI_InvalidReason": ProgrammingError("Invalid registration_kind provided."),
    "VR_WAPI_MissingAccessKey": ProgrammingError(
        "The PA client did not supply an API key."
    ),
    # TODO DAVE:
    # ASK PA API TEAM: this error appears to apply to both `address`
    # *and* to `mailing_address`. Is there a way to distinguish?
    "VR_WAPI_MissingAddress": APIValidationError.simple(
        "mailing_address", "missing", "A complete address is required."
    ),
    "VR_WAPI_MissingAPIaction": ProgrammingError(
        "The PA client did not supply an `action` value."
    ),
    "VR_WAPI_MissingCounty": ProgrammingError(
        "The PA client did not supply a `county` value in a `get_municipalities` call.",
    ),
    "VR_WAPI_MissingLanguage": ProgrammingError(
        "The PA client did not supply a `language` value."
    ),
    "VR_WAPI_MissingOVRassistancedeclaration": APIValidationError.simple(
        "assistant_declaration",
        "missing",
        "Please indicate assistance was provided with the completion of this form.",
    ),
    "VR_WAPI_MissingOVRcity": APIValidationError.simple(
        "city", "missing", "Please enter a valid city."
    ),
    "VR_WAPI_MissingOVRcounty": ProgrammingError(
        "Computed `county` field was missing."
    ),
    "VR_WAPI_MissingOVRdeclaration1": APIValidationError.simple(
        "confirm_declaration",
        "missing",
        "Please confirm you have read and agree to the terms.",
    ),
    "VR_WAPI_MissingOVRDL": APIValidationError.simple(
        "drivers_license",
        "missing",
        "Please supply a valid PA driver's license or PennDOT ID card number.",
    ),
    "VR_WAPI_MissingOVRfirstname": APIValidationError.simple(
        "first_name", "missing", "Your first name is required."
    ),
    "VR_WAPI_MissingOVRinterpreterlang": APIValidationError.simple(
        "interpreter_language", "missing", "Required if interpreter is checked."
    ),
    "VR_WAPI_MissingOVRisageover18": APIValidationError.simple(
        "will_be_18", "missing", "You must provide a response."
    ),
    "VR_WAPI_MissingOVRisuscitizen": APIValidationError.simple(
        "is_us_citizen", "missing", "You must provide a response."
    ),
    "VR_WAPI_MissingOVRlastname": APIValidationError.simple(
        "last_name", "missing", "Your last name is required."
    ),
    "VR_WAPI_MissingOVROtherParty": APIValidationError.simple(
        "other_party", "missing", "You must write-in a party of 'other' is selected."
    ),
    "VR_WAPI_MissingOVRPoliticalParty": APIValidationError.simple(
        "political_party", "missing", "Please select a political party."
    ),
    "VR_WAPI_MissingOVRPreviousAddress": APIValidationError.simple(
        "previous_address", "missing", "Required for an address change application."
    ),
    "VR_WAPI_MissingOVRPreviousCity": APIValidationError.simple(
        "previous_city", "missing", "Required for an address change application."
    ),
    "VR_WAPI_MissingOVRPreviousFirstName": APIValidationError.simple(
        "previous_first_name", "missing", "Required for a name change application."
    ),
    "VR_WAPI_MissingOVRPreviousLastName": APIValidationError.simple(
        "previous_last_name", "missing", "Required for a name change application."
    ),
    "VR_WAPI_MissingOVRPreviousZipCode": APIValidationError.simple(
        "previous_zip5", "missing", "Required for an address change application."
    ),
    "VR_WAPI_MissingOVRSSNDL": APIValidationError.simple(
        "ssn4", "missing", "Please supply the last four digits of your SSN."
    ),
    "VR_WAPI_MissingOVRstreetaddress": APIValidationError.simple(
        "address", "missing", "Please enter your street address."
    ),
    "VR_WAPI_MissingOVRtypeofassistance": APIValidationError.simple(
        "assistance_type", "missing", "Please select the type of assistance required."
    ),
    "VR_WAPI_MissingOVRzipcode": APIValidationError.simple(
        "zip5", "missing", "Please enter your 5-digit ZIP code."
    ),
    # CONSIDER DAVE: maybe this is a ProgrammingError?
    "VR_WAPI_MissingReason": APIValidationError.simple(
        "registration_kind",
        "missing",
        "Please select at least one reason for change applications.",
    ),
    "VR_WAPI_PennDOTServiceDown": ServiceUnavailableError(
        "The PennDOT service is currently down. Please try again later.",
    ),
    "VR_WAPI_RequestError": ProgrammingError(
        "The API request was invalid for unknown reasons."
    ),
    "VR_WAPI_ServiceError": ServiceUnavailableError(
        "The PA signature service is currently down. PLease try again later.",
    ),
    "VR_WAPI_SystemError": ServiceUnavailableError(
        "The PA voter registration service is currently down. Please try again later.",
    ),
    "VR_WAPI_InvalidOVRAssistedpersonphone": APIValidationError.simple(
        "assistant_phone", "invalid", "Please enter a valid phone number."
    ),
    "VR_WAPI_InvalidOVRsecondemail": APIValidationError.simple(
        "alternate_email", "invalid", "Please enter a valid email address."
    ),
    "VR_WAPI_Invalidsignaturestring": ServiceUnavailableError(
        "The signature upload was not successful. Please try again.",
    ),
    "VR_WAPI_Invalidsignaturetype": ProgrammingError(
        "Invalid signature file type was sent to the API endpoint."
    ),
    "VR_WAPI_Invalidsignaturesize": ProgrammingError(
        "Invalid signature file size of >= 5MB was sent to the API endpoint.",
    ),
    "VR_WAPI_Invalidsignaturedimension": ProgrammingError(
        "A signature image of other than 180 x 60 pixels was sent to the API endpoint.",
    ),
    "VR_WAPI_Invalidsignaturecontrast": ProgrammingError(
        "The signature has invalid contrast."
    ),
    "VR_WAPI_MissingOVRParty": APIValidationError.simple(
        "political_party", "missing", "Please select a political party."
    ),
    "VR_WAPI_InvalidOVRPoliticalParty": APIValidationError.simple(
        "political_party", "missing", "Please select a political party."
    ),
    "VR_WAPI_Invalidsignatureresolution": ProgrammingError(
        "Invalid signature resolution of other than 96dpi was sent to the endpoint.",
    ),
    "VR_WAPI_MissingOVRmailinballotaddr": APIValidationError.simple(
        "mail_in_address", "missing", "Please enter an address."
    ),
    "VR_WAPI_MissingOVRmailincity": APIValidationError.simple(
        "mail_in_city", "missing", "Please enter a city."
    ),
    "VR_WAPI_MissingOVRmailinstate": APIValidationError.simple(
        "mail_in_state", "missing", "Please enter a state."
    ),
    "VR_WAPI_InvalidOVRmailinzipcode": APIValidationError.simple(
        "mail_in_zipcode", "missing", "Please enter a 5 or 9-digit ZIP code."
    ),
    "VR_WAPI_MissingOVRmailinlivedsince": APIValidationError.simple(
        "mail_in_lived_since", "missing", "Please choose a date."
    ),
    "VR_WAPI_MissingOVRmailindeclaration": APIValidationError.simple(
        "mail_in_declaration",
        "missing",
        "Please indicate you have read and agreed to the terms.",
    ),
    "VR_WAPI_MailinNotEligible": APIValidationError.simple(
        "is_mail_in", "invalid", "This application is not mail-in eligible."
    ),
    "VR_WAPI_InvalidIsTransferPermanent": APIValidationError.simple(
        "transfer_permanent_status", "invalid", "This is not a valid value."
    ),
}


def _simplify_error_code(code: str) -> str:
    """Map an error code received from the PA API to a simpler form."""
    # We do this because, unfortunately, we've encountered cases where the
    # PA API sandbox endpoint sends very similar looking -- but not identical --
    # error codes back to us for days at a time. We send an email to the fine
    # folks in Harrisburg, and eventually things get squared away. It's impossible
    # to *entirely* eliminate this problem, but we can at least make it a tiny
    # bit less likely based on our own observations. In the worst case, if this
    # fails, we'll just raise generic "unexpected" errors.

    splits = code.split("_")  # sometimes the prefixes change slightly
    code = splits[-1]  # the final part of the code is the most stable
    code = code.replace("OVR", "")  # sometimes this goes away
    return code.lower()  # the capitalization is inconsistent


ERROR_MAP: dict[str, APIError] = {
    _simplify_error_code(code): error for code, error in BASE_ERROR_MAP.items()
}
