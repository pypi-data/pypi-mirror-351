import datetime
import io
import typing as t
from base64 import b64decode, b64encode
from enum import Enum
from urllib.parse import urlencode

import httpx
import pydantic as p
import pydantic_xml as px
from PIL import Image

from .counties import CountyChoice, get_county_choice
from .errors import (
    APIError,
    APIValidationError,
    ServiceUnavailableError,
    UnparsableResponseError,
    build_error_for_codes,
)

STAGING_URL = "https://paovrwebapi.beta.vote.pa.gov/SureOVRWebAPI/api/ovr"
PRODUCTION_URL = "https://paovrwebapi.vote.pa.gov/SureOVRWebAPI/api/ovr"

try:
    from lxml.etree import _Element as XmlElement  # type: ignore
    from lxml.etree import fromstring as xml_fromstring  # type: ignore
    from lxml.etree import tostring as xml_tostring  # type: ignore
except ImportError:
    from xml.etree.ElementTree import Element as XmlElement
    from xml.etree.ElementTree import fromstring as xml_fromstring
    from xml.etree.ElementTree import tostring as xml_tostring


# -----------------------------------------------------------------------------
# Pydantic validators & serializers for common data types found in the API
# -----------------------------------------------------------------------------

# Response dates from the PA API come in this format
PA_API_RESPONSE_DATE_FORMAT = "%m/%d/%Y"


def parse_response_date(v: str | datetime.date) -> datetime.date:
    """Parse dates in the PA API format."""
    if isinstance(v, datetime.date):
        return v
    return datetime.datetime.strptime(v, PA_API_RESPONSE_DATE_FORMAT).date()


def serialize_response_date(v: datetime.date) -> str:
    """Serialize dates in the PA API format."""
    return v.strftime(PA_API_RESPONSE_DATE_FORMAT)


PAResponseDate: t.TypeAlias = t.Annotated[
    datetime.date,
    p.PlainSerializer(serialize_response_date),
    p.BeforeValidator(parse_response_date),
]


# Response date times from the PA API come in this format
# 'Jun 26 2024  7:43PM' <-- may have extra spaces
PA_API_RESPONSE_DT_FORMAT = "%b %d %Y  %I:%M%p"


def parse_response_dt(v: str | datetime.datetime) -> datetime.datetime:
    """Parse dates in the PA API format."""
    if isinstance(v, datetime.datetime):
        return v
    return datetime.datetime.strptime(v, PA_API_RESPONSE_DT_FORMAT)


def serialize_response_dt(v: datetime.datetime) -> str:
    """Serialize dates in the PA API format."""
    return v.strftime(PA_API_RESPONSE_DT_FORMAT)


PAResponseDateTime: t.TypeAlias = t.Annotated[
    datetime.datetime,
    p.PlainSerializer(serialize_response_dt),
    p.BeforeValidator(parse_response_dt),
]


# Request dates sent to the PA API should be in this format
PA_API_REQUEST_DATE_FORMAT = "%Y-%m-%d"


def parse_request_date(v: str | datetime.date) -> datetime.date:
    """Parse dates in the PA API format."""
    if isinstance(v, datetime.date):
        return v
    return datetime.datetime.strptime(v, PA_API_REQUEST_DATE_FORMAT).date()


def serialize_request_date(v: datetime.date) -> str:
    """Serialize dates in the PA API format."""
    return v.strftime(PA_API_REQUEST_DATE_FORMAT)


PARequestDate: t.TypeAlias = t.Annotated[
    datetime.date,
    p.PlainSerializer(serialize_request_date),
    p.BeforeValidator(parse_request_date),
]


# At least this one is consistent!
PA_API_TIME_FORMAT = "%I:%M %p"


def parse_time(v: str | datetime.time) -> datetime.time:
    """Parse times in the PA API format."""
    if isinstance(v, datetime.time):
        return v
    return datetime.datetime.strptime(v, PA_API_TIME_FORMAT).time()


def serialize_time(v: datetime.time) -> str:
    """Serialize times in the PA API format."""
    return v.strftime(PA_API_TIME_FORMAT)


PATime: t.TypeAlias = t.Annotated[
    datetime.time, p.PlainSerializer(serialize_time), p.BeforeValidator(parse_time)
]


def title_case(v: str) -> str:
    """Ensure the string is title-cased."""
    return v.title()


TitleCaseStr: t.TypeAlias = t.Annotated[str, p.AfterValidator(title_case)]


def parse_phone_number(v: str) -> str:
    """Transform phone numbers to the PA API format, ###-###-####."""
    # Remove all non-numeric characters from the phone number.
    digits = "".join(filter(str.isdigit, v))
    # If there are 11 digits, check if the first digit is a '1' and remove it.
    if len(digits) == 11:
        if digits[0] != "1":
            raise ValueError("Phone number must start with '1' if it has 11 digits.")
        digits = digits[1:]
    if len(digits) != 10:
        raise ValueError("Phone number must have 10 digits.")
    # Format the phone number as ###-###-####.
    return f"{digits[:3]}-{digits[3:6]}-{digits[6:]}"


PhoneNumber: t.TypeAlias = t.Annotated[str, p.BeforeValidator(parse_phone_number)]


def validate_bit(v: int | str | bool) -> bool:
    """Validate that the value is a bit (0 or 1)."""
    if isinstance(v, bool):
        return v
    if isinstance(v, str):
        if v not in {"0", "1"}:
            raise ValueError("Bit value must be '0' or '1'.")
        return v == "1"
    if v not in {0, 1}:
        raise ValueError("Bit value must be 0 or 1.")
    return bool(v)


def bit_serializer(v: bool) -> int:
    """
    Serialize a boolean value as an integer (0 or 1).

    This is used for lots of boolean values in the PA API, which are
    represented as integers (0 or 1) in the XML.
    """
    return int(v)


Bit: t.TypeAlias = t.Annotated[
    bool, p.PlainSerializer(bit_serializer), p.BeforeValidator(validate_bit)
]


def validate_true_bit(v: int | str | bool) -> t.Literal[True]:
    """Validate that the value is a true bit (1)."""
    as_bit = validate_bit(v)
    if not as_bit:
        raise ValueError("Bit value must resolve to `True`.")
    return True


TrueBit: t.TypeAlias = t.Annotated[
    t.Literal[True],
    p.PlainSerializer(bit_serializer),
    p.BeforeValidator(validate_true_bit),
]


def validate_empty_str_as_none(v: str | None) -> str | None:
    """Validate that an empty string is treated as None."""
    if v == "":
        return None
    return v


EmptyStrNone: t.TypeAlias = t.Annotated[
    str | None,
    p.BeforeValidator(validate_empty_str_as_none),
]


def _binaryio_to_image(bio: t.BinaryIO) -> Image.Image:
    """Convert a binary file-like object to a PIL Image."""
    # Open the image from the file-like object.
    try:
        image = Image.open(bio)
        image.load()
    except Exception as e:
        raise ValueError("Invalid image data.") from e
    return image


def _bytes_to_image(b: bytes) -> Image.Image:
    """Convert a byte string to a PIL Image."""
    return _binaryio_to_image(io.BytesIO(b))


def data_url_to_image(data_url: str) -> Image.Image:
    """Convert a data: URL to a PIL Image."""
    # Split the data URL into its components.
    parts = data_url.split(",")
    if len(parts) != 2:
        raise ValueError("Invalid data: URL format.")

    if not parts[0].startswith("data:image/"):
        raise ValueError("Invalid data: URL format.")

    if not parts[0].endswith(";base64"):
        raise ValueError("Invalid data: URL format.")

    # Extract the data and decode it.
    try:
        data = parts[1].encode("utf-8")
        decoded = b64decode(data)
    except Exception as e:
        raise ValueError("Invalid data: URL format.") from e

    return _bytes_to_image(decoded)


def image_to_data_url(image: Image.Image) -> str:
    """Convert a PIL Image to a data: URL."""
    # Create a file-like object to store the image data.
    bio = io.BytesIO()
    image.save(bio, format="PNG", dpi=(75, 75))
    # Encode the image data as a base64 string.
    encoded = b64encode(bio.getvalue()).decode("utf-8")
    # Return the data: URL.
    return f"data:image/png;base64,{encoded}"


SIGNATURE_IMAGE_SIZE = (180, 60)


def validate_signature_image(
    v: str | bytes | t.BinaryIO | Image.Image,
) -> str:
    """
    Validate that the value is a valid signature image.

    The validator accepts a string, bytes, a binary file-like object, or a PIL
    Image object. If a string is provided, it is assumed to be a valid
    data: URL for an image. If bytes are provided, they are assumed to be the
    raw image data. If a file-like object is provided, it is read and its
    contents are used as the image data. If a PIL Image object is provided, it
    is treated as the image itself.

    Raw image data is converted to a canonical format, specifically a black
    and white PNG that is 180x60 pixels in size, marked as 75 DPI. The PA
    documentation says it wants < 98% white pixels and < 90% black pixels,
    but we mostly ignore that for now.

    The validator returns a string, which is the data: URL for the image.
    """
    image: Image.Image

    # Perform the basic conversion
    if isinstance(v, str):
        image = data_url_to_image(v)
    elif isinstance(v, bytes):
        image = _bytes_to_image(v)
    elif isinstance(v, t.BinaryIO) or isinstance(v, io.BytesIO):
        image = _binaryio_to_image(v)
    elif isinstance(v, Image.Image):
        image = v
    else:
        raise ValueError("Invalid signature image data kind.")

    def _threshold(p: int) -> int:
        """Threshold function for converting to black and white."""
        return 255 if p > 56 else 0

    # Resize the image to 180x60 pixels, make it black and white.
    resized = (
        image.convert("L").point(_threshold, mode="1").resize(SIGNATURE_IMAGE_SIZE)
    )

    # Convert the image to a data: URL.
    return image_to_data_url(resized)


SignatureImage: t.TypeAlias = t.Annotated[
    str, p.BeforeValidator(validate_signature_image)
]


# -----------------------------------------------------------------------------
# Generic response type
# -----------------------------------------------------------------------------


class APIResponse(px.BaseXmlModel, tag="RESPONSE", frozen=True):
    """
    A generic response from the Pennsylvania OVR API.

    This is a simple response that contains a status code and a message. Not
    all API calls return this response structure, but some do.

    It is also the response structure used on *any* error response, including
    for API calls that would normally return a different response type.
    """

    application_id: str | None = px.element(alias="APPLICATIONID", default=None)
    """The application ID, if one was created."""

    application_date: PAResponseDateTime | None = px.element(
        alias="APPLICATIONDATE", default=None
    )
    """The application date, if one was created."""

    signature: str | None = px.element(alias="SIGNATURE", default=None)
    """The signature, if one was created."""

    error_codes: tuple[str, ...] | None = px.element(alias="ERROR", default=None)
    """
    The error codes, if an error occurred.

    If batch mode is set to ALL_ERRORS, this will contain all errors found, 
    otherwise it will contain at most one.
    """

    @p.field_validator("error_codes", mode="before")
    def validate_error_codes(cls, value: t.Any) -> tuple[str, ...] | None:
        """Ensure that error codes are always a tuple."""
        if value is None:
            return None
        if isinstance(value, str):
            return tuple(v for v in value.split(",") if v)
        # We assume there's something iterable here.
        try:
            # First, collapse that thing back into a string.
            value = ",".join(value)
            # Now split it back into a tuple. (Yeah, I know; sorry.)
            return tuple(v for v in value.split(",") if v)
        except Exception as e:
            # Nope, not even iterable.
            raise ValueError("Error codes must be a string or an iterable.") from e

    @property
    def error_code(self) -> str | None:
        """Return the first error code, if any."""
        if self.error_codes is None:
            return None
        return self.error_codes[0]

    def has_error(self) -> bool:
        """Check if the response indicates an error."""
        # On occasion, the API will return a response with neither an error code
        # nor an application ID. We treat this as a registration error.
        return (self.error_code is not None) or (self.application_id is None)

    def get_error(self) -> APIError | None:
        """Get the error object for the error code, or None."""
        if not self.error_code:
            if self.application_id is None:
                return APIValidationError.unexpected()
            return None
        return build_error_for_codes(self.error_codes or ())

    def raise_for_error(self) -> None:
        """Raise an exception if the response indicates an error."""
        error = self.get_error()
        if error is not None:
            raise error


# -----------------------------------------------------------------------------
# *SETUP Response Types
# -----------------------------------------------------------------------------


class SetupOption(px.BaseXmlModel, frozen=True):
    """Base class for all options returned by the *SETUP API calls."""

    pass


class Suffix(SetupOption, frozen=True):
    """A suffix for a name, like 'jr'."""

    code: str = px.element(alias="NameSuffixCode")
    """The code for the suffix (like 'jr')"""

    description: str = px.element(alias="NameSuffixDescription")
    """The human-readable description of the suffix (like 'JR.')."""


class Race(SetupOption, frozen=True):
    """The type of a person's race, like 'white'."""

    code: str = px.element(alias="RaceCode")
    """The code for the race (like 'W')."""

    description: TitleCaseStr = px.element(alias="RaceDescription")
    """The human-readable description for the race (like 'WHITE')."""


class UnitType(SetupOption, tag="UnitTypes", frozen=True):
    """The type of an address unit, like 'building'."""

    code: str = px.element(alias="UnitTypesCode")
    """The code for the unit type (like 'BLD')."""

    description: TitleCaseStr = px.element(alias="UnitTypesDescription")
    """The human-readable description for the unit type (like 'BUILDING')."""


class AssistanceType(SetupOption, frozen=True):
    """The type of assistance needed, like 'hearing impaired'."""

    code: str = px.element(alias="AssistanceTypeCode")
    """The code for the assistance type (like 'HI')."""

    description: str = px.element(alias="AssistanceTypeDescription")
    """
    The human-readable description for the assistance type.

    (like 'I am deaf or hard of hearing').
    """


class Gender(SetupOption, frozen=True):
    """The type of a person's gender, like 'female'."""

    code: str = px.element(alias="GenderCode")
    """The code for the gender (like 'U')."""

    description: str = px.element(alias="GenderDescription")
    """The human-readable description for the gender (like 'Unknown')."""


class PoliticalParty(SetupOption, frozen=True):
    """The type of a person's political party, like 'democratic'."""

    code: str = px.element(alias="PoliticalPartyCode")
    """The code for the political party (like 'D')."""

    description: str = px.element(alias="PoliticalPartyDescription")
    """The human-readable description for the political party (like 'Democratic')."""


class MailinAddressType(SetupOption, tag="MailinAddressTypes", frozen=True):
    """The type of a mail-in address, like 'residential'."""

    code: str = px.element(alias="MailinAddressTypesCode")
    """The code for the mail-in address type (like 'R')."""

    description: str = px.element(alias="MailinAddressTypesDescription")
    """
    The human-readable description for the mail-in address type.
     
    (like 'Residential Address').
    """


class County(SetupOption, frozen=True):
    """A single county in Pennsylvania, like 'Adams'."""

    code: int = px.element(alias="countyID")
    """The ID for the county (like '2290')."""

    name: TitleCaseStr | None = px.element(alias="Countyname", default=None)
    """
    The name of the county (like 'ADAMS').
    
    SETUP calls may return a single county with no name.
    """


class State(SetupOption, tag="States", frozen=True):
    """A state in the United States, like 'Pennsylvania'."""

    code: str = px.element(alias="Code")
    """The code for the state (like 'PA')."""

    name: str = px.element(alias="CodesDescription")
    """The human-readable description for the state (like 'Pennsylvania')."""


class SetupResponse(
    px.BaseXmlModel, tag="NewDataSet", search_mode="unordered", frozen=True
):
    """
    A full response from the *SETUP API call.

    The setup call returns a variety of mappings and other data that can be used
    to build a voter registration or mail-in ballot application.
    """

    suffixes: tuple[Suffix, ...] = px.element(tag="Suffix")
    """All available suffixes for a name."""

    races: tuple[Race, ...] = px.element(tag="Race")
    """All available race options."""

    unit_types: tuple[UnitType, ...] = px.element(tag="UnitTypes")
    """All available unit types for an address (like 'Apartment')."""

    assistance_types: tuple[AssistanceType, ...] = px.element(tag="AssistanceType")
    """All available assistance types (like 'I am deaf or hard of hearing')."""

    genders: tuple[Gender, ...] = px.element(tag="Gender")
    """All available gender options."""

    political_parties: tuple[PoliticalParty, ...] = px.element(tag="PoliticalParty")
    """All available political parties."""

    mailin_address_types: tuple[MailinAddressType, ...] = px.element(
        tag="MailinAddressTypes"
    )
    """All available mail-in address types (like 'Residence')."""

    counties: tuple[County, ...] = px.element(tag="County")
    """All available counties in Pennsylvania."""

    states: tuple[State, ...] = px.element(tag="States")
    """All available states in the United States."""

    next_registration_deadline: PAResponseDate = px.wrapped(
        "NextVRDeadline/NextVRDeadline"
    )
    """The next voter registration deadline."""

    next_election: PAResponseDate = px.wrapped("NextElection/NextElection")
    """The next election date."""

    ovr_app_declaration: str = px.wrapped("Text_OVRApplnDeclaration/Text")
    """HTML text containing a legal declaration for the online application."""

    ovr_assistance_declaration: str = px.wrapped(
        "Text_OVRApplnAssistanceDeclaration/Text"
    )
    """HTML text containing a legal declaration for assisted OVR application."""

    mail_in_declaration: str = px.wrapped("Text_OVRMailInApplnDeclaration/Text")
    """HTML text containing a legal declaration for the mail-in ballot application."""

    election_name: TitleCaseStr = px.wrapped("Text_OVRMailInElectionName/ElectionName")
    """The name of the next election."""

    mail_in_completion_time: PATime = px.wrapped("Text_OVRMailInApplnComplTime/Time")
    """The expected completion time-of-day for a mail-in ballot application."""

    mail_in_received_time: PATime = px.wrapped(
        "Text_OVRMailInBallotRecvdTime/RecvdTime"
    )
    """The cutoff time for receiving a mail-in ballot on a given day."""


# -----------------------------------------------------------------------------
# Municipalities Response
# -----------------------------------------------------------------------------


class Municipality(px.BaseXmlModel, tag="Municipality", frozen=True):
    """A single municipality in Pennsylvania, like 'Barnett Township'."""

    mun_type: int = px.element(alias="MunicipalityType")
    """The numerical type of the municipality."""

    id: str | None = px.element(alias="MunicipalityID", default=None)
    """The ID for the municipality (like 'MN01')."""

    name: TitleCaseStr | None = px.element(alias="MunicipalityIDname", default=None)
    """The name of the municipality (like 'BARNETT TOWNSHIP')."""

    county_id: int = px.element(alias="CountyID")
    """The ID for the county (like '2290')."""

    county_name: TitleCaseStr | None = px.element(alias="CountyName", default=None)
    """The name of the county (like 'ADAMS')."""


class MunicipalitiesResponse(px.BaseXmlModel, tag="OVRLookupData", frozen=True):
    """A response from the GETMUNICIPALITIES API call."""

    municipalities: tuple[Municipality, ...]
    """A list of municipalities in the given county."""


# -----------------------------------------------------------------------------
# Error Values Response
# -----------------------------------------------------------------------------


class ErrorValue(px.BaseXmlModel, tag="MessageText", frozen=True):
    """A single error value from the GETERRORVALUES API call."""

    code: str = px.element(alias="ErrorCode")
    """The code for the error value (like 'VR_WAPI_InvalidAccessKey')."""

    text: str = px.element(alias="ErrorText")
    """The human-readable description of the error value."""


class ErrorValuesResponse(px.BaseXmlModel, tag="OVRLookupData", frozen=True):
    """A response from the GETERRORVALUES API call."""

    errors: tuple[ErrorValue, ...]
    """A mapping from error code to error message."""


# -----------------------------------------------------------------------------
# Languages Response
# -----------------------------------------------------------------------------


class Language(px.BaseXmlModel, tag="Languages", frozen=True):
    """A single language in the Pennsylvania OVR API."""

    code: str = px.element(alias="LanguageCode")
    """The code for the language (like 'LANGENG')."""

    name: str = px.element(alias="Language")
    """The human-readable name for the language (like 'English')."""


class LanguagesResponse(px.BaseXmlModel, tag="OVRLookupData", frozen=True):
    """A response from the GETLANGUAGES API call."""

    languages: tuple[Language, ...]
    """A list of languages available in the API."""


# -----------------------------------------------------------------------------
# Set Application Request
# -----------------------------------------------------------------------------


NSMAP = {"": "OVRexternaldata"}


class BatchMode(int, Enum):
    """Enumeration of batch numbers for voter registration applications."""

    FIRST_ERROR_ONLY = 0
    """Request that the API returns exactly one error, if any is found."""

    ALL_ERRORS = 1
    """Request that the API returns all errors found in the application."""


class SuffixChoice(str, Enum):
    """
    Enumeration of suffixes for a person's name.

    CONSIDER: the API returns a list of valid <Suffix> in the *SETUP response.
    These seem quite stable, so we simply hard-code them here.
    """

    NONE = ""
    FIRST = "I"
    SECOND = "II"
    THIRD = "III"
    FOURTH = "IV"
    FIFTH = "V"
    SIXTH = "VI"
    SEVENTH = "VII"
    JUNIOR = "JR"
    SENIOR = "SR"


class PoliticalPartyChoice(str, Enum):
    """
    Enumeration of political parties in Pennsylvania.

    CONSIDER: the API returns a list of valid <PoliticalParty> in the *SETUP
    response. These seem quite stable, so we simply hard-code them here.
    """

    DEMOCRATIC = "D"
    REPUBLICAN = "R"
    GREEN = "GR"
    LIBERTARIAN = "LN"
    NO_AFFILIATION = "NF"
    OTHER = "OTH"


class GenderChoice(str, Enum):
    """
    Enumeration of possible genders.

    CONSIDER: the API returns a list of valid <Gender> in the *SETUP response.
    These seem quite stable, so we simply hard-code them here.
    """

    FEMALE = "F"
    MALE = "M"
    UNKNOWN = "U"


class RaceChoice(str, Enum):
    """
    Enumeration of possible races/ethnicities.

    CONSIDER: the API returns a list of valid <Race> in the *SETUP response.
    These seem quite stable, so we simply hard-code them here.
    """

    ASIAN = "A"
    BLACK_OR_AFRICAN_AMERICAN = "B"
    HISPANIC_OR_LATINO = "H"
    NATIVE_AMERICAN_OR_ALASKAN_NATIVE = "I"
    NATIVE_HAWAIIAN_OR_OTHER_PACIFIC_ISLANDER = "P"
    OTHER = "O"
    TWO_OR_MORE_RACES = "T"
    WHITE = "W"


class RegistrationKind(int, Enum):
    """Enumeration of registration kinds for a voter registration application."""

    CHANGE = 0
    """The application is a change of registration."""

    NEW = 1
    """The application is a new registration."""


class UnitTypeChoice(str, Enum):
    """
    Enumeration of possible address unit types.

    CONSIDER: the API returns a list of valid <UnitTypes> in the *SETUP response.
    These seem quite stable, so we simply hard-code them here.
    """

    APARTMENT = "APT"
    BASEMENT = "BSM"
    BOX = "BOX"
    BUILDING = "BLD"
    DEPARTMENT = "DEP"
    FLOOR = "FL"
    FRONT = "FRN"
    HANGER = "HNG"
    LOBBY = "LBB"
    LOT = "LOT"
    LOWER = "LOW"
    OFFICE = "OFC"
    PENTHOUSE = "PH"
    PIER = "PIE"
    POLL = "POL"
    REAR = "REA"
    ROOM = "RM"
    SIDE = "SID"
    SLIP = "SLI"
    SPACE = "SPC"
    STOP = "STO"
    SUITE = "STE"
    TRAILER = "TRL"  # XXX the API also returns a separate TRLR tuple. Ugh.
    UNIT = "UNI"
    UPPER = "UPP"
    CABIN = "CBN"
    HUB = "HUB"
    STUDENT_MAILING_CENTER = "SMC"
    TOWNHOUSE = "TH"


class AssistanceTypeChoice(str, Enum):
    """
    Enumeration of possible assistance types.

    CONSIDER: the API returns a list of valid <AssistanceType> in the *SETUP
    response. These seem quite stable, so we simply hard-code them here.
    """

    HARD_OF_HEARING = "HI"  # "I am deaf or hard of hearing"
    VISION_IMPAIRED = "VI"  # "I am blind or have difficulty seeing"
    USES_WHEELCHAIR = "WC"  # "I use a wheelchair"
    PHYSICAL_DISABILITY = "PD"  # "I have a physical disability"
    READING = "IL"  # "I need help reading"
    LANGUAGE = "LN"  # "I do not speak English well"


class MailInAddressTypeChoice(str, Enum):
    """
    Enumeration of possible mail-in address types.

    CONSIDER: the API returns a list of valid <MailinAddressTypes> in the *SETUP
    response. These seem quite stable, so we simply hard-code them here.
    """

    RESIDENTIAL = "R"
    MAILING = "M"
    ALTERNATE = "A"


class VoterBatch(px.BaseXmlModel, frozen=True):
    """01 - A batch mode for a voter registration application."""

    # XXX setting BatchMode.FIRST_ERROR_ONLY results in the staging
    # endpoint returning empty responses. But *the exact same* application
    # data works fine with BatchMode.ALL_ERRORS. This must be a bug in the API.
    batch: BatchMode = px.element(default=BatchMode.ALL_ERRORS)


class VoterName(px.BaseXmlModel, frozen=True):
    """02 - Personal information for a voter registration application."""

    first_name: str = px.element(tag="FirstName", max_length=30)
    middle_name: str | None = px.element(tag="MiddleName", default=None, max_length=30)
    last_name: str = px.element(tag="LastName", max_length=30)
    suffix: SuffixChoice = px.element(tag="TitleSuffix", default=SuffixChoice.NONE)


class VoterEligibility(px.BaseXmlModel, frozen=True):
    """03 - Eligibility information for a voter registration application."""

    is_us_citizen: TrueBit = px.element(tag="united-states-citizen")
    will_be_18: TrueBit = px.element(tag="eighteen-on-election-day")

    @p.model_validator(mode="after")
    def validate_age(self) -> t.Self:
        """Ensure that the voter will be 18 on election day."""
        if not self.will_be_18:
            raise ValueError("Voter must be 18 on election day.")
        return self

    @p.model_validator(mode="after")
    def validate_citizenship(self) -> t.Self:
        """Ensure that the voter is a US citizen."""
        if not self.is_us_citizen:
            raise ValueError("Voter must be a US citizen.")
        return self


class VoterReason(px.BaseXmlModel, frozen=True):
    """

    Manage the reasons for a voter registration application.

    This combines two sections of the API documentation spreadsheet:

    04 - Reason for a voter registration application, and
    11 - Voting information has changed

    since proper validation requires the combination of both.
    """

    registration_kind: RegistrationKind = px.element(tag="isnewregistration")
    """Whether the application is a new registration, or a change."""

    is_name_change: Bit = px.element(tag="name-update", default=False)
    """Whether the application includes a name change."""

    is_address_change: Bit = px.element(tag="address-update", default=False)
    """Whether the application includes an address change."""

    is_party_change: Bit = px.element(tag="ispartychange", default=False)
    """Whether the application includes a party change."""

    is_federal_voter: Bit = px.element(tag="isfederalvoter", default=False)
    """
    Whether the application is for a Federal or State employee registering
    in their county of last residence.

    This is a bit confusing, but it's what the PA docs say. Moreover, this
    can apparently be *combined* with either new *or* change registrations.
    Okay!
    """

    @p.model_validator(mode="after")
    def validate_reasons(self) -> t.Self:
        """
        If the application is a new registration, no reasons should be selected.

        If the application is a change of registration, at least one reason
        should be selected.
        """
        any_reasons = any(
            (
                self.is_name_change,
                self.is_address_change,
                self.is_party_change,
            )
        )
        if self.registration_kind == RegistrationKind.NEW:
            if any_reasons:
                raise ValueError(
                    "No reasons should be selected for a new registration."
                )
        else:
            if not any_reasons:
                raise ValueError(
                    "At least one reason should be selected for a change regs."
                )
        return self

    voter_reg_number: str | None = px.element(
        "voterregnumber", default=None, max_length=12
    )
    """
    The voter registration number, if the application is a change.

    This is not strictly required for a change application, but it may
    help the API identify the voter.
    """

    previous_last_name: EmptyStrNone = px.element(
        "previousreglastname", default=None, max_length=30
    )
    """If the application includes a name change, the previous last name."""

    previous_first_name: EmptyStrNone = px.element(
        "previousregfirstname", default=None, max_length=30
    )
    """If the application includes a name change, the previous first name."""

    previous_middle_name: EmptyStrNone = px.element(
        "previousregmiddlename", default=None, max_length=30
    )
    """If the application includes a name change, the previous middle name."""

    previous_address: EmptyStrNone = px.element(
        "previousregaddress", default=None, max_length=100
    )
    """If the application includes an address change, the previous address."""

    previous_city: EmptyStrNone = px.element(
        "previousregcity", default=None, max_length=30
    )
    """If the application includes an address change, the previous city."""

    previous_state: EmptyStrNone = px.element(
        "previousregstate", default=None, max_length=2
    )
    """If the application includes an address change, the previous state."""

    previous_zip5: EmptyStrNone = px.element(
        "previousregzip", default=None, max_length=5
    )
    """If the application includes an address change, the previous ZIP code."""

    previous_year: str | None = px.element(
        "previousregyear", default=None, min_length=4, max_length=4
    )
    """If the application includes an address change, the previous year."""

    @p.model_validator(mode="after")
    def validate_previous_name(self) -> t.Self:
        """Ensure that previous names are set if the app includes a name change."""
        values = (
            self.previous_last_name,
            self.previous_first_name,
        )
        if self.is_name_change:
            if not all(values):
                raise ValueError("Previous name fields must be set for a name change.")
        else:
            if any(values):
                raise ValueError("No previous name fields should be set.")
        return self

    @p.model_validator(mode="after")
    def validate_previous_address(self) -> t.Self:
        """Ensure that previous addr fields are set if the app includes a change."""
        values = (
            self.previous_address,
            self.previous_city,
            self.previous_zip5,
        )
        if self.is_address_change:
            if not all(values):
                raise ValueError(
                    "Previous address fields must be set for an address change."
                )
        else:
            if any(values):
                raise ValueError("No previous address fields should be set.")
        return self

    @p.field_validator("previous_zip5", mode="after")
    def validate_previous_zip5_has_county(cls, value: str | None) -> str | None:
        """Ensure that the previous ZIP code has a corresponding county."""
        if value is None:
            return None
        if get_county_choice(value) is None:
            raise ValueError(f"Unknown county for previous ZIP code {value}")
        return value

    @px.computed_element(tag="previousregcounty")  # type: ignore
    def previous_county(self) -> CountyChoice | None:
        """Return the county for the given ZIP code."""
        if self.previous_zip5 is None:
            return None
        # Annoyingly needed to convince type checkers that all is well:
        assert self.previous_zip5 is not None
        choice = get_county_choice(self.previous_zip5)
        if choice is None:
            raise ValueError(
                f"Unknown county for previous ZIP code {self.previous_zip5}"
            )
        return choice


class VoterAbout(px.BaseXmlModel, frozen=True):
    """05 - Information about the voter for a voter registration application."""

    birth_date: PARequestDate = px.element(tag="DateOfBirth")

    gender: GenderChoice | None = px.element(tag="Gender", default=None)
    """Optional gender. (Some PA docs use the term 'sex', some use 'gender')."""

    race: RaceChoice | None = px.element("Ethnicity", default=None)
    """Optional ethnicity. (Some PA docs use the term 'race', some 'ethnicity')."""

    phone: PhoneNumber | None = px.element(
        tag="Phone", default=None, min_length=12, max_length=12
    )
    email: p.EmailStr | None = px.element(tag="Email", max_length=50, default=None)


class VoterAddress(px.BaseXmlModel, frozen=True):
    """06 - Address information for a voter registration application."""

    address: str = px.element(tag="streetaddress", max_length=40)
    address_2: str | None = px.element(
        tag="streetaddress2", default=None, max_length=40
    )
    unit_type: UnitTypeChoice | None = px.element(tag="unittype", default=None)
    unit_number: str | None = px.element(tag="unitnumber", default=None, max_length=15)
    city: str = px.element(tag="city", max_length=35)
    zip5: str = px.element(tag="zipcode", max_length=5, min_length=5)

    # FUTURE: make `unit_type` and `unit_number` computed fields, based on the
    # contents of the address lines themselves. Otherwise it's just weirdness?

    @p.field_validator("zip5", mode="after")
    def validate_zip5_has_county(cls, value: str) -> str:
        """Ensure that the ZIP code has a corresponding county."""
        if get_county_choice(value) is None:
            raise ValueError(f"Unknown county for ZIP code {value}")
        return value

    @px.computed_element(tag="county")  # type: ignore
    def county(self) -> CountyChoice:
        """Return the county for the given ZIP code."""
        choice = get_county_choice(self.zip5)
        if choice is None:
            raise ValueError(f"Unknown county for ZIP code {self.zip5}")
        return choice


class VoterMailingAddress(px.BaseXmlModel, frozen=True):
    """07 - Mailing address information for a voter registration application."""

    no_street_permanent: Bit = px.element(
        tag="donthavePermtOrResAddress", default=False
    )
    """If True, voter does not have a street address or permanent residence."""

    mailing_address: str | None = px.element(
        tag="mailingaddress", default=None, max_length=40
    )
    """Optional mailing address for the voter if no_street_permanent is set."""

    mailing_city: str | None = px.element(
        tag="mailingcity", default=None, max_length=35
    )
    """Optional mailing city for the voter if no_street_permanent is set."""

    mailing_state: str | None = px.element(
        tag="mailingstate", default=None, max_length=2
    )
    """Optional mailing state for the voter if no_street_permanent is set."""

    mailing_zipcode: str | None = px.element(
        tag="mailingzipcode", default=None, max_length=10
    )
    """
    Optional mailing ZIP code for the voter if no_street_permanent is set.
    
    Unlike the primary ZIP code, this field can be longer than 5 characters.
    :shrug-emoji: 
    """

    @p.model_validator(mode="after")
    def validate_mailing_address(self) -> t.Self:
        """Ensure that all mailing address fields are set if any are set."""
        values = (
            self.mailing_address,
            self.mailing_city,
            self.mailing_state,
            self.mailing_zipcode,
        )
        if self.no_street_permanent:
            if not all(values):
                raise ValueError("All mailing fields must be set if any are set.")
        else:
            if any(values):
                raise ValueError(
                    "No mailing fields should be set if no_street_permanent is False."
                )
        return self


class VoterIdentification(px.BaseXmlModel, frozen=True):
    """08 - Identification information for a voter registration application."""

    drivers_license: str | None = px.element(
        "drivers-license", default=None, max_length=8
    )
    """The voter's PA driver's license number *or* PennDOT id card number."""

    ssn4: str | None = px.element("ssn4", default=None, max_length=4, min_length=4)
    """The last 4 digits of the voter's Social Security Number."""

    @px.computed_element(tag="donthavebothDLandSSN")  # type: ignore
    def no_identification(self) -> Bit:
        """Return True if the voter has neither a driver's license nor an SSN."""
        return self.drivers_license is None and self.ssn4 is None

    signature: SignatureImage | None = px.element("signatureimage", default=None)
    """The voter's signature image."""

    @px.computed_element(tag="continueAppSubmit")  # type: ignore
    def continue_submit(self) -> Bit:
        """
        Return True if the application can continue a previous failed app.

        XXX The API documentation is a little fuzzy here; we should clarify. It
        specifically says that this is required to complete the application
        if a previous PennDOT DL or ID fails.
        """
        return self.drivers_license is None

    @p.model_validator(mode="after")
    def validate_identification(self) -> t.Self:
        """Ensure that API rules are met."""
        if self.drivers_license is not None:
            if any((self.ssn4, self.signature)):
                raise ValueError(
                    "SSNs and signatures are not allowed if a DL is provided."
                )
        elif self.ssn4 is not None:
            if self.signature is not None:
                raise ValueError("Signatures are not allowed if an SSN is provided.")
        elif self.signature is None:
            raise ValueError(
                "A signature is required if no identification is provided."
            )
        elif (
            self.drivers_license is None
            and self.ssn4 is None
            and self.signature is None
        ):
            raise ValueError("At least one form of identification must be supplied.")
        return self


class VoterPoliticalParty(px.BaseXmlModel, frozen=True):
    """09 - Political party information for a voter registration application."""

    political_party: PoliticalPartyChoice = px.element(tag="politicalparty")
    """The political party of the voter."""

    other_party: str | None = px.element(tag="otherpoliticalparty", default=None)
    """The name of the political party if 'Other' is selected."""

    # Validate that `other_party` is set if `political_party` is `OTHER`.
    @p.model_validator(mode="after")
    def validate_other_party(self) -> t.Self:
        """Ensure that `other_party` is set if `political_party` is `OTHER`."""
        if (self.political_party == PoliticalPartyChoice.OTHER) ^ (
            self.other_party is not None
        ):
            raise ValueError(
                "`other_party` must (only) be set if `political_party` is `OTHER`"
            )
        return self


class VoterAssistance(px.BaseXmlModel, frozen=True):
    """10 - Assistance information for a voter registration application."""

    require_help_to_vote: Bit = px.element(tag="needhelptovote", default=False)
    """Whether the voter requires assistance to vote."""

    # If require_help_to_vote is True, this must also be set.
    assistance_type: AssistanceTypeChoice | None = px.element(
        tag="typeofassistance", default=None
    )
    """The type of assistance needed by the voter."""

    # Despite the fact that not all assistance types require a language, the API
    # requires this to be set if require_help_to_vote is True.
    preferred_language: str | None = px.element(tag="preferredlanguage", default=None)
    """The preferred language of the voter."""

    @p.model_validator(mode="after")
    def validate_assistance(self) -> t.Self:
        """Ensure that all assistance fields are set if any are set."""
        values = (self.assistance_type, self.preferred_language)
        if self.require_help_to_vote:
            if not all(values):
                raise ValueError("All assistance fields must be set if any are set.")
        else:
            if any(values):
                raise ValueError("No assistance fields should be set if not needed.")
        return self


class VoterChangedInfo(px.BaseXmlModel, frozen=True):
    """11 - Changed information for a voter registration application."""

    # The implementation for this section of the API docs is
    # handled by VoterReason, since the validation required combines
    # both section 04 and section 11.

    pass


class VoterDeclaration(px.BaseXmlModel, frozen=True):
    """12 - Declaration information for a voter registration application."""

    confirm_declaration: TrueBit = px.element(tag="declaration1")
    """
    The voter's confirmation of the declaration.

    The declaration is provided by the *SETUP API call as `ovr_app_declaration`.
    """


class VoterHelpWithForm(px.BaseXmlModel, frozen=True):
    """13 - Help with form information for a voter registration application."""

    assistant_name: str | None = px.element(
        tag="assistedpersonname", max_length=100, default=None
    )
    """The name of the person who assisted the voter in filling out the form."""

    assistant_address: str | None = px.element(
        tag="assistedpersonAddress", max_length=100, default=None
    )
    """The address of the person who assisted the voter in filling out the form."""

    assistant_phone: PhoneNumber | None = px.element(
        tag="assistedpersonphone", max_length=15, default=None
    )

    assistant_declaration: TrueBit | None = px.element(
        tag="assistancedeclaration2", default=None
    )
    """
    The assistant's confirmation of the declaration.

    The declaration is provided by the *SETUP API call as `ovr_assistance_declaration`.
    """

    @p.model_validator(mode="after")
    def ensure_assistant_fields(self) -> t.Self:
        """Ensure that all assistant fields are set if any are set."""
        values = (
            self.assistant_name,
            self.assistant_address,
            self.assistant_phone,
            self.assistant_declaration,
        )
        if any(values) and not all(values):
            raise ValueError("All assistant fields must be set if any are set.")

        return self


class VoterPollWorker(px.BaseXmlModel, frozen=True):
    """14 - Poll worker information for a voter registration application."""

    be_poll_worker: Bit | None = px.element(tag="ispollworker", default=None)
    """If True, the voter wants to be a poll worker on election day."""

    be_interpreter: Bit | None = px.element(tag="bilingualinterpreter", default=None)
    """If True, the voter wants to be a bilingual interpreter on election day."""

    interpreter_language: str | None = px.element(
        tag="pollworkerspeaklang", default=None, max_length=50
    )
    """The language the voter speaks if they want to be a bilingual interpreter."""

    @p.model_validator(mode="after")
    def validate_interpreter(self) -> t.Self:
        """Ensure that interpreter fields are set if any are set."""
        if self.be_interpreter:
            if not self.interpreter_language:
                raise ValueError(
                    "An interpreter language is required if `be_interpreter`"
                )
        else:
            if self.interpreter_language:
                raise ValueError(
                    "`interpreter_language` is only allowed if `be_interpreter`"
                )
        return self


class VoterSecondEmailID(px.BaseXmlModel, frozen=True):
    """15 - Second email ID information for a voter registration application."""

    alternate_email: p.EmailStr | None = px.element(
        tag="secondEmail", max_length=50, default=None
    )


class VoterTransferPermanentStatusFlag(px.BaseXmlModel, frozen=True):
    """16 - Transfer Permanent Status Flag information for a voter reg application."""

    transfer_permanent_status: Bit | None = px.element(
        tag="istransferpermanent", default=None
    )
    """
    If True, the voter would like their 'permanent status' transferred to 
    their new county of residence when doing a change of address registration.
    """


class VoterMailInBallot(px.BaseXmlModel, frozen=True):
    """17 - Mail-In Ballot information for a voter registration application."""

    is_mail_in: Bit | None = px.element(tag="ismailinballot", default=None)
    """If True, the voter would like to receive a mail-in ballot."""

    mail_in_address_type: MailInAddressTypeChoice | None = px.element(
        tag="mailinaddresstype", default=None
    )
    """The type of mail-in address the voter would like to use."""

    mail_in_address: str | None = px.element(
        tag="mailinballotaddr", default=None, max_length=40
    )
    """The street address where a mail-in ballot should be mailed."""

    mail_in_city: str | None = px.element(tag="mailincity", default=None, max_length=35)
    """The city where a mail-in ballot should be mailed."""

    mail_in_state: str | None = px.element(
        tag="mailinstate", default=None, max_length=2
    )
    """The state where a mail-in ballot should be mailed."""

    mail_in_zipcode: str | None = px.element(
        tag="mailinzipcode", default=None, max_length=10
    )
    """The ZIP code where a mail-in ballot should be mailed."""

    mail_in_ward: str | None = px.element(tag="mailinward", default=None, max_length=50)
    """The ward where a mail-in ballot should be mailed."""

    mail_in_lived_since: PARequestDate | None = px.element(
        tag="mailinlivedsince", default=None
    )
    """
    The year the voter started living at the mail-in address.
    
    TODO: verify that this is actually what's expected here; the documentation
    is not at all helpful.
    """

    mail_in_declaration: TrueBit | None = px.element(
        tag="mailindeclaration", default=None
    )
    """
    The voter's confirmation of the mail-in ballot declaration.

    The declaration is provided by the *SETUP API call as `mail_in_declaration`.
    """

    @p.model_validator(mode="after")
    def validate_mail_in_address(self) -> t.Self:
        """Ensure that all mail-in address fields are set if any are set."""
        values = (
            self.mail_in_address_type,
            self.mail_in_address,
            self.mail_in_city,
            self.mail_in_state,
            self.mail_in_zipcode,
            # mail_in_ward is not required according to the API docs
            self.mail_in_lived_since,
            self.mail_in_declaration,
        )
        if self.is_mail_in:
            if not all(values):
                raise ValueError("All mail-in fields must be set if any are set.")
        else:
            if any(values):
                raise ValueError(
                    "No mail-in fields should be set if `is_mail_in` is False."
                )
        return self


class VoterApplicationRecord(
    VoterMailInBallot,
    VoterTransferPermanentStatusFlag,
    VoterSecondEmailID,
    VoterPollWorker,
    VoterHelpWithForm,
    VoterDeclaration,
    VoterChangedInfo,
    VoterAssistance,
    VoterPoliticalParty,
    VoterIdentification,
    VoterMailingAddress,
    VoterAddress,
    VoterAbout,
    VoterReason,
    VoterEligibility,
    VoterName,
    VoterBatch,
    tag="record",
    nsmap=NSMAP,
    frozen=True,
    search_mode="unordered",
):
    """A record for a voter registration application."""

    # NOTE: the inheritance order is important here. The API expects
    # the elements to be in a specific order, so we need to ensure that
    # the elements are defined in the correct order in the class definition.

    pass


class VoterApplication(
    px.BaseXmlModel,
    tag="APIOnlineApplicationData",
    nsmap=NSMAP,
    frozen=True,
):
    """A full voter registration application for the Pennsylvania OVR API."""

    record: VoterApplicationRecord
    """Silly, needless nesting in the API request structure. So be it."""


# -----------------------------------------------------------------------------
# API Verbs (what the PA API documentation calls "Actions")
# -----------------------------------------------------------------------------


class Action(str, Enum):
    """
    Enumeration of actions that can be taken against the Pennsylvania OVR API.

    The API has a single URL endpoint, which accepts a variety of so-called
    "actions" that determine what the API should do.
    """

    GET_APPLICATION_SETUP = "GETAPPLICATIONSETUP"
    """Get the possible values for a voter reg + optional mail-in ballot app."""

    GET_BALLOT_APPLICATION_SETUP = "GETBALLOTAPPLICATIONSETUP"
    """Get the possible values for a mail-in ballot app."""

    GET_LANGUAGES = "GETLANGUAGES"
    """Get the available languages for the PA OVR API."""

    GET_XML_TEMPLATE = "GETXMLTEMPLATE"
    """Get XML tags and format for voter registration + optional mail-in ballot app."""

    GET_BALLOT_XML_TEMPLATE = "GETBALLOTXMLTEMPLATE"
    """Get XML tags and format for mail-in ballot app."""

    GET_ERROR_VALUES = "GETERRORVALUES"
    """Get the possible error values for the PA OVR API."""

    GET_MUNICIPALITIES = "GETMUNICIPALITIES"
    """Get the available municipalities in a given county."""

    SET_APPLICATION = "SETAPPLICATION"
    """Submit a voter registration + optional mail-in ballot app."""

    SET_BALLOT_APPLICATION = "SETBALLOTAPPLICATION"
    """Submit a mail-in ballot app."""


# -----------------------------------------------------------------------------
# Client implementation
# -----------------------------------------------------------------------------


class PennsylvaniaAPIClient:
    """Client for speaking with the Pennsylvania online voter (OVR) API."""

    api_url: str
    api_key: str
    language: int
    _client: httpx.Client

    def __init__(
        self,
        api_url: str,
        api_key: str,
        *,
        language: int = 0,
        timeout: float = 5.0,
        # Lower-level parameter for test and debug purposes
        _transport: httpx.BaseTransport | None = None,
    ):
        """Create a new client for the Pennsylvania OVR API."""
        self.api_url = api_url
        self.api_key = api_key
        self.language = language
        mounts = {"all://": _transport} if _transport else None
        self._client = httpx.Client(mounts=mounts, timeout=timeout)

    @classmethod
    def staging(
        cls, api_key: str, *, language: int = 0, timeout: float = 5.0, **kwargs
    ):
        """Create a new client for the Pennsylvania OVR API in staging."""
        return cls(STAGING_URL, api_key, language=language, timeout=timeout, **kwargs)

    @classmethod
    def production(
        cls, api_key: str, *, language: int = 0, timeout: float = 5.0, **kwargs
    ):
        """Create a new client for the Pennsylvania OVR API in production."""
        return cls(
            PRODUCTION_URL, api_key, language=language, timeout=timeout, **kwargs
        )

    def build_url(self, action: Action, params: dict | None = None) -> str:
        """Build a URL for the given action and parameters."""
        query = {
            "AuthKey": self.api_key,
            "action": action.value,
            "Language": self.language,
            **(params or {}),
        }

        query_prefix = {f"sysparm_{k}": v for k, v in query.items()}
        encoded = urlencode(query_prefix)
        return f"{self.api_url}?JSONv2&{encoded}"

    def _get(self, action: Action, params: dict | None = None) -> str:
        """Perform a raw GET request to the Pennsylvania OVR API."""
        url = self.build_url(action, params)
        try:
            response = self._client.get(url, headers={"Cache-Control": "no-cache"})
            response.raise_for_status()
        except httpx.TimeoutException as e:
            raise TimeoutError() from e
        except httpx.RequestError as e:
            raise ServiceUnavailableError(
                "Generic network error. Please try again later."
            ) from e
        except httpx.HTTPStatusError as e:
            raise ServiceUnavailableError(
                "Unexpected response. Please try again later."
            ) from e
        try:
            return response.json()
        except Exception as e:
            raise UnparsableResponseError("Invalid JSON returned.") from e

    def _post(
        self,
        action: Action,
        data: XmlElement | str,  # type: ignore
        params: dict | None = None,
    ) -> str:
        """Perform a raw POST request to the Pennsylvania OVR API."""
        url = self.build_url(action)
        if isinstance(data, XmlElement):
            data_str = xml_tostring(data, encoding="unicode")  # type: ignore
            assert isinstance(data_str, str)
            # XXX this is no fun -- the API doesn't *really*
            # accept xml, because if it did, this would not be necessary.
            # Instead, the API accepts a *very specific variant* of XML
            # where the namespaces are just-so. And I can't figure out how
            # to produce that variant from pydantic-xml. So we're doing this.
            data_str = data_str.replace("ns0:", "").replace(":ns0=", "=")
        else:
            data_str = data

        assert isinstance(data_str, str), f"DATA was an unexpected type: {type(data)}"

        data_jsonable = {"ApplicationData": data_str}
        try:
            response = self._client.post(
                url,
                json=data_jsonable,
                headers={"Cache-Control": "no-cache"},
            )
            response.raise_for_status()
        except httpx.TimeoutException as e:
            raise TimeoutError() from e
        except httpx.RequestError as e:
            raise ServiceUnavailableError(
                "Generic network error. Please try again later."
            ) from e
        except httpx.HTTPStatusError as e:
            raise APIError("Unexpected status code. Please try again later.") from e
        try:
            return response.json()
        except Exception as e:
            raise UnparsableResponseError("Invalid JSON returned.") from e

    def invoke(
        self,
        action: Action,
        data: XmlElement | str | None = None,
        params: dict | None = None,
    ) -> XmlElement:
        """
        Invoke an action on the Pennsylvania OVR API.

        Look for errors in the response and raise an exception if one is found.
        """
        raw = (
            self._get(action, params)
            if data is None
            else self._post(action, data, params)
        )
        try:
            # print("RAW RESPONSE: ", raw)
            return xml_fromstring(raw)  # type: ignore
        except Exception as e:
            raise UnparsableResponseError("Invalid XML returned.") from e

    def get_application_setup(self) -> SetupResponse:
        """Get the possible values for a voter reg + optional mail-in ballot app."""
        data = self.invoke(Action.GET_APPLICATION_SETUP)
        try:
            return SetupResponse.from_xml_tree(data)
        except (px.ParsingError, p.ValidationError) as e:
            raise UnparsableResponseError("Invalid schema returned.") from e

    def get_ballot_application_setup(self) -> SetupResponse:
        """Get the possible values for a mail-in ballot app."""
        data = self.invoke(Action.GET_BALLOT_APPLICATION_SETUP)
        try:
            return SetupResponse.from_xml_tree(data)
        except (px.ParsingError, p.ValidationError) as e:
            raise UnparsableResponseError("Invalid schema returned.") from e

    def get_languages(self) -> LanguagesResponse:
        """Get the available languages for the PA OVR API."""
        data = self.invoke(Action.GET_LANGUAGES)
        try:
            return LanguagesResponse.from_xml_tree(data)
        except (px.ParsingError, p.ValidationError) as e:
            raise UnparsableResponseError("Invalid schema returned.") from e

    def get_xml_template(self) -> XmlElement:
        """Get XML tags and format for voter reg + optional mail-in ballot app."""
        return self.invoke(Action.GET_XML_TEMPLATE)

    def get_ballot_xml_template(self) -> XmlElement:
        """Get XML tags and format for mail-in ballot app."""
        return self.invoke(Action.GET_BALLOT_XML_TEMPLATE)

    def get_error_values(self) -> ErrorValuesResponse:
        """Get the possible error values for the PA OVR API."""
        data = self.invoke(Action.GET_ERROR_VALUES)
        try:
            return ErrorValuesResponse.from_xml_tree(data)
        except (px.ParsingError, p.ValidationError) as e:
            raise UnparsableResponseError("Invalid schema returned.") from e

    def get_municipalities(self, county: str) -> MunicipalitiesResponse:
        """Get the available municipalities in a given county."""
        data = self.invoke(Action.GET_MUNICIPALITIES, params={"County": county})
        try:
            return MunicipalitiesResponse.from_xml_tree(data)
        except (px.ParsingError, p.ValidationError) as e:
            raise UnparsableResponseError("Invalid schema returned.") from e

    def set_application(
        self, application: VoterApplication, raise_validation_error: bool = True
    ) -> APIResponse:
        """
        Submit a voter registration + optional mail-in ballot app.

        If the PA API returns a response with a validation error, and
        `raise_validation_error` is True, this method will raise an exception.
        Otherwise, the response will be returned as-is.
        """
        xml_tree = application.to_xml_tree()
        data = self.invoke(Action.SET_APPLICATION, data=xml_tree)
        try:
            api_response = APIResponse.from_xml_tree(data)
        except (px.ParsingError, p.ValidationError) as e:
            raise UnparsableResponseError("Invalid schema returned.") from e
        # CONSIDER allowing callers to decide whether to raise here or not.
        if raise_validation_error:
            api_response.raise_for_error()
            assert not api_response.has_error()
        return api_response

    def set_ballot_application(
        self, application: VoterApplication, raise_validation_error: bool = True
    ) -> APIResponse:
        """
        Submit a mail-in ballot app.

        If the PA API returns a response with a validation error, and
        `raise_validation_error` is True, this method will raise an exception.
        Otherwise, the response will be returned as-is.
        """
        data = self.invoke(
            Action.SET_BALLOT_APPLICATION, data=application.to_xml_tree()
        )
        try:
            api_response = APIResponse.from_xml_tree(data)
        except (px.ParsingError, p.ValidationError) as e:
            raise UnparsableResponseError("Invalid schema returned.") from e
        if raise_validation_error:
            api_response.raise_for_error()
            assert not api_response.has_error()
        return api_response
