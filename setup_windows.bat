@echo off
SET project_path=%UserProfile%\Desktop\Christofk_Grapha

echo Checking if Python is installed...
where python >nul 2>nul
IF %ERRORLEVEL% NEQ 0 (
  echo Python is not installed. Please install Python and rerun this script.
  exit /b
)

echo Creating a virtual environment...
cd /d %project_path%
python -m venv venv

echo Activating the virtual environment...
call %project_path%\venv\Scripts\activate.bat

echo Installing dependencies from requirements.txt...
pip install -r requirements.txt

echo Setup is complete!
pause