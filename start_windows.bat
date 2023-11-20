@echo off
SET project_path=%UserProfile%\Desktop\Christofk_Grapha

echo Activating the virtual environment...
call %project_path%\venv\Scripts\activate.bat

echo Starting the Dash app...
start python %project_path%\index.py

echo Opening the Dash app in the web browser...
timeout /t 10
start http://127.0.0.1:8050/

pause