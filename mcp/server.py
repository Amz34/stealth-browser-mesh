#!/usr/bin/env python3
"""
Enterprise Hybrid Browser MCP Server
Exposes high-speed Lightpanda extraction and Stealth Nodriver CDP tools
to Claude Code, Codex, Antigravity, and Agentic swarms.
"""

import asyncio
import os
import shutil
import subprocess
import sys

try:
    from fastmcp import FastMCP
except ImportError:
    FastMCP = None

def resolve_lightpanda_bin() -> str:
    env_bin = os.environ.get("LIGHTPANDA_BIN")
    if env_bin:
        return env_bin
    which_bin = shutil.which("lightpanda-core") or shutil.which("lightpanda")
    if which_bin:
        return which_bin
    return os.path.expanduser("~/.local/bin/lightpanda-core")


def resolve_chrome_bin() -> str:
    env_bin = os.environ.get("CHROME_BIN")
    if env_bin:
        return env_bin
    for candidate in ("google-chrome", "google-chrome-stable", "chromium", "chromium-browser"):
        which_bin = shutil.which(candidate)
        if which_bin:
            return which_bin
    return "/usr/bin/google-chrome"


def lightpanda_scrape_impl(url: str, format: str = "markdown") -> str:
    bin_path = resolve_lightpanda_bin()
    if not os.path.exists(bin_path):
        return f"Lightpanda error: binary not found at {bin_path}"
    cmd = [
        bin_path,
        "fetch",
        url,
        "--dump", format,
        "--log-filter", "-all",
    ]
    try:
        res = subprocess.run(cmd, capture_output=True, text=True, timeout=15)
        return res.stdout.strip() or f"Error or empty output: {res.stderr}"
    except Exception as e:
        return f"Lightpanda error: {str(e)}"


async def stealth_clone_element_impl(url: str, selector: str = "body") -> str:
    try:
        import nodriver as uc
    except ImportError:
        return "Stealth browser error: nodriver package is not installed."

    chrome_bin = resolve_chrome_bin()
    if not os.path.exists(chrome_bin):
        return f"Stealth browser error: Chrome binary not found at {chrome_bin}"

    browser = None
    try:
        browser = await uc.start(
            browser_executable_path=chrome_bin,
            headless=True,
            browser_args=["--no-sandbox", "--disable-dev-shm-usage"],
        )
        page = await browser.get(url)
        await page.sleep(3)

        if selector and selector != "body":
            elem = await page.select(selector)
            html = await elem.get_html() if elem else "Element not found"
        else:
            html = await page.get_content()

        return html[:15000]
    except Exception as e:
        return f"Stealth browser error: {str(e)}"
    finally:
        if browser:
            try:
                browser.stop()
            except Exception:
                pass


if FastMCP is not None:
    mcp = FastMCP("enterprise-hybrid-browser")

    @mcp.tool()
    def lightpanda_scrape(url: str, format: str = "markdown") -> str:
        """
        Sub-millisecond high-speed DOM/Markdown scraper via Lightpanda (Zig-based native browser).
        Supported formats: markdown, html, semantic_tree.
        """
        return lightpanda_scrape_impl(url, format)

    @mcp.tool()
    async def stealth_clone_element(url: str, selector: str = "body") -> str:
        """
        Stealth Chrome CDP scraper via nodriver. Bypasses Cloudflare, Turnstile, bot-walls,
        and anti-automation defenses. Clones DOM and styles without detection.
        """
        return await stealth_clone_element_impl(url, selector)
else:
    mcp = None


if __name__ == "__main__":
    if mcp is None:
        print("fastmcp is not installed. Install with `pip install fastmcp`.", file=sys.stderr)
        sys.exit(1)
    mcp.run()
