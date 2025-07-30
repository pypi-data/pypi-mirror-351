"""Utilities for debugging this library."""

import typing as t

import httpx


class ProcessTransportBase(httpx.HTTPTransport):
    """A transport that provides hooks for processing requests and responses."""

    def handle_request(self, request: httpx.Request) -> httpx.Response:
        """Handle a request."""
        try:
            response = super().handle_request(request)
        except Exception as e:
            return self.process_exception(request, e)
        else:
            return self.process_response(request, response)

    def process_exception(
        self, request: httpx.Request, exception: Exception
    ) -> httpx.Response:
        """
        Process a request that raised an exception.

        This can re-raise the exception, log it, or otherwise handle it.
        It can also transmute the exception into a response, if desired.
        """
        raise exception

    def process_response(
        self, request: httpx.Request, response: httpx.Response
    ) -> httpx.Response:
        """
        Process a response.

        This can log the response, modify it, or otherwise handle it.
        It can also transmute the response into an exception, if desired.
        """
        return response


class DumpDebugTransport(ProcessTransportBase):
    """A transport that prints the request and response."""

    _out: t.TextIO

    def __init__(self, out: t.TextIO, *args, **kwargs):
        """Initialize the transport."""
        super().__init__(*args, **kwargs)
        self._out = out

    def process_response(
        self, request: httpx.Request, response: httpx.Response
    ) -> httpx.Response:
        """Print the request and response."""
        self._out.write("# Request:\n")
        self._out.write(f"{request.method} {request.url}\n")
        self._out.write("# Headers:\n")
        for k, v in request.headers.items():
            self._out.write(f"{k}: {v}\n")
        self._out.write("# Body:\n")
        self._out.write(f"{request.content.decode()}\n")
        self._out.write("# Response:\n")
        self._out.write(f"Status: {response.status_code}\n")
        self._out.write("# Headers:\n")
        for k, v in response.headers.items():
            self._out.write(f"{k}: {v}\n")
        self._out.write("# Body:\n")
        _ = response.read()
        self._out.write(f"{response.text}\n")
        return response


class CurlDebugTransport(ProcessTransportBase):
    """A transport that prints the request as a CURL command."""

    _out: t.TextIO

    def __init__(self, out: t.TextIO, *args, **kwargs):
        """Initialize the transport."""
        super().__init__(*args, **kwargs)
        self._out = out

    def process_response(
        self, request: httpx.Request, response: httpx.Response
    ) -> httpx.Response:
        """Print the request as a CURL command."""
        SHOW_HEADERS = {"content-type"}
        self._out.write(f"curl -X {request.method} {request.url} \\\n")
        for k, v in request.headers.items():
            if k in SHOW_HEADERS:
                self._out.write(f"--header '{k}: {v}' \\\n")
        # This is one massive hack to make the output more readable.

        dbg_content = (
            request.content.decode().replace("\\n", "\n").replace("><", ">\n<")
        )
        self._out.write(f"--data '{dbg_content}'\n")
        return response
