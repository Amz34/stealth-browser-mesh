# 🌐 Enterprise Stealth Browser Mesh

[![CI](https://github.com/Amz34/stealth-browser-mesh/actions/workflows/ci.yml/badge.svg)](https://github.com/Amz34/stealth-browser-mesh/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Engine: Lightpanda](https://img.shields.io/badge/Engine-Lightpanda_(Zig)-orange.svg)](https://lightpanda.io)
[![Engine: Nodriver CDP](https://img.shields.io/badge/Anti--Bot-Nodriver_CDP-green.svg)](https://github.com/ultrafunkamsterdam/nodriver)
[![Protocol: FastMCP](https://img.shields.io/badge/Protocol-Model_Context_Protocol-purple.svg)](https://modelcontextprotocol.io)

An enterprise-grade hybrid browser mesh engineered for AI agents, swarms, and high-throughput LLM pipelines. Combines sub-millisecond, low-memory DOM extraction with undetectable Chrome DevTools Protocol automation to navigate Cloudflare walls, Turnstile challenges, and complex SPAs.

![Enterprise Stealth Browser Mesh Architecture](assets/stealth-browser-mesh-overview.jpg)

---

## 🏛️ Dual-Engine Architecture

| Capability | Engine 1: Lightpanda (Zig Core) | Engine 2: Stealth Nodriver (Chrome CDP) |
| :--- | :--- | :--- |
| **Primary Role** | High-throughput, sub-millisecond DOM & markdown extraction | Anti-bot bypass, Cloudflare challenges, full browser cloning |
| **Startup Overhead** | **< 10ms** (Instant Zig binary execution) | ~1.5s (Full Chrome instance lifecycle) |
| **RAM Footprint** | **~15 MB** per thread | ~120 MB per instance |
| **Detection Profile** | Optimized for content endpoints & reader modes | **Undetectable** (Native CDP without standard WebDriver flags) |
| **Best Use Case** | Real-time RAG ingestion, markdown dumps, semantic trees | Bypassing bot-shields, SPA cloning, event interception |

---

## 🚀 Key Features

1. **Sub-Millisecond Extraction (`lightpanda_scrape`)**
   - Native Zig engine compiles web pages into pure Markdown, Semantic Trees, or structured JSON in under 100ms.
   - Ideal for agent tool calls where latency must remain strictly constrained.

2. **Undetectable Anti-Bot Automation (`stealth_clone_element`)**
   - Eliminates `navigator.webdriver` artifacts natively by communicating directly via CDP.
   - Bypasses Cloudflare Turnstile, Queue-It, and fingerprint barriers.

3. **Universal Model Context Protocol (MCP)**
   - Pre-packaged FastMCP server ready for integration into Claude Code, Codex, Cursor, and custom agentic frameworks.

---

## 💻 CLI Quickstart

```bash
# Instant sub-millisecond markdown extraction via Lightpanda
python3 engine.py https://example.com

# Dump HTML or semantic trees
python3 engine.py https://example.com --format html

# Run via stealth engine
python3 engine.py https://example.com --engine stealth --selector "#content"

# Launch MCP server
python3 mcp/server.py
```

---

## 🧪 Testing & Verification

![Continuous Integration & Automated Testing](assets/github-benefits-cicd.jpg)

Run the test suite and verify syntax:

```bash
# Run unit tests
make test

# Verify syntax across all modules
make lint
```

---

## 🔗 Ecosystem

Part of the **[Awesome Agent Infrastructure](https://github.com/Amz34/awesome-agent-infrastructure)** curated catalogue of production-grade agent tools, scrapers, and orchestration runtimes.

---

## 🛡️ License

Licensed under **MIT**. Engineered by **[Aamir Zameer (Amz34)](https://github.com/Amz34)**.
