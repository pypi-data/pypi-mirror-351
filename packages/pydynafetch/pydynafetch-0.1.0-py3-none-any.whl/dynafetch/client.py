import time
from typing import Any
from urllib.parse import urljoin

import requests
from loguru import logger


class DynaFetchError(Exception):
    """Custom exception for DynaFetch operations."""


class DynaFetchClient:
    """
    A robust client for fetching paginated data from OData/REST APIs.

    Supports automatic pagination, retry logic, and comprehensive error handling.
    """

    def __init__(
        self,
        base_url: str,
        session: requests.Session | None = None,
        credentials: tuple[str, str] | None = None,
        timeout: int = 30,
        max_retries: int = 3,
        retry_delay: float = 1.0,
        data_key: str = "value",
        next_link_key: str = "@odata.nextLink",
    ) -> None:
        """
        Initialize the DynaFetch client.

        Args:
            base_url: Base URL for the API
            session: Pre-configured requests session (takes precedence over credentials)
            credentials: Tuple of (username, password) for basic auth
            timeout: Request timeout in seconds
            max_retries: Maximum number of retry attempts for failed requests
            retry_delay: Initial delay between retries (uses exponential backoff)
            data_key: Key in response JSON containing the data array
            next_link_key: Key in response JSON containing the next page URL

        Raises:
            DynaFetchError: If neither session nor credentials are provided

        """
        self.base_url = self._validate_base_url(base_url)
        self.timeout = timeout
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.data_key = data_key
        self.next_link_key = next_link_key

        # Set up session
        if session is not None:
            self.session = session
            logger.debug("Using provided authenticated session")
        elif credentials is not None:
            self.session = requests.Session()
            self.session.auth = credentials
            logger.debug(f"Created session with basic auth for user: {credentials[0]}")
        else:
            raise DynaFetchError("Either 'session' or 'credentials' must be provided")

    def _validate_base_url(self, base_url: str) -> str:
        """Validate and normalize the base URL."""
        if not base_url or not isinstance(base_url, str):
            raise DynaFetchError("base_url must be a non-empty string")

        if not base_url.startswith(("http://", "https://")):
            raise DynaFetchError("base_url must start with http:// or https://")

        return base_url.rstrip("/")

    def _make_request(
        self,
        url: str,
        params: dict[str, Any] | None = None,
        headers: dict[str, str] | None = None,
    ) -> dict[str, Any]:
        """
        Make HTTP request with retry logic and comprehensive error handling.

        Args:
            url: Request URL
            params: Query parameters
            headers: Additional headers

        Returns:
            JSON response as dictionary

        Raises:
            DynaFetchError: For various HTTP and network errors

        """
        last_exception = None

        for attempt in range(self.max_retries + 1):
            try:
                logger.debug(f"Making request to {url} with params {params} (attempt {attempt + 1})")

                response = self.session.get(
                    url,
                    params=params,
                    headers=headers,
                    timeout=self.timeout,
                )

                # Handle HTTP errors
                if response.status_code == 429:
                    # Rate limit - wait longer
                    retry_after = int(response.headers.get("Retry-After", self.retry_delay * (2**attempt)))
                    logger.warning(f"Rate limited. Waiting {retry_after} seconds...")
                    time.sleep(retry_after)
                    continue
                if response.status_code >= 500:
                    # Server errors - retry
                    logger.warning(f"Server error {response.status_code}. Retrying...")
                    response.raise_for_status()
                else:
                    # Other HTTP errors or success
                    response.raise_for_status()

                try:
                    json_data = response.json()
                    logger.debug(f"Successfully fetched data from {url} with params {params}")
                    return json_data
                except ValueError as e:
                    raise DynaFetchError(
                        f"Invalid JSON response from {url} with params {params}: {e}",
                    ) from e

            except requests.exceptions.Timeout:
                last_exception = DynaFetchError(
                    f"Request to {url} with params {params} timed out after {self.timeout} seconds",
                )
                logger.warning(f"Request timeout (attempt {attempt + 1})")
            except requests.exceptions.ConnectionError:
                last_exception = DynaFetchError(f"Connection error when accessing {url} with params {params}")
                logger.warning(f"Connection error (attempt {attempt + 1})")
            except requests.exceptions.HTTPError as e:
                if e.response.status_code < 500:
                    # Client errors (4xx) - don't retry
                    raise DynaFetchError(
                        f"HTTP {e.response.status_code} error for"
                        f" {url} with params {params}: {e}",
                    ) from e
                last_exception = DynaFetchError(
                    f"HTTP {e.response.status_code} error for {url} with params {params}: {e}",
                )
                logger.warning(f"HTTP error {e.response.status_code} (attempt {attempt + 1})")
            except requests.exceptions.RequestException as e:
                last_exception = DynaFetchError(f"Request to {url} with params {params} failed: {e}")
                logger.warning(f"Request exception (attempt {attempt + 1}): {e}")

            # Wait before retrying (exponential backoff)
            if attempt < self.max_retries:
                delay = self.retry_delay * (2**attempt)
                logger.debug(f"Waiting {delay} seconds before retry...")
                time.sleep(delay)

        # All retries exhausted
        logger.error(f"All {self.max_retries + 1} attempts failed for {url} with params {params}")
        raise last_exception or DynaFetchError(
            f"Failed to fetch data from {url} with params {params} after {self.max_retries + 1} attempts",
        )

    def _validate_response_data(self, response_data: Any, data_key: str) -> None:
        """
        Validate that response data is a list.
        
        Args:
            response_data: The data to validate
            data_key: The key used to access the data        
        Raises:
            DynaFetchError: If response_data is not a list

        """
        if not isinstance(response_data, list):
            raise DynaFetchError(f"Expected list in '{data_key}', got {type(response_data)}")

    def get_data(
        self,
        endpoint: str,
        params: dict[str, Any] | None = None,
        headers: dict[str, str] | None = None,
    ) -> list[dict[str, Any]]:
        """
        Fetch all paginated data from an API endpoint.

        Args:
            endpoint: API endpoint path (relative to base_url)
            params: Query parameters for the first request
            headers: Additional headers to include in requests

        Returns:
            List of all data records from all pages

        Raises:
            DynaFetchError: For various API or network errors

        """
        if not endpoint:
            raise DynaFetchError("endpoint cannot be empty")

        # Build initial URL
        url = urljoin(self.base_url + "/", endpoint.lstrip("/"))
        params = params.copy() if params else {}
        data = []
        page_count = 0

        logger.debug(f"Starting paginated fetch from {endpoint} with initial params {params}")

        while True:
            page_count += 1
            logger.debug(f"Fetching page {page_count} from {url} with params {params}")

            try:
                response = self._make_request(url, params, headers)

                # Extract data using configurable key
                if self.data_key not in response:
                    logger.warning(
                        f"Response missing expected data key '{self.data_key}'. "
                        f"Available keys: {list(response.keys())}",
                    )
                    response_data = []
                else:
                    response_data = response.get(self.data_key, [])

                if not isinstance(response_data, list):
                    self._validate_response_data(response_data, self.data_key)

                data.extend(response_data)
                logger.debug(f"Page {page_count}: fetched {len(response_data)} records")

                # Check for next page
                next_url = response.get(self.next_link_key)
                if not next_url:
                    break

                url = next_url
                params = {}  # Next URL usually contains all necessary parameters

            except DynaFetchError:
                logger.error(f"Failed to fetch page {page_count}")
                raise

        logger.debug(f"Completed paginated fetch: {len(data)} total records across {page_count} pages")
        return data

    def set_default_headers(self, headers: dict[str, str]) -> None:
        """Set default headers for all requests."""
        self.session.headers.update(headers)
        logger.debug(f"Updated default headers: {list(headers.keys())}")

    def get_single_page(
        self,
        endpoint: str,
        params: dict[str, Any] | None = None,
        headers: dict[str, str] | None = None,
    ) -> dict[str, Any]:
        """
        Fetch a single page/response from an API endpoint.

        Args:
            endpoint: API endpoint path
            params: Query parameters
            headers: Additional headers

        Returns:
            Raw JSON response as dictionary

        """
        if not endpoint:
            raise DynaFetchError("endpoint cannot be empty")

        url = urljoin(self.base_url + "/", endpoint.lstrip("/"))
        logger.debug(f"Fetching single page from {endpoint} with params {params}")

        return self._make_request(url, params, headers)
