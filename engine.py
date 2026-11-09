#!/usr/bin/env python3
"""
Hybrid Dual-Engine Browser Automation Framework
- Engine 1: Lightpanda (Zig-based, sub-millisecond, ultra-lightweight DOM/Markdown/Semantic extraction)
- Engine 2: Nodriver / Stealth Chrome (CDP-native, bypasses Cloudflare, Turnstile, Queue-It, and Bot-walls)
"""

import argparse
import asyncio
import json
import os
import shutil
import subprocess
import sys

def resolve_lightpanda_bin() -> str:
    """Resolve path to Lightpanda binary via environment or PATH."""
    env_bin = os.environ.get("LIGHTPANDA_BIN")
    if env_bin:
        return env_bin
    which_bin = shutil.which("lightpanda-core") or shutil.which("lightpanda")
    if which_bin:
        return which_bin
    default_path = os.path.expanduser("~/.local/bin/lightpanda-core")
    return default_path


def resolve_chrome_bin() -> str:
    """Resolve path to Google Chrome or Chromium binary via environment or PATH."""
    env_bin = os.environ.get("CHROME_BIN")
    if env_bin:
        return env_bin
    for candidate in ("google-chrome", "google-chrome-stable", "chromium", "chromium-browser"):
        which_bin = shutil.which(candidate)
        if which_bin:
            return which_bin
    return "/usr/bin/google-chrome"


class HybridBrowser:
    def __init__(self, mode="auto", lightpanda_bin=None, chrome_bin=None):
        self.mode = mode
        self.lightpanda_bin = lightpanda_bin or resolve_lightpanda_bin()
        self.chrome_bin = chrome_bin or resolve_chrome_bin()

    def fetch_fast_dom(self, url, dump_format="markdown", timeout=15):
        """Lightpanda execution: low-latency, ultra-low memory, pure Zig engine."""
        if not os.path.exists(self.lightpanda_bin):
            return {
                "engine": "lightpanda",
                "error": f"Lightpanda binary not found at {self.lightpanda_bin}",
                "status": "binary_missing",
            }

        cmd = [
            self.lightpanda_bin,
            "fetch",
            url,
            "--dump", dump_format,
            "--log-filter", "-all",
        ]
        try:
            res = subprocess.run(cmd, capture_output=True, text=True, check=True, timeout=timeout)
            return {
                "engine": "lightpanda",
                "format": dump_format,
                "content": res.stdout.strip(),
                "status": "success",
            }
        except subprocess.TimeoutExpired:
            return {"engine": "lightpanda", "error": f"Command timed out after {timeout}s", "status": "timeout"}
        except subprocess.CalledProcessError as e:
            return {"engine": "lightpanda", "error": e.stderr.strip() or str(e), "status": "error"}
        except Exception as e:
            return {"engine": "lightpanda", "error": str(e), "status": "error"}

    async def fetch_stealth_chrome(self, url, extract_selector=None, timeout=30):
        """Nodriver execution: CDP native, bypasses bot shields."""
        try:
            import nodriver as uc
        except ImportError:
            return {
                "engine": "stealth_nodriver",
                "error": "nodriver library not installed (pip install nodriver)",
                "status": "dependency_missing",
            }

        if not os.path.exists(self.chrome_bin):
            return {
                "engine": "stealth_nodriver",
                "error": f"Chrome binary not found at {self.chrome_bin}",
                "status": "binary_missing",
            }

        browser = None
        try:
            browser = await uc.start(
                browser_executable_path=self.chrome_bin,
                headless=True,
                browser_args=["--no-sandbox", "--disable-dev-shm-usage"],
            )
            page = await browser.get(url)
            await page.sleep(2)

            if extract_selector:
                elem = await page.select(extract_selector)
                content = await elem.get_html() if elem else None
            else:
                content = await page.get_content()

            return {
                "engine": "stealth_nodriver",
                "url": url,
                "content": content,
                "status": "success",
            }
        except Exception as e:
            return {"engine": "stealth_nodriver", "error": str(e), "status": "error"}
        finally:
            if browser:
                try:
                    browser.stop()
                except Exception:
                    pass


def main():
    parser = argparse.ArgumentParser(description="Hybrid Dual-Engine Browser Automation CLI")
    parser.add_argument("url", nargs="?", default="https://example.com", help="Target URL to fetch")
    parser.add_argument("--format", default="markdown", choices=["markdown", "html", "semantic_tree"], help="Dump format")
    parser.add_argument("--engine", default="lightpanda", choices=["lightpanda", "stealth"], help="Engine selection")
    parser.add_argument("--selector", default=None, help="CSS selector for stealth extraction")
    args = parser.parse_args()

    hb = HybridBrowser()
    if args.engine == "lightpanda":
        print(f"Fetching {args.url} via Lightpanda ({args.format})...")
        res = hb.fetch_fast_dom(args.url, dump_format=args.format)
        if res.get("status") == "success":
            print(f"Extracted {len(res.get('content', ''))} characters.")
            if res.get("content"):
                print("--- Preview ---")
                print(res["content"][:300])
        else:
            print(f"Engine status: {res.get('status')}, error: {res.get('error')}", file=sys.stderr)
            sys.exit(1)
    else:
        print(f"Fetching {args.url} via Stealth Chrome...")
        res = asyncio.run(hb.fetch_stealth_chrome(args.url, extract_selector=args.selector))
        if res.get("status") == "success":
            print(f"Extracted {len(res.get('content', '') or '')} characters.")
        else:
            print(f"Engine status: {res.get('status')}, error: {res.get('error')}", file=sys.stderr)
            sys.exit(1)


if __name__ == "__main__":
    main()
