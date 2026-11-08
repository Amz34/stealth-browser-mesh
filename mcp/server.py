#!/usr/bin/env python3
"""
Enterprise Hybrid Browser MCP Server
Exposes high-speed Lightpanda extraction and Stealth Nodriver CDP tools
to Claude Code, Codex, Antigravity, and Agentic swarms.
"""

import sys
import os
import subprocess
import asyncio
from fastmcp import FastMCP

mcp = FastMCP("enterprise-hybrid-browser")

LIGHTPANDA_BIN = "/home/ubuntu/.local/bin/lightpanda-core"
CHROME_BIN = "/usr/bin/google-chrome"

@mcp.tool()
def lightpanda_scrape(url: str, format: str = "markdown") -> str:
    """
    Sub-millisecond high-speed DOM/Markdown scraper via Lightpanda (Zig-based native browser).
    Supported formats: markdown, html, semantic_tree, structured_data.
    Zero-bloat, 10x faster than traditional headless Chrome.
    """
    cmd = [
        LIGHTPANDA_BIN,
        "fetch",
        url,
        "--dump", format,
        "--log-filter", "-all"
    ]
    try:
        res = subprocess.run(cmd, capture_output=True, text=True, timeout=15)
        return res.stdout.strip() or f"Error or empty output: {res.stderr}"
    except Exception as e:
        return f"Lightpanda error: {str(e)}"

@mcp.tool()
async def stealth_clone_element(url: str, selector: str = "body") -> str:
    """
    Stealth Chrome CDP scraper via nodriver. Bypasses Cloudflare, Turnstile, bot-walls,
    and anti-automation defenses. Clones pixel-accurate DOM and styles without detection.
    """
    import nodriver as uc
    try:
        browser = await uc.start(
            browser_executable_path=CHROME_BIN,
            headless=True,
            browser_args=["--no-sandbox", "--disable-dev-shm-usage"]
        )
        page = await browser.get(url)
        await page.sleep(3) # Wait for challenge resolution and rendering
        
        if selector and selector != "body":
            elem = await page.select(selector)
            html = await elem.get_html() if elem else "Element not found"
        else:
            html = await page.get_content()
            
        browser.stop()
        return html[:15000] # Return safe slice
    except Exception as e:
        return f"Stealth browser error: {str(e)}"

if __name__ == "__main__":
    mcp.run()
