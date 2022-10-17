.PHONY: clean
clean:
	@rm -rf dist
	@find . -name "*.egg-info" -exec rm -rf {} +
	@find . -name "__pycache__" -exec rm -rf {} +

.PHONY: requirements
requirements:
	@pip install --upgrade flask jinja2 build twine

dist: clean
	@python3 -m build
	@twine check dist/*

.PHONY: install_local
install_local:
	@pip install .

.PHONY: install_remote
install_remote:
	@pip install --upgrade flask-sitemapper
