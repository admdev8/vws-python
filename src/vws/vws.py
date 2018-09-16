"""
Tools for interacting with Vuforia APIs.
"""

import base64
import io
import json
from time import sleep
from typing import Any, Dict, List, Union
from urllib.parse import urljoin

import requests
import timeout_decorator
from requests import Response

from vws._authorization import authorization_header, rfc_1123_date


def _target_api_request(
    server_access_key: bytes,
    server_secret_key: bytes,
    method: str,
    content: bytes,
    request_path: str,
    base_vws_url: str,
) -> Response:
    """
    Make a request to the Vuforia Target API.

    This uses `requests` to make a request against https://vws.vuforia.com.
    The content type of the request will be `application/json`.

    Args:
        server_access_key: A VWS server access key.
        server_secret_key: A VWS server secret key.
        method: The HTTP method which will be used in the request.
        content: The request body which will be used in the request.
        request_path: The path to the endpoint which will be used in the
            request.

        base_vws_url: The base URL for the VWS API.

    Returns:
        The response to the request made by `requests`.
    """
    date = rfc_1123_date()
    content_type = 'application/json'

    signature_string = authorization_header(
        access_key=server_access_key,
        secret_key=server_secret_key,
        method=method,
        content=content,
        content_type=content_type,
        date=date,
        request_path=request_path,
    )

    headers = {
        'Authorization': signature_string,
        'Date': date,
        'Content-Type': content_type,
    }

    url = urljoin(base=base_vws_url, url=request_path)

    response = requests.request(
        method=method,
        url=url,
        headers=headers,
        data=content,
    )

    return response


class VWS:
    """
    An interface to Vuforia Web Services APIs.
    """

    def __init__(
        self,
        server_access_key: str,
        server_secret_key: str,
        base_vws_url: str = 'https://vws.vuforia.com',
    ) -> None:
        """
        Args:
            server_access_key: A VWS server access key.
            server_secret_key: A VWS server secret key.
            base_vws_url: The base URL for the VWS API.
        """
        self._server_access_key = server_access_key.encode()
        self._server_secret_key = server_secret_key.encode()
        self._base_vws_url = base_vws_url

    def add_target(
        self,
        name: str,
        width: Union[int, float],
        image: io.BytesIO,
        active_flag: bool = True,
    ) -> str:
        """
        Add a target to a Vuforia Web Services database.

        Args:
            name: The name of the target.
            width: The width of the target.
            image: The image of the target.
            active_flag: Whether or not the target is active for query.

        Returns:
            The target ID of the new target.
        """
        image_data = image.getvalue()
        image_data_encoded = base64.b64encode(image_data).decode('ascii')

        data = {
            'name': name,
            'width': width,
            'image': image_data_encoded,
            'active_flag': active_flag,
        }

        content = bytes(json.dumps(data), encoding='utf-8')

        response = _target_api_request(
            server_access_key=self._server_access_key,
            server_secret_key=self._server_secret_key,
            method='POST',
            content=content,
            request_path='/targets',
            base_vws_url=self._base_vws_url,
        )

        return str(response.json()['target_id'])

    def get_target(self, target_id: str) -> Dict[str, Any]:
        """
        Get details of a given target.

        Args:
            target_id: The ID of the target to get details of.

        Returns:
            Response details of a target from Vuforia.
        """
        response = _target_api_request(
            server_access_key=self._server_access_key,
            server_secret_key=self._server_secret_key,
            method='GET',
            content=b'',
            request_path=f'/targets/{target_id}',
            base_vws_url=self._base_vws_url,
        )

        return dict(response.json())

    @timeout_decorator.timeout(seconds=60 * 5)
    def wait_for_target_processed(self, target_id: str) -> None:
        """
        Wait up to five minutes (arbitrary) for a target to get past the
        processing stage.

        Args:
            target_id: The ID of the target to wait for.

        Raises:
            TimeoutError: The target remained in the processing stage for more
                than five minutes.
        """
        while True:
            target_details = self.get_target(target_id=target_id)
            if target_details['status'] != 'processing':
                return

            # We wait 0.2 seconds rather than less than that to decrease the
            # number of calls made to the API, to decrease the likelihood of
            # hitting the request quota.
            sleep(0.2)

    def list_targets(self) -> List[str]:
        """
        List target IDs.

        Returns:
            The IDs of all targets in the database.
        """
        response = _target_api_request(
            server_access_key=self._server_access_key,
            server_secret_key=self._server_secret_key,
            method='GET',
            content=b'',
            request_path='/targets',
            base_vws_url=self._base_vws_url,
        )

        return list(response.json()['results'])

    def get_target_summary_report(
        self,
        target_id: str,
    ) -> Dict[str, Union[str, int]]:
        """
        Get a summary report for a target.

        Args:
            target_id: The ID of the target to get a summary report for.

        Returns:
            Details of the target.
        """
        response = _target_api_request(
            server_access_key=self._server_access_key,
            server_secret_key=self._server_secret_key,
            method='GET',
            content=b'',
            request_path=f'/summary/{target_id}',
            base_vws_url=self._base_vws_url,
        )

        return dict(response.json())