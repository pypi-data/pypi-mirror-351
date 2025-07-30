class VoterToolsError(Exception):
    """Base class for all voter tools errors."""

    pass


class CheckRegistrationError(Exception):
    """An error occurred while checking voter registration."""

    pass


class MultipleRecordsFoundError(CheckRegistrationError):
    """Multiple voters were found matching the given information."""

    pass


class APIError(Exception):
    """Base class for all API errors."""

    pass
