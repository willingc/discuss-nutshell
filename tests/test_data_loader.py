"""Tests for the data_loader module."""

from __future__ import annotations

from typing import TYPE_CHECKING
from unittest.mock import MagicMock, patch

import pytest
import requests

from discuss_nutshell.data_loader import get_topic

if TYPE_CHECKING:
    from pathlib import Path


class TestGetTopic:
    """Tests for get_topic function."""

    @patch("discuss_nutshell.data_loader.requests.get")
    @patch("discuss_nutshell.data_loader.Path")
    @patch("builtins.print")
    def test_get_topic_success(
        self,
        mock_print: MagicMock,
        mock_path: MagicMock,
        mock_get: MagicMock,
        tmp_path: Path,
    ) -> None:
        """Test successful topic retrieval and file writing.

        Parameters
        ----------
        mock_print : MagicMock
            Mocked print function.
        mock_path : MagicMock
            Mocked Path class.
        mock_get : MagicMock
            Mocked requests.get function.
        tmp_path : Path
            Temporary directory path provided by pytest.
        """
        # Setup mock response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.headers = {"Content-Type": "application/json"}
        mock_response.text = '{"test": "data"}'
        mock_get.return_value = mock_response

        # Setup file mock - Path(filename).open() pattern
        mock_file = MagicMock()
        mock_context_manager = MagicMock()
        mock_context_manager.__enter__ = MagicMock(return_value=mock_file)
        mock_context_manager.__exit__ = MagicMock(return_value=None)
        mock_path_instance = MagicMock()
        mock_path_instance.open.return_value = mock_context_manager
        mock_path.return_value = mock_path_instance

        # Test
        topic_id = 12345
        filename = tmp_path / "test_topic.json"
        get_topic(topic_id, filename)

        # Assertions
        mock_get.assert_called_once_with(
            f"https://discuss.python.org/t/{topic_id}.json?print=true",
            headers={
                "Authorization": "Bearer None",
                "Content-Type": "application/json",
            },
            timeout=30,
        )
        # Verify Path(filename) was called and then .open() was called
        mock_path.assert_called_once_with(filename)
        mock_path_instance.open.assert_called_once_with("w", encoding="utf-8")
        mock_file.write.assert_called_once_with('{"test": "data"}')
        mock_print.assert_called_once_with(200, "application/json")

    @patch("discuss_nutshell.data_loader.requests.get")
    @patch("discuss_nutshell.data_loader.Path")
    def test_get_topic_with_api_key(
        self,
        mock_path: MagicMock,
        mock_get: MagicMock,
        tmp_path: Path,
    ) -> None:
        """Test that headers are passed to requests.get.

        Parameters
        ----------
        mock_path : MagicMock
            Mocked Path class.
        mock_get : MagicMock
            Mocked requests.get function.
        tmp_path : Path
            Temporary directory path provided by pytest.
        """
        # Patch headers at module level
        with patch(
            "discuss_nutshell.data_loader.headers",
            {
                "Authorization": "Bearer test-api-key",
                "Content-Type": "application/json",
            },
        ):
            # Setup mock response
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.headers = {"Content-Type": "application/json"}
            mock_response.text = '{"test": "data"}'
            mock_get.return_value = mock_response

            # Setup file mock
            mock_file = MagicMock()
            mock_context_manager = MagicMock()
            mock_context_manager.__enter__ = MagicMock(return_value=mock_file)
            mock_context_manager.__exit__ = MagicMock(return_value=None)
            mock_path_instance = MagicMock()
            mock_path_instance.open.return_value = mock_context_manager
            mock_path.return_value = mock_path_instance

            # Test
            topic_id = 12345
            filename = tmp_path / "test_topic.json"
            get_topic(topic_id, filename)

            # Assertions
            mock_get.assert_called_once()
            call_args = mock_get.call_args
            assert call_args[1]["headers"]["Authorization"] == "Bearer test-api-key"
            assert call_args[1]["headers"]["Content-Type"] == "application/json"

    @patch("discuss_nutshell.data_loader.requests.get")
    @patch("discuss_nutshell.data_loader.Path")
    def test_get_topic_different_topic_ids(
        self,
        mock_path: MagicMock,
        mock_get: MagicMock,
        tmp_path: Path,
    ) -> None:
        """Test get_topic with different topic IDs.

        Parameters
        ----------
        mock_path : MagicMock
            Mocked Path class.
        mock_get : MagicMock
            Mocked requests.get function.
        tmp_path : Path
            Temporary directory path provided by pytest.
        """
        # Setup mock response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.headers = {"Content-Type": "application/json"}
        mock_response.text = '{"test": "data"}'
        mock_get.return_value = mock_response

        # Setup file mock
        mock_file = MagicMock()
        mock_context_manager = MagicMock()
        mock_context_manager.__enter__ = MagicMock(return_value=mock_file)
        mock_context_manager.__exit__ = MagicMock(return_value=None)
        mock_path_instance = MagicMock()
        mock_path_instance.open.return_value = mock_context_manager
        mock_path.return_value = mock_path_instance

        # Test with different topic IDs
        for topic_id in [104906, 12345, 99999]:
            get_topic(topic_id, tmp_path / f"topic_{topic_id}.json")
            expected_url = f"https://discuss.python.org/t/{topic_id}.json?print=true"
            mock_get.assert_any_call(
                expected_url,
                headers={
                    "Authorization": "Bearer None",
                    "Content-Type": "application/json",
                },
                timeout=30,
            )

    @patch("discuss_nutshell.data_loader.requests.get")
    @patch("discuss_nutshell.data_loader.Path")
    @patch("builtins.print")
    def test_get_topic_http_error(
        self,
        mock_print: MagicMock,
        mock_path: MagicMock,
        mock_get: MagicMock,
        tmp_path: Path,
    ) -> None:
        """Test get_topic handles HTTP error responses.

        Parameters
        ----------
        mock_print : MagicMock
            Mocked print function.
        mock_path : MagicMock
            Mocked Path class.
        mock_get : MagicMock
            Mocked requests.get function.
        tmp_path : Path
            Temporary directory path provided by pytest.
        """
        # Setup mock response with error status
        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_response.headers = {"Content-Type": "application/json"}
        mock_response.text = '{"error": "Not found"}'
        mock_get.return_value = mock_response

        # Setup file mock
        mock_file = MagicMock()
        mock_context_manager = MagicMock()
        mock_context_manager.__enter__ = MagicMock(return_value=mock_file)
        mock_context_manager.__exit__ = MagicMock(return_value=None)
        mock_path_instance = MagicMock()
        mock_path_instance.open.return_value = mock_context_manager
        mock_path.return_value = mock_path_instance

        # Test - should still write the error response
        topic_id = 12345
        filename = tmp_path / "test_topic.json"
        get_topic(topic_id, filename)

        # Should still print status code
        mock_print.assert_called_once_with(404, "application/json")

    @patch("discuss_nutshell.data_loader.requests.get")
    def test_get_topic_network_error(
        self,
        mock_get: MagicMock,
        tmp_path: Path,
    ) -> None:
        """Test get_topic handles network errors.

        Parameters
        ----------
        mock_get : MagicMock
            Mocked requests.get function.
        tmp_path : Path
            Temporary directory path provided by pytest.
        """
        # Setup mock to raise network error
        mock_get.side_effect = requests.RequestException("Network error")

        # Test - should raise exception
        topic_id = 12345
        filename = tmp_path / "test_topic.json"
        with pytest.raises(requests.RequestException, match="Network error"):
            get_topic(topic_id, filename)

    @patch("discuss_nutshell.data_loader.requests.get")
    def test_get_topic_timeout(
        self,
        mock_get: MagicMock,
        tmp_path: Path,
    ) -> None:
        """Test get_topic handles timeout errors.

        Parameters
        ----------
        mock_get : MagicMock
            Mocked requests.get function.
        tmp_path : Path
            Temporary directory path provided by pytest.
        """
        # Setup mock to raise timeout error
        mock_get.side_effect = requests.Timeout("Request timed out")

        # Test - should raise exception
        topic_id = 12345
        filename = tmp_path / "test_topic.json"
        with pytest.raises(requests.Timeout, match="Request timed out"):
            get_topic(topic_id, filename)

    @patch("discuss_nutshell.data_loader.requests.get")
    @patch("discuss_nutshell.data_loader.Path")
    def test_get_topic_file_write_error(
        self,
        mock_path: MagicMock,
        mock_get: MagicMock,
        tmp_path: Path,
    ) -> None:
        """Test get_topic handles file writing errors.

        Parameters
        ----------
        mock_path : MagicMock
            Mocked Path class.
        mock_get : MagicMock
            Mocked requests.get function.
        tmp_path : Path
            Temporary directory path provided by pytest.
        """
        # Setup mock response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.headers = {"Content-Type": "application/json"}
        mock_response.text = '{"test": "data"}'
        mock_get.return_value = mock_response

        # Setup file mock to raise error
        mock_path_instance = MagicMock()
        mock_path_instance.open.side_effect = OSError("Permission denied")
        mock_path.return_value = mock_path_instance

        # Test - should raise exception
        topic_id = 12345
        filename = tmp_path / "test_topic.json"
        with pytest.raises(OSError, match="Permission denied"):
            get_topic(topic_id, filename)

    @patch("discuss_nutshell.data_loader.requests.get")
    @patch("discuss_nutshell.data_loader.Path")
    def test_get_topic_writes_json_content(
        self,
        mock_path: MagicMock,
        mock_get: MagicMock,
        tmp_path: Path,
    ) -> None:
        """Test that get_topic writes the response text to file.

        Parameters
        ----------
        mock_path : MagicMock
            Mocked Path class.
        mock_get : MagicMock
            Mocked requests.get function.
        tmp_path : Path
            Temporary directory path provided by pytest.
        """
        # Setup mock response with JSON content
        json_content = '{"id": 123, "title": "Test Topic", "posts": []}'
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.headers = {"Content-Type": "application/json"}
        mock_response.text = json_content
        mock_get.return_value = mock_response

        # Setup file mock
        mock_file = MagicMock()
        mock_context_manager = MagicMock()
        mock_context_manager.__enter__ = MagicMock(return_value=mock_file)
        mock_context_manager.__exit__ = MagicMock(return_value=None)
        mock_path_instance = MagicMock()
        mock_path_instance.open.return_value = mock_context_manager
        mock_path.return_value = mock_path_instance

        # Test
        topic_id = 12345
        filename = tmp_path / "test_topic.json"
        get_topic(topic_id, filename)

        # Assertions
        mock_file.write.assert_called_once_with(json_content)

    @patch("discuss_nutshell.data_loader.requests.get")
    @patch("discuss_nutshell.data_loader.Path")
    def test_get_topic_uses_correct_timeout(
        self,
        mock_path: MagicMock,
        mock_get: MagicMock,
        tmp_path: Path,
    ) -> None:
        """Test that get_topic uses the correct timeout value.

        Parameters
        ----------
        mock_path : MagicMock
            Mocked Path class.
        mock_get : MagicMock
            Mocked requests.get function.
        tmp_path : Path
            Temporary directory path provided by pytest.
        """
        # Setup mock response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.headers = {"Content-Type": "application/json"}
        mock_response.text = '{"test": "data"}'
        mock_get.return_value = mock_response

        # Setup file mock
        mock_file = MagicMock()
        mock_context_manager = MagicMock()
        mock_context_manager.__enter__ = MagicMock(return_value=mock_file)
        mock_context_manager.__exit__ = MagicMock(return_value=None)
        mock_path_instance = MagicMock()
        mock_path_instance.open.return_value = mock_context_manager
        mock_path.return_value = mock_path_instance

        # Test
        topic_id = 12345
        filename = tmp_path / "test_topic.json"
        get_topic(topic_id, filename)

        # Assertions - check timeout is 30 seconds
        call_args = mock_get.call_args
        assert call_args[1]["timeout"] == 30

    @patch("discuss_nutshell.data_loader.requests.get")
    @patch("discuss_nutshell.data_loader.Path")
    def test_get_topic_url_format(
        self,
        mock_path: MagicMock,
        mock_get: MagicMock,
        tmp_path: Path,
    ) -> None:
        """Test that get_topic constructs the correct URL format.

        Parameters
        ----------
        mock_path : MagicMock
            Mocked Path class.
        mock_get : MagicMock
            Mocked requests.get function.
        tmp_path : Path
            Temporary directory path provided by pytest.
        """
        # Setup mock response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.headers = {"Content-Type": "application/json"}
        mock_response.text = '{"test": "data"}'
        mock_get.return_value = mock_response

        # Setup file mock
        mock_file = MagicMock()
        mock_context_manager = MagicMock()
        mock_context_manager.__enter__ = MagicMock(return_value=mock_file)
        mock_context_manager.__exit__ = MagicMock(return_value=None)
        mock_path_instance = MagicMock()
        mock_path_instance.open.return_value = mock_context_manager
        mock_path.return_value = mock_path_instance

        # Test
        topic_id = 104906
        filename = tmp_path / "test_topic.json"
        get_topic(topic_id, filename)

        # Assertions - check URL format
        expected_url = f"https://discuss.python.org/t/{topic_id}.json?print=true"
        call_args = mock_get.call_args
        assert call_args[0][0] == expected_url
