import logging
from datetime import datetime, timezone
from enum import Enum
from xml.etree.ElementTree import ParseError, fromstring

import requests
import base64
import json
import time
from typing import Dict

from pydantic import BaseModel

from .regions import Region
from .exceptions import YandexSearchAPIError, YandexSearchTimeoutError, YandexAuthError

logging.getLogger('YandexSearchApi').addHandler(logging.NullHandler())
logger = logging.getLogger('YandexSearchApi')

class SearchType(Enum):
    RUSSIAN = "SEARCH_TYPE_RU"
    TURKISH = "SEARCH_TYPE_TR"
    INTERNATIONAL = "SEARCH_TYPE_COM"


class ResponseFormat(Enum):
    XML = "FORMAT_XML"
    HTML = "FORMAT_HTML"


class IamTokenResponse(BaseModel):
    expiresAt: datetime
    iamToken: str

    def expired(self) -> bool:
        now = datetime.now(tz=timezone.utc)
        return now >= self.expiresAt

class YandexSearchAPIClient:
    """
    Yandex Search API client for Python
    """

    BASE_URL = "https://searchapi.api.cloud.yandex.net/v2/web/searchAsync"
    OPERATION_URL = "https://operation.api.cloud.yandex.net/operations/"
    IAM_TOKEN_URL = "https://iam.api.cloud.yandex.net/iam/v1/tokens"

    def __init__(
            self,
            folder_id: str,  # https://yandex.cloud/en-ru/docs/resource-manager/operations/folder/get-id
            oauth_token: str  # https://yandex.cloud/en-ru/docs/iam/concepts/authorization/oauth-token
    ):
        """
        Initialize the client with either IAM token or OAuth token

        Args:
            folder_id: Yandex Cloud folder ID
            oauth_token: Yandex OAuth token (will be converted to IAM token if iam_token not provided)

        Raises:
            YandexAuthError: If neither token is provided or token conversion fails
        """
        self.folder_id = folder_id
        self.oauth_token = oauth_token
        self.__iam_token_data = self._get_iam_token_from_oauth(oauth_token)  # type: ignore

    @property
    def _iam_token(self) -> str:
        if self.__iam_token_data.expired():
            self.__iam_token_data = self._get_iam_token_from_oauth(self.oauth_token)
            logger.debug(f"IAM token is expired, rewew: {self.__iam_token_data.expired()}")
        return self.__iam_token_data.iamToken

    def _get_iam_token_from_oauth(self, oauth_token: str) -> IamTokenResponse:
        """
        Convert OAuth token to IAM token

        Args:
            oauth_token: Yandex OAuth token

        Returns:
            IAM token

        Raises:
            YandexAuthError: If token conversion fails
        """
        try:
            response = requests.post(
                self.IAM_TOKEN_URL,
                json={"yandexPassportOauthToken": oauth_token},
                timeout=10
            )
            response.raise_for_status()
            return IamTokenResponse.model_validate(response.json())
        except Exception as e:
            raise YandexAuthError(f"Failed to get IAM token from OAuth: {str(e)}")

    def search(
            self,
            query_text: str,
            *,
            search_type: SearchType = SearchType.RUSSIAN,
            region: Region = Region.RUSSIA,
            page: int = 0,
            n_links: int = 10,
            response_timeout: int = 5,

    ) -> str:
        headers = {
            "Authorization": f"Bearer {self._iam_token}",
            "Content-Type": "application/json"
        }

        body = {
            "query": {
                "searchType": search_type.value,
                "queryText": query_text,
                "page": page,
            },
            "groupSpec": {
                "groupsOnPage": n_links,
            },
            "region": region.value,
            "l10N": "ru",
            "folderId": self.folder_id,
            "responseFormat": ResponseFormat.XML.value,
        }

        try:
            response = requests.post(
                self.BASE_URL,
                headers=headers,
                data=json.dumps(body),
                timeout=response_timeout
            )
            response.raise_for_status()
            return response.json()["id"]
        except Exception as e:
            raise e

    def _check_operation_status(self, operation_id: str) -> Dict:
        """
        Check the status of a search operation

        Args:
            operation_id: Operation ID returned by search()

        Returns:
            Dictionary with operation status

        Raises:
            YandexSearchAPIError: If the API request fails
        """
        headers = {
            "Authorization": f"Bearer {self._iam_token}"
        }

        try:
            response = requests.get(
                f"{self.OPERATION_URL}{operation_id}",
                headers=headers,
                timeout=30
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            raise YandexSearchAPIError(f"Status check failed: {str(e)}")

    def get_search_results(
            self,
            operation_id: str,
    ) -> str:
        """
        Get the search results when operation is complete

        Args:
            operation_id: Operation ID returned by search()

        Returns:
            Decoded search results (XML)

        Raises:
            YandexSearchAPIError: If the operation failed or no data available
        """
        status = self._check_operation_status(operation_id)

        if not status.get("done", False):
            raise YandexSearchAPIError("No response data available")

        if "response" not in status or "rawData" not in status["response"]:
            raise YandexSearchAPIError("No response data available")

        try:
            return base64.b64decode(status["response"]["rawData"]).decode('utf-8')
        except Exception as e:
            raise YandexSearchAPIError(f"Failed to decode results: {str(e)}")

    @staticmethod
    def _extract_yandex_search_links(xml_content: str):
        urls = []

        try:
            root = fromstring(xml_content)

            groups = root.findall('.//group')

            for group in groups:
                doc = group.find('doc')
                if doc is not None:
                    url_elem = doc.find('url')
                    if url_elem is not None and url_elem.text:
                        urls.append(url_elem.text)

        except ParseError as e:
            print(f"Error parsing XML: {e}")
        except Exception as e:
            print(f"Error processing search results: {e}")

        return urls

    def search_and_wait(
            self,
            query_text: str,
            *,
            search_type: SearchType = SearchType.RUSSIAN,
            region: Region = Region.RUSSIA,
            max_wait: int = 300,
            interval: int = 1,
            n_links: int = 10,
    ) -> str:

        operation_id = self.search(query_text, search_type=search_type, n_links=n_links, region=region)
        start_time = time.time()

        while time.time() - start_time < max_wait:
            try:
                status = self._check_operation_status(operation_id)

                if status.get("done", False):
                    return self.get_search_results(operation_id)
                time.sleep(interval)
            except YandexSearchAPIError as e:
                raise e

        raise YandexSearchTimeoutError(f"Timeout waiting for search results after {max_wait} seconds")

    def get_links(
            self,
            query_text: str,
            search_type: SearchType = SearchType.RUSSIAN,
            region: Region = Region.RUSSIA,
            n_links: int = 10,
            max_wait: int = 300,
            interval: int = 1,
    ) -> list[str]:
        results = self.search_and_wait(query_text, search_type=search_type, n_links=n_links, region=region, max_wait=max_wait, interval=interval)
        links = self._extract_yandex_search_links(results)
        if len(links) != n_links:
            logger.warning(f"Found {len(results)} links but expected {n_links} links.")

        return links
