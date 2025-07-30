import pathlib
import typing as t
from datetime import date

import httpx
from user_agent import generate_user_agent

from ..errors import CheckRegistrationError
from ..tool import CheckRegistrationResult, CheckRegistrationTool, SupportedFeatures
from ..zipcodes import get_county

COUNTY_TO_CODE = {
    "ADAMS": "2290",
    "ALLEGHENY": "2291",
    "ARMSTRONG": "2292",
    "BEAVER": "2293",
    "BEDFORD": "2294",
    "BERKS": "2295",
    "BLAIR": "2296",
    "BRADFORD": "2297",
    "BUCKS": "2298",
    "BUTLER": "2299",
    "CAMBRIA": "2300",
    "CAMERON": "2301",
    "CARBON": "2302",
    "CENTRE": "2303",
    "CHESTER": "2304",
    "CLARION": "2305",
    "CLEARFIELD": "2306",
    "CLINTON": "2307",
    "COLUMBIA": "2308",
    "CRAWFORD": "2309",
    "CUMBERLAND": "2310",
    "DAUPHIN": "2311",
    "DELAWARE": "2312",
    "ELK": "2313",
    "ERIE": "2314",
    "FAYETTE": "2315",
    "FOREST": "2316",
    "FRANKLIN": "2317",
    "FULTON": "2318",
    "GREENE": "2319",
    "HUNTINGDON": "2320",
    "INDIANA": "2321",
    "JEFFERSON": "2322",
    "JUNIATA": "2323",
    "LACKAWANNA": "2324",
    "LANCASTER": "2325",
    "LAWRENCE": "2326",
    "LEBANON": "2327",
    "LEHIGH": "2328",
    "LUZERNE": "2329",
    "LYCOMING": "2330",
    "McKEAN": "2331",
    "MERCER": "2332",
    "MIFFLIN": "2333",
    "MONROE": "2334",
    "MONTGOMERY": "2335",
    "MONTOUR": "2336",
    "NORTHAMPTON": "2337",
    "NORTHUMBERLAND": "2338",
    "PERRY": "2339",
    "PHILADELPHIA": "2340",
    "PIKE": "2341",
    "POTTER": "2342",
    "SCHUYLKILL": "2343",
    "SNYDER": "2344",
    "SOMERSET": "2345",
    "SULLIVAN": "2346",
    "SUSQUEHANNA": "2347",
    "TIOGA": "2348",
    "UNION": "2349",
    "VENANGO": "2350",
    "WARREN": "2351",
    "WASHINGTON": "2352",
    "WAYNE": "2353",
    "WESTMORELAND": "2354",
    "WYOMING": "2355",
    "YORK": "2356",
}


def get_county_code(zipcode: str) -> str | None:
    """Get the county code for a Pennsylvania ZIP code."""
    county = get_county(zipcode)
    if not county:
        return None
    return COUNTY_TO_CODE.get(county.upper())


class PennsylvaniaCheckRegistrationTool(CheckRegistrationTool):
    """A tool for checking voter registration in Pennsylvania."""

    state: t.ClassVar[str] = "PA"
    features: t.ClassVar[SupportedFeatures] = SupportedFeatures(details=False)

    STATUS_URL: t.ClassVar[str] = (
        "https://www.pavoterservices.pa.gov/Pages/voterregistrationstatus.aspx"
    )
    ASPDATA_PATH: t.ClassVar[pathlib.Path] = (
        pathlib.Path(__file__).parent / "pa.aspdata.txt"
    )

    def _get_view_state_data(self) -> dict[str, str]:
        """Return obscure ASP.NET strucutred data. Annoying."""
        with open(self.ASPDATA_PATH) as f:
            lines = f.readlines()
        lines = [stripped for line in lines if (stripped := line.strip())]
        return {kv[0]: kv[1].strip() for line in lines if (kv := line.split(":", 1))}

    def _request(
        self, first_name: str, last_name: str, zipcode: str, birth_date: date
    ) -> httpx.Response:
        """Make a request to the PA voter registration status page."""
        county_code = get_county_code(zipcode)
        if not county_code:
            raise CheckRegistrationError("Invalid ZIP code or unknown county")
        data = {
            "ctl00$ContentPlaceHolder1$ScriptManager1": "ctl00$ContentPlaceHolder1$UpdatePanel1|ctl00$ContentPlaceHolder1$btnContinue",  # noqa: E501
            "ctl00_ContentPlaceHolder1_ScriptManager1_HiddenField": "",
            "ctl00$ContentPlaceHolder1$SearchSelection": "rdoSearchByName",
            "ctl00$ContentPlaceHolder1$CountyCombo": county_code,
            "ctl00$ContentPlaceHolder1$txtVRSzip": zipcode,
            "ctl00$ContentPlaceHolder1$txtVRSOpt2Item2": first_name,
            "ctl00$ContentPlaceHolder1$txtVRSOpt2Item3": last_name,
            "ctl00$ContentPlaceHolder1$txtVRSOpt2Item4": birth_date.strftime(
                "%m/%d/%Y"
            ),
            **self._get_view_state_data(),
            "ctl00$ContentPlaceHolder1$btnContinue": "Search",
        }
        response = httpx.post(
            self.STATUS_URL,
            data=data,
            headers={
                "Content-Type": "application/x-www-form-urlencoded",
                "Referer": "https://www.pavoterservices.pa.gov/pages/voterregistrationstatus.aspx",
                "Origin": "https://www.pavoterservices.pa.gov",
                "User-Agent": generate_user_agent(os="mac"),
                "X-MicrosoftAjax": "Delta=true",
                "X-Requested-With": "XMLHttpRequest",
            },
        )
        response.raise_for_status()
        return response

    def check_registration(
        self,
        first_name: str,
        last_name: str,
        zipcode: str,
        birth_date: date,
        details: bool = False,
    ) -> CheckRegistrationResult:
        """Check whether a voter is registered in Pennsylvania."""
        try:
            response = self._request(first_name, last_name, zipcode, birth_date)
        except httpx.HTTPStatusError as e:
            raise CheckRegistrationError("Failed to check voter registration") from e
        except CheckRegistrationError:
            raise

        return CheckRegistrationResult(
            registered="voter status record" in response.text.lower(), details=None
        )
