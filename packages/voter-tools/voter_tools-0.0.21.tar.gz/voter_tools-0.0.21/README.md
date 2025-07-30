# voter-tools

[![PyPI](https://img.shields.io/pypi/v/voter-tools.svg)](https://pypi.org/project/voter-tools/)
[![Tests](https://github.com/front-seat/voter-tools/actions/workflows/test.yml/badge.svg)](https://github.com/front-seat/voter-tools/actions/workflows/test.yml)
[![Changelog](https://img.shields.io/github/v/release/front-seat/voter-tools?include_prereleases&label=changelog)](https://github.com/front-seat/voter-tools/releases)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](https://github.com/front-seat/voter-tools/blob/main/LICENSE)

Tools for online voter registration in the United States of America.

Contains a command-line tool (`vote`) and a python library (`voter_tools`) to:

1. Check voter registration status in key states, currently including:
   - Georgia
   - Michigan
   - Pennsylvania
   - Wisconsin
1. Perform online voter registration (OVR) directly with key states, via their APIs. We currently support the [Pennsylvania OVR API](https://www.pa.gov/en/agencies/dos/resources/voting-and-elections-resources/pa-online-voter-registration-web-api-rfc.html) with plans to support Michigan and Washington states in the future.


## Installation

Install this library using `pip`:

```bash
pip install voter-tools
```

## Command-line usage

### Check registration of a single voter

To check whether a voter is registered:

```
vote check <first-name> <last-name> <zip> <dob YYYY-MM-DD> [--details]
```

This will tell you whether the user is registered to vote. You can request extra details (registration date, current status, etc.) with the `--details` flag. Not all states support all details.

### Check registration of multiple voters in bulk

There is also a tool to check every record in a CSV file:

```
vote check-csv <input-file.csv> [--details]
```

A new CSV is written to `stdout` with the same fields as the input CSV plus extras related to the registration check.

### Interact with the Pennsylvania API

The `vote` command contains a number of sub-commands for interacting directly with the [Pennsylvania state API](https://www.pa.gov/en/agencies/dos/resources/voting-and-elections-resources/pa-online-voter-registration-web-api-rfc.html).

For instance, to invoke the API's "get available languages" call:

```
> vote pa get-languages
languages=(Language(code='LANGENG', name='English'), Language(code='LANGSPN', name='Spanish'), Language(code='LANGTCN', name='Chinese'))
```

Use `vote pa --help` for details on available subcommands.

## Development

To contribute to this library, first checkout the code. Then create a new virtual environment:

```bash
cd voter-tools
python -m venv .venv
source .venv/bin/activate
```

Now install the dependencies and test dependencies:

```bash
pip install -e '.[dev]'
```

To run tests:

```bash
make test
```

To run a full lint/typecheck/test pass:

```bash
make check
```

## State-specific documents

We've collected state-specific documents in the [`docs`](./docs) directory and will try to keep them up-to-date as state APIs change.
