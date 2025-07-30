"""Tools for working with voter registration data."""

from .ga import GeorgiaCheckRegistrationTool
from .mi import MichiganCheckRegistrationTool
from .pa.check import PennsylvaniaCheckRegistrationTool
from .pa.client import PennsylvaniaAPIClient
from .tool import CheckRegistrationTool
from .wi import WisconsinCheckRegistrationTool
from .zipcodes import get_state

_CHECK_TOOLS: dict[str, type[CheckRegistrationTool]] = {
    "GA": GeorgiaCheckRegistrationTool,
    "MI": MichiganCheckRegistrationTool,
    "PA": PennsylvaniaCheckRegistrationTool,
    "WI": WisconsinCheckRegistrationTool,
}


def get_check_tool(
    *, zipcode: str | None = None, state: str | None = None
) -> CheckRegistrationTool | None:
    """Return a voter registration tool for the given ZIP code or state."""
    if state is None:
        if zipcode is None:
            raise ValueError("Must provide either a ZIP code or state")
        state = get_state(zipcode)

    if state is None:
        return None

    tool_class = _CHECK_TOOLS.get(state)
    return tool_class() if tool_class else None


# TODO FUTURE: consider whether there's *any* kind of common interface
# between OVR API clients for different states. For now, we just have
# Pennsylvania, so there's no point in trying to generalize.


__all__ = [
    "get_check_tool",
    "PennsylvaniaAPIClient",
]
