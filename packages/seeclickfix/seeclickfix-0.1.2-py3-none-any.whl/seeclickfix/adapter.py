import json
import logging
from json import JSONDecodeError
from typing import Dict

import aiohttp

from .models.result import Result


class RestAdapterException(Exception):
    pass


class RestAdapter:
    def __init__(
        self,
        hostname: str = "",
        base: str = "",
        user_agent: str = "",
        ssl_verify: bool = True,
        logger: logging.Logger = None,
    ):
        """
        Constructor for RestAdapter
        :param hostname: Hostname of the API server
        :param base (optional): Base URL of the API server
        :param user_agent (optional):  User-Agent string to use when making HTTP requests
        :param ssl_verify: (optional) Verify SSL certificates. Defaults to True.
        :param logger: (optional) If your app has a logger, pass it in here.
        """
        self._logger = logger or logging.getLogger(__name__)
        self.url = f"https://{hostname}/"

        if base:
            self.url = f"{self.url}{base}/"

        self.user_agent = user_agent
        self.ssl_verify = ssl_verify

    async def _do(
        self,
        session: aiohttp.ClientSession,
        http_method: str,
        endpoint: str,
        ep_params: Dict = None,
        headers: Dict = {},
        data: Dict = None,
    ) -> Result:
        """
        Private method for get(), post(), delete(), etc. methods
        :param http_method: GET, POST, DELETE, etc.
        :param endpoint: URL Endpoint as a string
        :param ep_params: Dictionary of endpoint parameters (Optional)
        :param headers: Dictionary of headers (Optional)
        :param data: Dictionary of data to pass in the request (Optional)
        :return: a Result object
        """
        full_url = self.url + endpoint

        if self.user_agent:
            headers["User-Agent"] = self.user_agent
        log_line_pre = f"method={http_method}, url={full_url}"
        log_line_post = ", ".join(
            (log_line_pre, "success={}, status_code={}, message={}")
        )

        session.ssl_verify = self.ssl_verify

        try:
            self._logger.debug(msg=log_line_pre)
            response = await session.request(
                method=http_method,
                url=full_url,
                verify_ssl=self.ssl_verify,
                headers=headers,
                params=ep_params,
                json=data,
            )
        except aiohttp.ClientError as e:
            self._logger.error(msg=(str(e)))
            raise RestAdapterException("Request failed") from e

        self._logger.debug(response.url)

        # deserialize
        try:
            data_out = await response.json()
        except (ValueError, TypeError, JSONDecodeError) as e:
            self._logger.error(msg=log_line_post.format(False, None, e))
            raise RestAdapterException("Bad JSON in response") from e

        status_code = response.status
        # If status_code in 200-299 range, return success Result with data, otherwise raise exception
        is_success = 299 >= status_code >= 200  # 200 to 299 is OK

        log_line = log_line_post.format(is_success, status_code, response.reason)
        if is_success:
            self._logger.debug(msg=log_line)
            return Result(
                status_code,
                headers=response.headers,
                message=response.reason,
                data=data_out,
            )
        self._logger.error(msg=log_line)
        raise RestAdapterException(f"{status_code}: {response.reason}")

    async def get(
        self,
        session: aiohttp.ClientSession,
        endpoint: str,
        ep_params: Dict = None,
        headers: Dict = {},
    ) -> Result:
        return await self._do(
            session,
            http_method="GET",
            endpoint=endpoint,
            ep_params=ep_params,
            headers=headers,
        )

    async def post(
        self,
        session: aiohttp.ClientSession,
        endpoint: str,
        ep_params: Dict = None,
        headers: Dict = {},
        data: Dict = None,
    ) -> Result:
        return await self._do(
            session,
            http_method="POST",
            endpoint=endpoint,
            ep_params=ep_params,
            headers=headers,
            data=data,
        )

    async def delete(
        self,
        session: aiohttp.ClientSession,
        endpoint: str,
        ep_params: Dict = None,
        headers: Dict = {},
        data: Dict = None,
    ) -> Result:
        return await self._do(
            session,
            http_method="DELETE",
            endpoint=endpoint,
            ep_params=ep_params,
            headers=headers,
            data=data,
        )
