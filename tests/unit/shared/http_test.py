import pytest

from pytest_mock import MockerFixture

from svs_core.shared.http import is_url, send_http_request


class TestSendHttpRequest:
    @pytest.mark.unit
    def test_send_http_request_get_success(self, mocker: MockerFixture) -> None:
        """Test successful GET request."""
        mock_response = mocker.MagicMock()
        mock_response.status_code = 200
        mock_response.text = '{"message": "success"}'
        mock_response.raise_for_status = mocker.MagicMock()

        mock_client = mocker.MagicMock()
        mock_client.request = mocker.MagicMock(return_value=mock_response)
        mock_client.__enter__ = mocker.MagicMock(return_value=mock_client)
        mock_client.__exit__ = mocker.MagicMock(return_value=None)

        mocker.patch("svs_core.shared.http.httpx.Client", return_value=mock_client)

        response = send_http_request(
            method="GET",
            url="https://api.example.com/test",
        )

        assert response.status_code == 200
        mock_client.request.assert_called_once_with(
            method="GET",
            url="https://api.example.com/test",
            headers=None,
            params=None,
            data=None,
            json=None,
        )

    @pytest.mark.unit
    def test_send_http_request_post_with_json(self, mocker: MockerFixture) -> None:
        """Test POST request with JSON data."""
        mock_response = mocker.MagicMock()
        mock_response.status_code = 201
        mock_response.text = '{"id": 123}'
        mock_response.raise_for_status = mocker.MagicMock()

        mock_client = mocker.MagicMock()
        mock_client.request = mocker.MagicMock(return_value=mock_response)
        mock_client.__enter__ = mocker.MagicMock(return_value=mock_client)
        mock_client.__exit__ = mocker.MagicMock(return_value=None)

        mocker.patch("svs_core.shared.http.httpx.Client", return_value=mock_client)

        test_data = {"name": "test", "value": 42}
        response = send_http_request(
            method="POST",
            url="https://api.example.com/create",
            json=test_data,
        )

        assert response.status_code == 201
        mock_client.request.assert_called_once_with(
            method="POST",
            url="https://api.example.com/create",
            headers=None,
            params=None,
            data=None,
            json=test_data,
        )

    @pytest.mark.unit
    def test_send_http_request_with_headers_and_params(
        self, mocker: MockerFixture
    ) -> None:
        """Test request with headers and query parameters."""
        mock_response = mocker.MagicMock()
        mock_response.status_code = 200
        mock_response.text = "OK"
        mock_response.raise_for_status = mocker.MagicMock()

        mock_client = mocker.MagicMock()
        mock_client.request = mocker.MagicMock(return_value=mock_response)
        mock_client.__enter__ = mocker.MagicMock(return_value=mock_client)
        mock_client.__exit__ = mocker.MagicMock(return_value=None)

        mocker.patch("svs_core.shared.http.httpx.Client", return_value=mock_client)

        headers = {"Authorization": "Bearer token123"}
        params = {"search": "query", "limit": "10"}

        response = send_http_request(
            method="GET",
            url="https://api.example.com/search",
            headers=headers,
            params=params,
        )

        assert response.status_code == 200
        mock_client.request.assert_called_once_with(
            method="GET",
            url="https://api.example.com/search",
            headers=headers,
            params=params,
            data=None,
            json=None,
        )

    @pytest.mark.unit
    def test_send_http_request_put_with_form_data(self, mocker: MockerFixture) -> None:
        """Test PUT request with form data."""
        mock_response = mocker.MagicMock()
        mock_response.status_code = 200
        mock_response.text = "Updated"
        mock_response.raise_for_status = mocker.MagicMock()

        mock_client = mocker.MagicMock()
        mock_client.request = mocker.MagicMock(return_value=mock_response)
        mock_client.__enter__ = mocker.MagicMock(return_value=mock_client)
        mock_client.__exit__ = mocker.MagicMock(return_value=None)

        mocker.patch("svs_core.shared.http.httpx.Client", return_value=mock_client)

        form_data = {"field1": "value1", "field2": "value2"}

        response = send_http_request(
            method="PUT",
            url="https://api.example.com/update/1",
            data=form_data,
        )

        assert response.status_code == 200
        mock_client.request.assert_called_once_with(
            method="PUT",
            url="https://api.example.com/update/1",
            headers=None,
            params=None,
            data=form_data,
            json=None,
        )

    @pytest.mark.unit
    def test_send_http_request_delete(self, mocker: MockerFixture) -> None:
        """Test DELETE request."""
        mock_response = mocker.MagicMock()
        mock_response.status_code = 204
        mock_response.text = ""
        mock_response.raise_for_status = mocker.MagicMock()

        mock_client = mocker.MagicMock()
        mock_client.request = mocker.MagicMock(return_value=mock_response)
        mock_client.__enter__ = mocker.MagicMock(return_value=mock_client)
        mock_client.__exit__ = mocker.MagicMock(return_value=None)

        mocker.patch("svs_core.shared.http.httpx.Client", return_value=mock_client)

        response = send_http_request(
            method="DELETE",
            url="https://api.example.com/delete/1",
        )

        assert response.status_code == 204

    @pytest.mark.unit
    def test_send_http_request_raises_on_http_error(
        self, mocker: MockerFixture
    ) -> None:
        """Test that raise_for_status is called to raise on HTTP errors."""
        mock_response = mocker.MagicMock()
        mock_response.status_code = 404
        mock_response.text = "Not Found"
        mock_response.raise_for_status = mocker.MagicMock(
            side_effect=Exception("404 Not Found")
        )

        mock_client = mocker.MagicMock()
        mock_client.request = mocker.MagicMock(return_value=mock_response)
        mock_client.__enter__ = mocker.MagicMock(return_value=mock_client)
        mock_client.__exit__ = mocker.MagicMock(return_value=None)

        mocker.patch("svs_core.shared.http.httpx.Client", return_value=mock_client)

        with pytest.raises(Exception, match="404 Not Found"):
            send_http_request(
                method="GET",
                url="https://api.example.com/missing",
            )


class TestIsUrl:
    @pytest.mark.unit
    @pytest.mark.parametrize(
        "url,expected",
        [
            # Valid URLs
            ("http://example.com", True),
            ("https://example.com", True),
            ("https://www.example.com", True),
            ("https://example.com/path/to/resource", True),
            ("https://example.com/search?q=test&limit=10", True),
            ("https://example.com/page#section", True),
            ("https://example.com:8080/api", True),
            ("https://api.example.com", True),
            ("https://my-example.com", True),
            ("http://localhost:3000", True),
            ("http://192.168.1.1", True),
            ("http://192.168.1.1:8000/api", True),
            # Invalid URLs
            ("example.com", False),
            ("ftp://example.com", False),
            ("", False),
            ("just some text", False),
            ("https://", False),
        ],
    )
    def test_is_url(self, url: str, expected: bool) -> None:
        """Test URL validation with various inputs."""
        assert is_url(url) is expected
