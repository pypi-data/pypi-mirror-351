#!/usr/bin/env python

import csv
import datetime
import os
import pathlib
import sys
import typing as t
from xml.etree import ElementTree as ET

import click

from . import PennsylvaniaAPIClient, get_check_tool
from .pa.debug import CurlDebugTransport


@click.group()
@click.version_option()
def vote():
    """Command-line tool for working with voter data."""
    pass


@vote.command()
@click.argument("first_name", type=str, required=True)
@click.argument("last_name", type=str, required=True)
@click.argument("zipcode", type=str, required=True)
@click.argument("birthday", type=click.DateTime(), required=True)
@click.option(
    "--details", is_flag=True, default=False, help="Return detailed information."
)
def check(
    first_name: str,
    last_name: str,
    zipcode: str,
    birthday: datetime.date,
    details: bool = False,
) -> None:
    """Check if a single person is registered to vote."""
    tool = get_check_tool(zipcode=zipcode)
    if tool is None:
        print(f"Error: unsupported state for zipcode {zipcode}.")
        sys.exit(1)
    result = tool.check_registration(first_name, last_name, zipcode, birthday, details)
    if result.registered:
        print(f"{first_name} {last_name} is registered to vote in {tool.state}.")
        if details and result.details:
            print(result.details.model_dump_json(indent=2))
    else:
        print(f"{first_name} {last_name} is not registered to vote in {tool.state}.")


@vote.command()
@click.argument("csv_path", type=click.Path(exists=True))
@click.option(
    "--details", is_flag=True, default=False, help="Return detailed information."
)
@click.option(
    "-f",
    "--first-name",
    "first_name_header",
    type=str,
    default="First Name",
    help="Name of the 'First Name' column.",
)
@click.option(
    "-l",
    "--last-name",
    "last_name_header",
    type=str,
    default="Last Name",
    help="Name of the 'Last Name' column.",
)
@click.option(
    "-d",
    "--dob",
    "dob_header",
    type=str,
    default="Date of Birth",
    help="Name of the 'Date of Birth' column.",
)
@click.option(
    "-z",
    "--zipcode",
    "zipcode_header",
    type=str,
    default="Zipcode",
    help="Name of the 'Zipcode' column.",
)
@click.option(
    "-r",
    "--registered",
    "registered_header",
    type=str,
    default="Registered",
    help="Name of the 'Registered' column.",
)
@click.option(
    "--registration-date",
    "registration_date_header",
    type=str,
    default="Registration Date",
    help="Name of the 'Registration Date' column.",
)
@click.option(
    "--registration-status",
    "registration_status_header",
    type=str,
    default="Registration Status",
    help="Name of the 'Registration Status' column.",
)
@click.option(
    "--state-voter-id",
    "state_voter_id_header",
    type=str,
    default="State Voter ID",
    help="Name of the 'State Voter ID' column.",
)
def check_csv(
    csv_path: pathlib.Path,
    details: bool = False,
    first_name_header: str = "First Name",
    last_name_header: str = "Last Name",
    dob_header: str = "Date of Birth",
    zipcode_header: str = "Zipcode",
    registered_header: str = "Registered",
    registration_date_header: str = "Registration Date",
    registration_status_header: str = "Registration Status",
    state_voter_id_header: str = "State Voter ID",
) -> None:
    """
    Check if multiple people are registered to vote.

    Output a new CSV. If `details` is False, a single column is added to the CSV
    indicating whether the person is registered to vote.

    If `details` is True, additional columns are added including registration
    date and state voter ID, if known.
    """
    extra_fields = [registered_header]
    if details:
        extra_fields += [
            registration_date_header,
            registration_status_header,
            state_voter_id_header,
        ]

    with open(csv_path, "r") as f:
        # Read the CSV file and begin the new output CSV
        reader = csv.DictReader(f)
        if not reader.fieldnames:
            raise ValueError("Invalid CSV format: missing header row.")
        field_names = list(reader.fieldnames) + extra_fields
        writer = csv.DictWriter(sys.stdout, fieldnames=field_names)
        writer.writeheader()

        for row in reader:
            # Read the relevant cells from the row
            try:
                first_name, last_name, dob_str, zipcode = (
                    row[first_name_header],
                    row[last_name_header],
                    row[dob_header],
                    row[zipcode_header],
                )
                dob = datetime.datetime.strptime(dob_str, "%Y-%m-%d").date()
            except (KeyError, ValueError) as e:
                raise ValueError(
                    "Invalid CSV format: unable to parse required fields."
                ) from e

            # Add default values for the new details columns, if needed
            if details:
                row[registration_date_header] = ""
                row[registration_status_header] = ""
                row[state_voter_id_header] = ""

            # Get the registration tool for the given ZIP code
            tool = get_check_tool(zipcode=zipcode)

            # Handle unsupported states
            if tool is None:
                row["Registered"] = "(unsupported state)"
                continue

            # Check the registration status for this voter
            result = tool.check_registration(
                first_name, last_name, zipcode, dob, details
            )

            # Finish quickly if the voter is not registered
            if not result.registered:
                row[registered_header] = False
                writer.writerow(row)
                continue

            # Update the row with the registration status and details if requested
            row[registered_header] = True
            if details and result.details:
                row[registration_date_header] = (
                    result.details.registration_date.strftime("%Y-%m-%d")
                )
                row[registration_status_header] = result.details.status
                row[state_voter_id_header] = result.details.state_id

            writer.writerow(row)


@vote.group()
def pa():
    """Commands for working with Pennsylvania voter registration."""
    pass


def _pa_api_key() -> str:
    API_KEY = os.environ.get("PA_API_KEY")
    if not API_KEY:
        raise ValueError("PA_API_KEY environment variable must be set.")
    return API_KEY


@pa.command()
def get_application_setup():
    """Get the application setup."""
    client = PennsylvaniaAPIClient.staging(_pa_api_key())
    setup = client.get_application_setup()
    print(setup)


@pa.command()
def get_ballot_application_setup():
    """Get the mail-in ballot setup."""
    client = PennsylvaniaAPIClient.staging(_pa_api_key())
    setup = client.get_ballot_application_setup()
    print(setup)


@pa.command()
def get_languages():
    """Get the languages."""
    client = PennsylvaniaAPIClient.staging(_pa_api_key())
    languages = client.get_languages()
    print(languages)


@pa.command()
def get_xml_template():
    """Get the XML template."""
    client = PennsylvaniaAPIClient.staging(_pa_api_key())
    template = client.get_xml_template()
    ET.indent(template)
    ET.dump(template)


@pa.command()
def get_ballot_xml_template():
    """Get the ballot XML template."""
    client = PennsylvaniaAPIClient.staging(_pa_api_key())
    template = client.get_ballot_xml_template()
    ET.indent(template)
    ET.dump(template)


@pa.command()
def get_error_values():
    """Get the error values."""
    client = PennsylvaniaAPIClient.staging(_pa_api_key())
    errors = client.get_error_values()
    print(errors)


@pa.command()
@click.argument("county")
def get_municipalities(county: str):
    """Get the municipalities for the given county."""
    client = PennsylvaniaAPIClient.staging(_pa_api_key())
    municipalities = client.get_municipalities(county)
    print(municipalities)


@pa.command()
@click.option("--xml", type=click.File("r"))
@click.option("--timeout", type=float, default=100.0, help="Timeout in seconds.")
@click.option(
    "--debug-curl",
    is_flag=True,
    default=False,
    help="Display the request as a CURL command.",
)
def set_xml_application(xml: t.TextIO, timeout: float, debug_curl: bool):
    """Validate an arbitrary XML application structure and submit it if valid."""
    from .pa.client import VoterApplication

    xml_str = xml.read()
    application = VoterApplication.from_xml(xml_str)
    transport = (
        CurlDebugTransport(click.get_text_stream("stdout")) if debug_curl else None
    )
    client = PennsylvaniaAPIClient.staging(
        _pa_api_key(), timeout=timeout, _transport=transport
    )
    response = client.set_application(application)
    print(response)


@pa.command()
def set_test_application():
    """Submit a test application with test data."""
    import datetime

    from .pa.client import (
        BatchMode,
        GenderChoice,
        PoliticalPartyChoice,
        RegistrationKind,
        VoterApplication,
        VoterApplicationRecord,
    )

    ar = VoterApplicationRecord(
        batch=BatchMode.ALL_ERRORS,
        first_name="Test",
        last_name="Applicant1",
        is_us_citizen=True,
        will_be_18=True,
        political_party=PoliticalPartyChoice.DEMOCRATIC,
        gender=GenderChoice.MALE,
        email="test.applicant1@example.com",
        birth_date=datetime.date(1980, 1, 1),
        registration_kind=RegistrationKind.NEW,
        confirm_declaration=True,
        address="123 Main St",
        city="Philadelphia",
        zip5="19127",
        drivers_license="12345678",
    )
    application = VoterApplication(record=ar)

    client = PennsylvaniaAPIClient.staging(_pa_api_key())
    response = client.set_application(application)
    print(response)


if __name__ == "__main__":
    vote()
