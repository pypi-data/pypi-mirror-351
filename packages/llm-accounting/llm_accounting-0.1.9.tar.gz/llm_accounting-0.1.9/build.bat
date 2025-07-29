@echo off
setlocal enabledelayedexpansion
.venv\Scripts\activate && python increment_version.py && rmdir /s /q dist && python -m build && twine upload --username __token__ --password "%PYPI_TOKEN%" dist/*
