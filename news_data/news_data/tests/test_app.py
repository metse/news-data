from unittest import mock
from unittest.mock import MagicMock

import pytest
import requests
from pyramid.testing import DummyRequest

from news_data.app import (
    NEWS_API_URL,
    REQUEST_TIMEOUT,
    fetch_topic,
    includeme,
    news,
)


class TestFetchTopic:
    @mock.patch("news_data.app.requests.get")
    def test_success(self, mock_get):
        mock_response = MagicMock()
        mock_response.json.return_value = {"status": "ok", "articles": []}
        mock_get.return_value = mock_response

        result = fetch_topic("tesla", "test-key")

        mock_get.assert_called_once_with(
            NEWS_API_URL,
            params={"q": "tesla", "sortBy": "publishedAt", "apiKey": "test-key"},
            timeout=REQUEST_TIMEOUT,
        )
        mock_response.raise_for_status.assert_called_once()
        assert result == {"status": "ok", "articles": []}

    @mock.patch("news_data.app.requests.get")
    def test_http_error_propagates(self, mock_get):
        mock_response = MagicMock()
        mock_response.raise_for_status.side_effect = requests.HTTPError("404")
        mock_get.return_value = mock_response

        with pytest.raises(requests.HTTPError):
            fetch_topic("tesla", "test-key")

    @mock.patch("news_data.app.requests.get")
    def test_timeout_propagates(self, mock_get):
        mock_get.side_effect = requests.ConnectTimeout("timed out")

        with pytest.raises(requests.ConnectTimeout):
            fetch_topic("tesla", "test-key")


class TestNewsView:
    @mock.patch.dict("os.environ", {}, clear=True)
    def test_missing_api_key(self):
        request = DummyRequest()

        result = news(request)

        assert request.response.status_int == 503
        assert result == {"error": "API key missing"}

    @mock.patch("news_data.app.fetch_topic")
    @mock.patch.dict("os.environ", {"NEWS_API_KEY": "test-key"})
    def test_all_topics_succeed(self, mock_fetch):
        mock_fetch.return_value = {"status": "ok", "articles": []}
        request = DummyRequest()

        result = news(request)

        assert set(result.keys()) == {"tesla", "bitcoin", "microsoft"}
        for topic_data in result.values():
            assert topic_data == {"status": "ok", "articles": []}

    @mock.patch("news_data.app.fetch_topic")
    @mock.patch.dict("os.environ", {"NEWS_API_KEY": "test-key"})
    def test_one_topic_fails(self, mock_fetch):
        def side_effect(topic, api_key):
            if topic == "bitcoin":
                raise requests.RequestException("connection error")
            return {"status": "ok", "articles": []}

        mock_fetch.side_effect = side_effect
        request = DummyRequest()

        result = news(request)

        assert result["tesla"] == {"status": "ok", "articles": []}
        assert result["microsoft"] == {"status": "ok", "articles": []}
        assert "error" in result["bitcoin"]
        assert "connection error" in result["bitcoin"]["error"]


class TestIncludeMe:
    def test_registers_news_route(self):
        config = MagicMock()

        includeme(config)

        config.add_route.assert_called_once_with("news", "/")
