import asyncio
import json
import time
import uuid
from types import TracebackType
from typing import Any, Self
from urllib.parse import urlencode

import aiolimiter
import httpx
import tenacity
from loguru import logger

from bcodata.exceptions import (
    ODataConnectionError,
    ODataHTTPError,
    ODataJSONDecodeError,
    ODataRequestError,
    ODataTimeoutError,
)


class Client:
    """A client for Business Central OData API."""

    # HTTP status codes that are considered retryable
    RETRYABLE_STATUS_CODES = {429, 500, 502, 503, 504}  # noqa: RUF012

    # Default configuration values
    DEFAULT_MAX_RATE = 10
    DEFAULT_TIME_PERIOD = 1
    DEFAULT_MAX_CONCURRENCY = 5
    DEFAULT_MAX_RETRIES = 3
    DEFAULT_RETRY_DELAY = 1
    DEFAULT_TIMEOUT = 90

    def __init__(
        self,
        base_url: str,
        credentials: tuple[str, str] | None = None,
        max_rate: int = DEFAULT_MAX_RATE,
        time_period: int = DEFAULT_TIME_PERIOD,
        max_concurrency: int = DEFAULT_MAX_CONCURRENCY,
        max_retries: int = DEFAULT_MAX_RETRIES,
        base_retry_delay: int = DEFAULT_RETRY_DELAY,
        timeout: int = DEFAULT_TIMEOUT,
    ) -> None:
        """
        Initialize the client with the given base URL and credentials.

        Parameters
        ----------
        base_url : str
            The base URL of the Business Central OData API.
        credentials : tuple[str, str] | None
            The credentials for the client.
        max_rate : int
            The maximum number of requests per time period.
        time_period : int
            The time period in seconds.
        max_concurrency : int
            The maximum number of concurrent requests.
        max_retries : int
            The number of times to retry a request.
        base_retry_delay : int
            The base delay in seconds between retries.
        timeout : int
            The timeout for the request.

        Returns
        -------
        None

        """
        self.base_url = base_url.rstrip("/")
        self._username = credentials[0] if credentials else None
        self._password = credentials[1] if credentials else None
        self._session = None
        self.limiter = aiolimiter.AsyncLimiter(max_rate=max_rate, time_period=time_period)
        self.semaphore = asyncio.Semaphore(max_concurrency)
        self.max_retries = max_retries
        self.base_retry_delay = base_retry_delay
        self.timeout = timeout

        if max_rate <= 0:
            raise ValueError("max_rate must be greater than 0")
        if time_period <= 0:
            raise ValueError("time_period must be greater than 0")
        if max_concurrency <= 0:
            raise ValueError("max_concurrency must be greater than 0")
        if self.max_retries < 0:
            raise ValueError("max_retries must be greater than or equal to 0")
        if self.base_retry_delay <= 0:
            raise ValueError("base_retry_delay must be greater than 0")
        if self.timeout <= 0:
            raise ValueError("timeout must be greater than 0")

        # Keep this at INFO as it's important initialization information
        logger.info(f"OData client initialized for {base_url}")
        logger.debug(
            f"Client config: max_rate={max_rate}/{time_period}s, "
            f"concurrency={max_concurrency}, retries={max_retries}, "
            f"retry_delay={base_retry_delay}s, timeout={timeout}s",
        )

    async def __aenter__(self) -> Self:
        """Enter the context manager."""
        logger.debug("Creating HTTP client session")
        self._session = httpx.AsyncClient(auth=(self._username, self._password), timeout=self.timeout)
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        """Exit the context manager."""
        if self._session:
            logger.debug("Closing HTTP client session")
            await self._session.aclose()
        self._session = None

    @staticmethod
    def _is_retryable_exception(exception: BaseException) -> bool:
        """
        Determine if an exception is retryable.

        Parameters
        ----------
        exception : BaseException
            The exception to check.

        Returns
        -------
        bool
            True if the exception is retryable, False otherwise.

        """
        if isinstance(exception, httpx.ConnectError | httpx.ReadTimeout | httpx.PoolTimeout):
            logger.debug(f"Connection/timeout error identified as retryable: {type(exception).__name__}")
            return True
        if isinstance(exception, httpx.HTTPStatusError):
            status_code = exception.response.status_code
            is_retryable = status_code in Client.RETRYABLE_STATUS_CODES
            logger.debug(
                f"HTTP {status_code} {'retryable' if is_retryable else 'non-retryable'}: "
                f"{exception.response.url}",
            )
            return is_retryable
        logger.debug(f"Non-retryable exception: {type(exception).__name__}")
        return False

    @staticmethod
    def _build_full_url(base_url: str, params: dict[str, Any] | None = None) -> str:
        """Build full URL with query parameters."""
        if params:
            query_string = urlencode(params, safe="$")
            return f"{base_url}?{query_string}"
        return base_url

    async def _request(
        self,
        url: str,
        params: dict[str, Any] | None = None,
        request_id: str | None = None,
    ) -> httpx.Response:
        """
        Make a request to the API.

        Parameters
        ----------
        url : str
            The URL to request.
        params : dict[str, Any] | None
            The parameters to pass to the endpoint.
        request_id : str | None
            A unique identifier for this request for logging purposes.

        Returns
        -------
        httpx.Response
            The response from the endpoint.

        """
        request_id = request_id or str(uuid.uuid4())
        full_url = self._build_full_url(url, params)

        @tenacity.retry(
            stop=tenacity.stop_after_attempt(self.max_retries + 1),
            wait=tenacity.wait_exponential(multiplier=self.base_retry_delay, max=self.timeout / 2),
            retry=tenacity.retry_if_exception(self._is_retryable_exception),
            reraise=True,
            before_sleep=lambda retry_state: logger.debug(
                f"[{request_id}] Retry {retry_state.attempt_number} after "
                f"{retry_state.outcome.exception() if retry_state.outcome else 'unknown error'}",
            ),
        )
        async def _attempt_request() -> httpx.Response:
            async with self.semaphore, self.limiter:
                logger.debug(f"[{request_id}] GET {full_url}")
                response = await self._session.get(url, params=params, headers={"X-Request-ID": request_id})
                response.raise_for_status()
                logger.debug(f"[{request_id}] Response: {response.status_code} ({len(response.content)} bytes)")
                return response

        if not self._session:
            logger.error("Client not initialized. Use 'async with Client(...):' context manager.")
            raise RuntimeError("Client not initialized. Use 'async with Client(...):' context manager.")

        try:
            return await _attempt_request()
        except httpx.ConnectError as e:
            logger.error(f"[{request_id}] Connection failed: {full_url}")
            raise ODataConnectionError(url, params=params, original_exception=e) from e
        except httpx.ReadTimeout as e:
            logger.error(f"[{request_id}] Request timeout ({self.timeout}s): {full_url}")
            raise ODataTimeoutError(url, params=params, timeout_duration=self.timeout) from e
        except httpx.HTTPStatusError as e:
            status_code = e.response.status_code
            error_text = e.response.text[:200] + "..." if len(e.response.text) > 200 else e.response.text
            logger.error(f"[{request_id}] HTTP {status_code}: {full_url} - {error_text}")
            raise ODataHTTPError(
                url,
                status_code=status_code,
                params=params,
                response_content=e.response.text,
            ) from e
        except json.JSONDecodeError as e:
            logger.error(f"[{request_id}] Invalid JSON response: {full_url}")
            raise ODataJSONDecodeError(url, params=params, original_exception=e) from e
        except httpx.RequestError as e:
            logger.error(f"[{request_id}] Request error: {type(e).__name__} - {full_url}")
            raise ODataRequestError(
                f"Request failed for {url}: {e}",
            ) from e
        except Exception as e:
            logger.error(f"[{request_id}] Unexpected error: {type(e).__name__} - {full_url}")
            raise ODataRequestError(
                f"Unexpected error for {url}: {e}",
            ) from e

    async def get_data(self, endpoint: str, params: dict[str, Any] | None = None) -> list[dict[str, Any]]:
        """
        Get data from the API.

        Parameters
        ----------
        endpoint : str
            The endpoint to request.
        params : dict[str, Any] | None
            The parameters to pass to the endpoint. Can be built using QueryBuilder.

        Returns
        -------
        list[dict[str, Any]]
            The response from the endpoint.

        """
        start_time = time.time()
        request_id = str(uuid.uuid4())[:8]  # Shorter ID for readability

        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        initial_url = self._build_full_url(url, params)
        content = []
        page_count = 0

        # Single INFO log for the entire operation
        logger.info(f"Fetching {endpoint}")
        logger.debug(f"[{request_id}] Full URL: {initial_url}")

        while url:
            page_count += 1
            page_start_time = time.time()
            
            response = await self._request(url, params, request_id)
            try:
                response_json = response.json()
            except json.JSONDecodeError as e:
                logger.error(f"[{request_id}] Failed to parse JSON from {url}")
                raise ODataJSONDecodeError(url, params=params, original_exception=e) from e

            items = response_json.get("value", [])
            content.extend(items)

            page_duration = time.time() - page_start_time
            logger.debug(
                f"[{request_id}] Page {page_count}: {len(items)} items "
                f"({page_duration:.2f}s, total: {len(content)} items)",
            )

            url = response_json.get("@odata.nextLink", None)
            if url:
                logger.debug(f"[{request_id}] Next: {url}")
            params = None  # Clear params for subsequent requests

        total_duration = time.time() - start_time
        
        # Summary at INFO level - concise for users
        if page_count > 1:
            logger.info(
                f"Retrieved {len(content)} items from {endpoint} "
                f"({page_count} pages, {total_duration:.1f}s)",
            )
        else:
            logger.info(
                f"Retrieved {len(content)} items from {endpoint} ({total_duration:.1f}s)",
            )
        
        # Detailed stats at DEBUG level
        logger.debug(
            f"[{request_id}] Complete: {len(content)} items, {page_count} pages, "
            f"{total_duration:.3f}s total, {total_duration / (page_count or 1):.3f}s avg/page",
        )
        
        return content