# tests/test_tools.py
import pytest
import os
from unittest.mock import patch, MagicMock
from tools.searchTool import WebSearchTool
from tools.scrapeTool import WebScrapeTool
from tools.fileTool import WriteFileTool, ReadFileTool


# ── WebSearchTool Tests ───────────────────────────────────────────
class TestWebSearchTool:

    def setup_method(self):
        """Runs before each test — creates a fresh tool instance."""
        self.tool = WebSearchTool()

    def test_tool_has_correct_name(self):
        """Tool name must match exactly what agents see."""
        assert self.tool.name == "Web Search"

    def test_tool_has_description(self):
        """Tool must have a non-empty description for agents to read."""
        assert len(self.tool.description) > 0

    def test_invalid_query_returns_string(self):
        """Tool should always return a string, never crash."""
        with patch("tools.searchTool.requests.post") as mock_post:
            mock_post.side_effect = Exception("Network error")
            result = self.tool._run(query="test query")
            assert isinstance(result, str)
            assert "ERROR" in result

    @patch("tools.searchTool.requests.post")
    def test_successful_search_returns_results(self, mock_post):
        """Successful search should return formatted results."""
        # Mock the API response
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "organic": [
                {
                    "title": "Test Article",
                    "link": "https://example.com",
                    "snippet": "Test snippet content"
                }
            ]
        }
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response

        result = self.tool._run(query="test query")
        assert "Test Article" in result
        assert "https://example.com" in result
        assert "Test snippet content" in result

    @patch("tools.searchTool.requests.post")
    def test_empty_results_handled_gracefully(self, mock_post):
        """Empty search results should return helpful message."""
        mock_response = MagicMock()
        mock_response.json.return_value = {"organic": []}
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response

        result = self.tool._run(query="xyzabcnonexistent")
        assert "No results found" in result


# ── WebScrapeTool Tests ───────────────────────────────────────────
class TestWebScrapeTool:

    def setup_method(self):
        self.tool = WebScrapeTool()

    def test_tool_has_correct_name(self):
        assert self.tool.name == "Web Scraper"

    def test_invalid_url_rejected(self):
        """URLs without http:// should be rejected immediately."""
        result = self.tool._run(url="not-a-valid-url")
        assert "ERROR" in result
        assert "Invalid URL" in result

    def test_invalid_url_without_protocol(self):
        """URL missing protocol should fail validation."""
        result = self.tool._run(url="www.example.com/page")
        assert "ERROR" in result

    @patch("tools.scrapeTool.requests.get")
    def test_successful_scrape_returns_content(self, mock_get):
        """Successful scrape should return page content."""
        mock_response = MagicMock()
        mock_response.content = (
            b"<html><body>"
            b"<script>remove this</script>"
            b"<p>Keep this content</p>"
            b"</body></html>"
        )
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        result = self.tool._run(url="https://example.com")
        assert "Keep this content" in result
        assert "remove this" not in result

    @patch("tools.scrapeTool.requests.get")
    def test_content_truncated_at_4000_chars(self, mock_get):
        """Content exceeding 4000 chars should be truncated."""
        mock_response = MagicMock()
        long_content = b"<p>" + b"x" * 5000 + b"</p>"
        mock_response.content = long_content
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        result = self.tool._run(url="https://example.com")
        assert "truncated" in result.lower()


# ── WriteFileTool Tests ───────────────────────────────────────────
class TestWriteFileTool:

    def setup_method(self):
        self.tool = WriteFileTool()

    def test_tool_has_correct_name(self):
        assert self.tool.name == "Write File"

    def test_writes_file_successfully(self, tmp_path, monkeypatch):
        """File should be written and success message returned."""
        # Redirect output to temp directory
        monkeypatch.chdir(tmp_path)

        result = self.tool._run(
            content="# Test\nHello world",
            filename="test.md",
            subfolder="reports"
        )
        assert "SUCCESS" in result
        assert "test" in result

    def test_adds_timestamp_to_filename(self, tmp_path, monkeypatch):
        """Filename should include timestamp to avoid overwrites."""
        monkeypatch.chdir(tmp_path)

        result = self.tool._run(
            content="test content",
            filename="report.md",
            subfolder="reports"
        )
        # Timestamp format: YYYYMMDD_HHMMSS
        assert "report_" in result
        assert "SUCCESS" in result

    def test_default_extension_is_markdown(self, tmp_path, monkeypatch):
        """Files without extension should default to .md"""
        monkeypatch.chdir(tmp_path)

        result = self.tool._run(
            content="test",
            filename="myfile",  # no extension
            subfolder="reports"
        )
        assert ".md" in result


# ── ReadFileTool Tests ────────────────────────────────────────────
class TestReadFileTool:

    def setup_method(self):
        self.tool = ReadFileTool()

    def test_tool_has_correct_name(self):
        assert self.tool.name == "Read File"

    def test_missing_file_returns_error(self):
        """Reading nonexistent file should return error string."""
        result = self.tool._run(filepath="output/nonexistent_file.md")
        assert "ERROR" in result
        assert "not found" in result

    def test_reads_existing_file(self, tmp_path):
        """Should successfully read a file that exists."""
        # Create a test file
        test_file = tmp_path / "test.md"
        test_file.write_text("# Hello\nThis is test content")

        result = self.tool._run(filepath=str(test_file))
        assert "Hello" in result
        assert "test content" in result