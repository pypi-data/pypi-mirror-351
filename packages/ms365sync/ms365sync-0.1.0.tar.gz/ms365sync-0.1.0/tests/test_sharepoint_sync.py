"""
Tests for SharePointSync functionality.
"""

import tempfile
from pathlib import Path
from typing import Any, Dict
from unittest.mock import Mock, patch

import pytest

from ms365sync import SharePointSync


class TestSharePointSync:
    """Test cases for SharePointSync class."""

    @patch("ms365sync.sharepoint_sync.msal.ConfidentialClientApplication")
    @patch("ms365sync.sharepoint_sync.requests.get")
    def test_init(self, mock_get: Mock, mock_msal_app: Mock) -> None:
        """Test SharePointSync initialization."""
        # Mock MSAL authentication
        mock_app_instance = Mock()
        mock_app_instance.acquire_token_for_client.return_value = {
            "access_token": "test_token"
        }
        mock_msal_app.return_value = mock_app_instance

        # Mock site and drive API calls
        mock_site_response = Mock()
        mock_site_response.json.return_value = {"id": "test_site_id"}

        mock_drives_response = Mock()
        mock_drives_response.json.return_value = {
            "value": [{"id": "test_drive_id", "name": "Restricted Test PDFs"}]
        }

        mock_get.side_effect = [mock_site_response, mock_drives_response]

        # Test initialization
        syncer = SharePointSync()

        assert syncer.site_id == "test_site_id"
        assert syncer.drive_id == "test_drive_id"
        assert "Authorization" in syncer.headers
        assert syncer.headers["Authorization"] == "Bearer test_token"

    def test_compare_files_empty(self) -> None:
        """Test file comparison with empty file lists."""
        syncer = SharePointSync.__new__(
            SharePointSync
        )  # Create instance without __init__

        added, modified, deleted = syncer.compare_files({}, {})

        assert added == []
        assert modified == []
        assert deleted == []

    def test_compare_files_added(self) -> None:
        """Test file comparison with added files."""
        syncer = SharePointSync.__new__(SharePointSync)

        sp_files: Dict[str, Dict[str, Any]] = {"test.pdf": {"size": 1000, "last_modified": "2024-01-01T10:00:00Z"}}
        local_files: Dict[str, Dict[str, Any]] = {}

        added, modified, deleted = syncer.compare_files(sp_files, local_files)

        assert added == ["test.pdf"]
        assert modified == []
        assert deleted == []

    def test_compare_files_deleted(self) -> None:
        """Test file comparison with deleted files."""
        syncer = SharePointSync.__new__(SharePointSync)

        sp_files: Dict[str, Dict[str, Any]] = {}
        local_files: Dict[str, Dict[str, Any]] = {
            "test.pdf": {"size": 1000, "last_modified": "2024-01-01T10:00:00Z"}
        }

        added, modified, deleted = syncer.compare_files(sp_files, local_files)

        assert added == []
        assert modified == []
        assert deleted == ["test.pdf"]

    def test_compare_files_modified(self) -> None:
        """Test file comparison with modified files."""
        syncer = SharePointSync.__new__(SharePointSync)

        sp_files: Dict[str, Dict[str, Any]] = {
            "test.pdf": {
                "size": 2000,  # Different size
                "last_modified": "2024-01-01T10:00:00Z",
            }
        }
        local_files: Dict[str, Dict[str, Any]] = {
            "test.pdf": {"size": 1000, "last_modified": "2024-01-01T09:00:00Z"}
        }

        added, modified, deleted = syncer.compare_files(sp_files, local_files)

        assert added == []
        assert modified == ["test.pdf"]
        assert deleted == []

    def test_get_local_files_empty_directory(self) -> None:
        """Test getting local files from empty directory."""
        syncer = SharePointSync.__new__(SharePointSync)

        with tempfile.TemporaryDirectory() as temp_dir:
            syncer.local_root = Path(temp_dir)
            files = syncer.get_local_files()

            assert files == {}

    def test_get_local_files_with_files(self) -> None:
        """Test getting local files from directory with files."""
        syncer = SharePointSync.__new__(SharePointSync)

        with tempfile.TemporaryDirectory() as temp_dir:
            # Create test files
            test_file = Path(temp_dir) / "test.pdf"
            test_file.write_text("test content")

            # Create subdirectory with file
            subdir = Path(temp_dir) / "subdir"
            subdir.mkdir()
            sub_file = subdir / "sub.pdf"
            sub_file.write_text("sub content")

            syncer.local_root = Path(temp_dir)
            files = syncer.get_local_files()

            assert "test.pdf" in files
            assert "subdir/sub.pdf" in files
            assert files["test.pdf"]["size"] == len("test content")
            assert files["subdir/sub.pdf"]["size"] == len("sub content")

    def test_init_with_custom_paths(self) -> None:
        """Test SharePointSync initialization with custom paths."""
        with tempfile.TemporaryDirectory() as temp_dir:
            local_root = Path(temp_dir) / "downloads"
            sync_logs_dir = Path(temp_dir) / "logs"

            with patch(
                "ms365sync.sharepoint_sync.msal.ConfidentialClientApplication"
            ) as mock_msal_app, patch(
                "ms365sync.sharepoint_sync.requests.get"
            ) as mock_get:
                # Mock MSAL authentication
                mock_app_instance = Mock()
                mock_app_instance.acquire_token_for_client.return_value = {
                    "access_token": "test_token"
                }
                mock_msal_app.return_value = mock_app_instance

                # Mock site and drive API calls
                mock_site_response = Mock()
                mock_site_response.json.return_value = {"id": "test_site_id"}

                mock_drives_response = Mock()
                mock_drives_response.json.return_value = {
                    "value": [{"id": "test_drive_id", "name": "Restricted Test PDFs"}]
                }

                mock_get.side_effect = [mock_site_response, mock_drives_response]

                # Test initialization with custom paths
                syncer = SharePointSync(
                    local_root=local_root,
                    sync_logs_dir=sync_logs_dir,
                )

                assert syncer.local_root == local_root
                assert syncer.sync_logs_dir == sync_logs_dir

    def test_init_with_default_paths(self) -> None:
        """Test SharePointSync initialization with default paths."""
        with patch(
            "ms365sync.sharepoint_sync.msal.ConfidentialClientApplication"
        ) as mock_msal_app, patch("ms365sync.sharepoint_sync.requests.get") as mock_get:
            # Mock MSAL authentication
            mock_app_instance = Mock()
            mock_app_instance.acquire_token_for_client.return_value = {
                "access_token": "test_token"
            }
            mock_msal_app.return_value = mock_app_instance

            # Mock site and drive API calls
            mock_site_response = Mock()
            mock_site_response.json.return_value = {"id": "test_site_id"}

            mock_drives_response = Mock()
            mock_drives_response.json.return_value = {
                "value": [{"id": "test_drive_id", "name": "Restricted Test PDFs"}]
            }

            mock_get.side_effect = [mock_site_response, mock_drives_response]

            # Test initialization with defaults
            syncer = SharePointSync()

            assert syncer.local_root == Path("download")
            assert syncer.sync_logs_dir == Path("sync_logs")

    @pytest.fixture(autouse=True)
    def setup_env_vars(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Set up required environment variables for tests."""
        monkeypatch.setenv("TENANT_ID", "test_tenant_id")
        monkeypatch.setenv("CLIENT_ID", "test_client_id")
        monkeypatch.setenv("CLIENT_SECRET", "test_client_secret")
