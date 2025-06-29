from unittest.mock import AsyncMock, MagicMock, patch

import httpx
import pytest

import svs_core.shared.http as http_mod


@pytest.mark.unit
@pytest.mark.asyncio
class TestSendHttpRequest:
    @patch("svs_core.shared.http.httpx.AsyncClient")
    async def test_send_http_request_success(self, mock_client_cls):
        """Test that send_http_request returns a successful response."""
        mock_response = MagicMock(spec=httpx.Response)
        mock_response.status_code = 200
        mock_response.text = "ok"
        mock_response.raise_for_status = MagicMock()
        mock_client = AsyncMock()
        mock_client.request.return_value = mock_response
        mock_client_cls.return_value.__aenter__.return_value = mock_client

        response = await http_mod.send_http_request(
            method="GET",
            url="https://example.com/api",
            headers={"X-Test": "1"},
            params={"q": "test"},
            data=None,
            json=None,
        )
        assert response.status_code == 200
        assert response.text == "ok"
        mock_client.request.assert_awaited_once_with(
            method="GET",
            url="https://example.com/api",
            headers={"X-Test": "1"},
            params={"q": "test"},
            data=None,
            json=None,
        )
        mock_response.raise_for_status.assert_called_once()

    @patch("svs_core.shared.http.httpx.AsyncClient")
    async def test_send_http_request_raises_for_status(self, mock_client_cls):
        """Test that send_http_request raises HTTPStatusError on non-200 response."""
        mock_response = MagicMock(spec=httpx.Response)
        mock_response.status_code = 404
        mock_response.text = "not found"
        mock_response.raise_for_status.side_effect = httpx.HTTPStatusError(
            "error", request=MagicMock(), response=MagicMock()
        )
        mock_client = AsyncMock()
        mock_client.request.return_value = mock_response
        mock_client_cls.return_value.__aenter__.return_value = mock_client

        with pytest.raises(httpx.HTTPStatusError):
            await http_mod.send_http_request(
                method="GET",
                url="https://example.com/notfound",
            )
        mock_client.request.assert_awaited_once()
        mock_response.raise_for_status.assert_called_once()
