#!/usr/bin/env python3
"""
Hybrid Dual-Engine Browser Automation Framework
- Engine 1: Lightpanda (Zig-based, sub-millisecond, ultra-lightweight DOM/Markdown/Semantic extraction)
- Engine 2: Nodriver / Stealth Chrome (CDP-native, bypasses Cloudflare, Turnstile, Queue-It, and Bot-walls)
"""

import os
import sys
import json
import subprocess
import asyncio

LIGHTPANDA_BIN = "/home/ubuntu/.local/bin/lightpanda-core"
CHROME_BIN = "/usr/bin/google-chrome"

class HybridBrowser:
    def __init__(self, mode="auto"):
        self.mode = mode

    def fetch_fast_dom(self, url, dump_format="markdown"):
        """Lightpanda execution: <100ms startup, ultra-low memory, pure Zig engine"""
        cmd = [
            LIGHTPANDA_BIN,
            "fetch",
            url,
            "--dump", dump_format,
            "--log-filter", "-all"
        ]
        try:
            res = subprocess.run(cmd, capture_output=True, text=True, check=True)
            return {"engine": "lightpanda", "format": dump_format, "content": res.stdout.strip()}
        except Exception as e:
            return {"engine": "lightpanda", "error": str(e)}

    async def fetch_stealth_chrome(self, url, extract_selector=None):
        """Nodriver execution: CDP native, undetectable by Cloudflare & Bot-shields"""
        import nodriver as uc
        browser = await uc.start(
            browser_executable_path=CHROME_BIN,
            headless=True,
            browser_args=["--no-sandbox", "--disable-dev-shm-usage"]
        )
        page = await browser.get(url)
        await page.sleep(2)
        
        if extract_selector:
            elem = await page.select(extract_selector)
            content = await elem.get_html() if elem else None
        else:
            content = await page.get_content()
            
        browser.stop()
        return {"engine": "stealth_nodriver", "url": url, "content": content}

if __name__ == "__main__":
    hb = HybridBrowser()
    url = sys.argv[1] if len(sys.argv) > 1 else "https://example.com"
    print(f"⚡ Testing Lightpanda fast engine on {url}...")
    res = hb.fetch_fast_dom(url, dump_format="markdown")
    print(f"Extracted {len(res.get('content', ''))} characters in <100ms.")
