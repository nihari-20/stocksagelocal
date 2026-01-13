@echo off
cd /d "%~dp0\.."
echo Installing dependencies...
python -m pip install -r requirements.txt
echo.
echo Starting backend...
echo If this fails with a Database error, verify your PostgreSQL is running or ask me to switch to SQLite.
echo.
python -m uvicorn app.main:app --reload
pause
