#!/usr/bin/env python3
"""
Unit test suite for stealth-browser-mesh dual-engine framework.
Tests path resolution, CLI, mocked Lightpanda subprocess, and MCP server tools.
"""

import asyncio
import importlib.util
import os
import subprocess
import sys
import unittest
from unittest.mock import MagicMock, patch

# Add parent directory to sys.path
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, BASE_DIR)

from engine import HybridBrowser, resolve_chrome_bin, resolve_lightpanda_bin

# Dynamically load local mcp/server.py to avoid collisions with any installed 'mcp' SDK
mcp_server_path = os.path.join(BASE_DIR, "mcp", "server.py")
spec = importlib.util.spec_from_file_location("local_mcp_server", mcp_server_path)
if spec is None or spec.loader is None:
    raise ImportError(f"Could not load spec for {mcp_server_path}")
mcp_server = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mcp_server)


class TestBinaryResolution(unittest.TestCase):
    def test_resolve_lightpanda_bin(self):
        path = resolve_lightpanda_bin()
        self.assertIsInstance(path, str)
        self.assertTrue(len(path) > 0)

    def test_resolve_chrome_bin(self):
        path = resolve_chrome_bin()
        self.assertIsInstance(path, str)
        self.assertTrue(len(path) > 0)

    def test_env_override_lightpanda(self):
        with patch.dict(os.environ, {"LIGHTPANDA_BIN": "/custom/path/lightpanda"}):
            self.assertEqual(resolve_lightpanda_bin(), "/custom/path/lightpanda")

    def test_env_override_chrome(self):
        with patch.dict(os.environ, {"CHROME_BIN": "/custom/path/chrome"}):
            self.assertEqual(resolve_chrome_bin(), "/custom/path/chrome")


class TestHybridBrowser(unittest.TestCase):
    def test_init_defaults(self):
        hb = HybridBrowser()
        self.assertEqual(hb.mode, "auto")
        self.assertIsInstance(hb.lightpanda_bin, str)
        self.assertIsInstance(hb.chrome_bin, str)

    def test_fetch_fast_dom_missing_binary(self):
        hb = HybridBrowser(lightpanda_bin="/nonexistent/binary/path")
        res = hb.fetch_fast_dom("https://example.com")
        self.assertEqual(res["status"], "binary_missing")
        self.assertIn("not found", res["error"])

    @patch("os.path.exists", return_value=True)
    @patch("subprocess.run")
    def test_fetch_fast_dom_success(self, mock_run, mock_exists):
        mock_run.return_value = MagicMock(stdout="# Example Domain\nThis is a mock page.", stderr="", returncode=0)
        hb = HybridBrowser(lightpanda_bin="/usr/bin/lightpanda-core")
        res = hb.fetch_fast_dom("https://example.com", dump_format="markdown")
        self.assertEqual(res["status"], "success")
        self.assertEqual(res["engine"], "lightpanda")
        self.assertIn("Example Domain", res["content"])

    @patch("os.path.exists", return_value=True)
    @patch("subprocess.run", side_effect=subprocess.TimeoutExpired(cmd=["test"], timeout=15))
    def test_fetch_fast_dom_timeout(self, mock_run, mock_exists):
        hb = HybridBrowser(lightpanda_bin="/usr/bin/lightpanda-core")
        res = hb.fetch_fast_dom("https://example.com", timeout=15)
        self.assertEqual(res["status"], "timeout")
        self.assertIn("timed out", res["error"])

    def test_fetch_stealth_chrome_missing_binary(self):
        hb = HybridBrowser(chrome_bin="/nonexistent/chrome/path")
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            res = loop.run_until_complete(hb.fetch_stealth_chrome("https://example.com"))
            self.assertIn(res["status"], ["binary_missing", "dependency_missing", "error"])
        finally:
            loop.close()


class TestMCPServer(unittest.TestCase):
    @patch("os.path.exists", return_value=True)
    @patch("subprocess.run")
    def test_lightpanda_scrape_impl(self, mock_run, mock_exists):
        mock_run.return_value = MagicMock(stdout="## Extracted Markdown Content", stderr="")
        res = mcp_server.lightpanda_scrape_impl("https://example.com")
        self.assertEqual(res, "## Extracted Markdown Content")

    def test_lightpanda_scrape_missing_binary(self):
        with patch.dict(os.environ, {"LIGHTPANDA_BIN": "/invalid/nonexistent"}):
            res = mcp_server.lightpanda_scrape_impl("https://example.com")
            self.assertIn("binary not found", res)


class TestAssets(unittest.TestCase):
    def test_overview_artwork(self):
        asset_path = os.path.join(BASE_DIR, "assets", "stealth-browser-mesh-overview.jpg")
        self.assertTrue(os.path.exists(asset_path), f"Asset missing at {asset_path}")
        with open(asset_path, "rb") as f:
            header = f.read(2)
        self.assertEqual(header, b"\xff\xd8", "Asset must be a valid JPEG file")

    def test_cicd_artwork(self):
        asset_path = os.path.join(BASE_DIR, "assets", "github-benefits-cicd.jpg")
        self.assertTrue(os.path.exists(asset_path), f"Asset missing at {asset_path}")
        with open(asset_path, "rb") as f:
            header = f.read(2)
        self.assertEqual(header, b"\xff\xd8", "Asset must be a valid JPEG file")


if __name__ == "__main__":
    unittest.main()
