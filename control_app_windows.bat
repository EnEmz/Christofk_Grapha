@echo off
SET project_path=%UserProfile%\Desktop\Christofk_Grapha

echo Please type "start" to run the app or "stop" to stop it:
set /p userinput=

if "%userinput%"=="start" goto start
if "%userinput%"=="stop" goto stop

echo Invalid input. Exiting.
goto end

:start
echo Activating the virtual environment...
call "%project_path%\venv\Scripts\activate.bat"

echo Starting the Dash app...
start python "%project_path%\index.py"

echo Opening the Dash app in the web browser...
timeout /t 10
start http://127.0.0.1:8050/
goto end

:stop
echo Shutting down the Dash app...
for /f "tokens=5" %%a in ('netstat -ano ^| findstr 127.0.0.1:8050') do (
    taskkill /PID %%a /F
)
echo Server shut down.

echo Attempting to terminate any remaining Python processes...
taskkill /IM python.exe /F

echo Virtual environment 'deactivation' attempted.
goto end

:end
pause