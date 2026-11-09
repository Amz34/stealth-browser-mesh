.PHONY: test lint clean run

test:
	python3 -m unittest discover -s tests -v

lint:
	python3 -m py_compile engine.py mcp/server.py tests/test_hybrid_browser.py

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

run:
	python3 engine.py https://example.com
