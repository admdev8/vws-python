"""
Tests for the mock of the target summary endpoint.
"""

import pytest
from urllib.parse import urljoin

import requests
from requests import codes
from requests_mock import GET

from common.constants import ResultCodes
from tests.mock_vws.utils import assert_vws_response
from tests.utils import VuforiaServerCredentials
from vws._request_utils import authorization_header, rfc_1123_date


@pytest.mark.usefixtures('verify_mock_vuforia')
class TestTargetSummary:
    """
    Tests for the target summary endpoint.
    """

    def test_target_summary(
        self,
        vuforia_server_credentials: VuforiaServerCredentials,
        target_id: str,
    ) -> None:
        """
        A target summary is returned.
        """
        content_type = 'application/json'
        date = rfc_1123_date()
        request_path = '/summary/' + target_id

        authorization_string = authorization_header(
            access_key=vuforia_server_credentials.access_key,
            secret_key=vuforia_server_credentials.secret_key,
            method=GET,
            content=b'',
            content_type=content_type,
            date=date,
            request_path=request_path,
        )

        headers = {
            "Authorization": authorization_string,
            "Date": date,
            'Content-Type': content_type,
        }

        response = requests.request(
            method=GET,
            url=urljoin('https://vws.vuforia.com/', request_path),
            headers=headers,
            data='',
        )

        assert_vws_response(
            response=response,
            status_code=codes.OK,
            result_code=ResultCodes.SUCCESS,
        )

        expected_keys = {
            'status',
            'result_code',
            'transaction_id',
            'database_name',
            'target_name',
            'upload_date',
            'active_flag',
            'tracking_rating',
            'total_recos',
            'current_month_recos',
            'previous_month_recos',
        }

        assert response.json().keys() == expected_keys

        assert response.json()['status'] == 'processing'
