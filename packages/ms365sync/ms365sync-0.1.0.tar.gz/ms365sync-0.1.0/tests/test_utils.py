"""
Tests for utility functions.
"""

import io
from unittest.mock import patch

from ms365sync.utils import print_file_tree


class TestUtils:
    """Test cases for utility functions."""

    def test_print_file_tree_empty(self) -> None:
        """Test printing an empty file tree."""
        with patch("sys.stdout", new_callable=io.StringIO) as mock_stdout:
            print_file_tree({}, "TEST TREE")
            output = mock_stdout.getvalue()

            assert "=== TEST TREE ===" in output
            assert "(empty)" in output

    def test_print_file_tree_with_files(self) -> None:
        """Test printing a file tree with files."""
        files = {
            "file1.txt": {"size": 100},
            "folder/file2.txt": {"size": 200},
            "folder/subfolder/file3.txt": {"size": 300},
            "another_file.txt": {"size": 400},
        }

        with patch("sys.stdout", new_callable=io.StringIO) as mock_stdout:
            print_file_tree(files, "TEST TREE")
            output = mock_stdout.getvalue()

            assert "=== TEST TREE ===" in output
            assert "file1.txt" in output
            assert "another_file.txt" in output
            assert "folder/" in output
            assert "file2.txt" in output
            assert "subfolder/" in output
            assert "file3.txt" in output

    def test_print_file_tree_structure(self) -> None:
        """Test that the file tree structure looks correct."""
        files = {
            "root_file.txt": {"size": 100},
            "docs/readme.md": {"size": 200},
            "docs/guide.md": {"size": 300},
        }

        with patch("sys.stdout", new_callable=io.StringIO) as mock_stdout:
            print_file_tree(files, "STRUCTURE TEST")
            output = mock_stdout.getvalue()

            # Check for tree structure characters
            assert "├──" in output or "└──" in output
            assert "docs/" in output
            assert "root_file.txt" in output
            assert "readme.md" in output
            assert "guide.md" in output
