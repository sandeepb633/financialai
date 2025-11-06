@echo off
echo Starting Financial GraphRAG Auto-Refresh Service...
echo.
cd /d "%~dp0"
".venv\Scripts\python.exe" auto_refresh_service.py
pause
