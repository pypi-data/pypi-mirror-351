class ODataRequestError(Exception):
    """Base exception for all OData errors."""


class ODataConnectionError(ODataRequestError):
    """Exception raised when a connection error occurs (e.g., DNS error, refused connection)."""

    def __init__(self, url: str, params: dict | None = None, original_exception: Exception | None = None) -> None:
        """
        Initialize ODataConnectionError.

        Args:
            url (str): The URL that caused the connection error.
            params (dict, optional): The parameters sent with the request. Defaults to None.
            original_exception (Exception, optional): The original exception that was caught. Defaults to None.

        """
        self.url = url
        self.params = params if params else {}
        self.original_exception = original_exception
        message = f"Connection error occurred while trying to reach {self.url}"
        if self.params:
            message += f" with params: {self.params}"
        if self.original_exception:
            message += f". Original error: {type(self.original_exception).__name__}: {self.original_exception!s}"
        super().__init__(message)


class ODataTimeoutError(ODataRequestError):
    """Exception raised when a read timeout occurs."""

    def __init__(self, url: str, params: dict | None = None, timeout_duration: float | None = None) -> None:
        """
        Initialize ODataTimeoutError.

        Args:
            url (str): The URL that caused the timeout error.
            params (dict, optional): The parameters sent with the request. Defaults to None.
            timeout_duration (float, optional): The configured timeout duration in seconds. Defaults to None.

        """
        self.url = url
        self.params = params if params else {}
        self.timeout_duration = timeout_duration
        message = f"Read timeout occurred while requesting {self.url}"
        if self.params:
            message += f" with params: {self.params}"
        if self.timeout_duration is not None:
            message += f" (timeout was {self.timeout_duration}s)"
        super().__init__(message)


class ODataHTTPError(ODataRequestError):
    """Exception raised when an HTTP error occurs (e.g., 4xx or 5xx response)."""

    def __init__(
        self,
        url: str,
        status_code: int,
        params: dict | None = None,
        response_content: str | None = None,
    ) -> None:
        """
        Initialize ODataHTTPError.

        Args:
            url (str): The URL that caused the HTTP error.
            status_code (int): The HTTP status code received.
            error_message (str, optional): The error message from the server or a default message.
                                           Defaults to "Unknown HTTP error".
            params (dict, optional): The parameters sent with the request. Defaults to None.
            response_content (str, optional): The full content of the HTTP response body. Defaults to None.

        """
        self.url = url
        self.status_code = status_code
        self.params = params if params else {}
        self.response_content = response_content

        if self.status_code == 401:
            self.error_message = "Authentication failed (401): Invalid credentials"
        elif self.status_code == 403:
            self.error_message = "Authorization failed (403): Insufficient permissions"
        elif self.status_code == 404:
            self.error_message = "Resource not found (404)"
        elif self.status_code == 429:
            self.error_message = "Rate limit exceeded (429)"
        else:
            self.error_message = f"HTTP error {self.status_code}"

        message = f"HTTP error {self.status_code} occurred for {self.url}: {self.error_message}"
        if self.params:
            message += f" with params: {self.params}"
        if self.response_content:
            preview_content = (
                (self.response_content[:200] + "...") if len(self.response_content) > 200 else self.response_content
            )
            message += f"\nServer response preview: {preview_content}"
        super().__init__(message)


class ODataJSONDecodeError(ODataRequestError):
    """Exception raised when a JSON decode error occurs."""

    def __init__(self, url: str, params: dict | None = None, original_exception: Exception | None = None) -> None:
        """Initialize ODataJSONDecodeError."""
        super().__init__(
            f"JSON decode error occurred while requesting {url} with params: {params}. "
            f"Original Exception: {original_exception}",
        )
