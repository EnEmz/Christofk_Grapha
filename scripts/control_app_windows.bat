@echo off
SET project_path=%UserProfile%\Desktop\Christofk_Grapha
SET scripts_path=%project_path%\scripts
SET repo_url=https://github.com/EnEmz/Christofk_Grapha
SET zip_file_name=repo.zip
SET temp_extract_path=%project_path%\temp

echo Please type "start", "stop", or "update" to run the respective commands:
set /p userinput=

if "%userinput%"=="start" goto start
if "%userinput%"=="stop" goto stop
if "%userinput%"=="update" goto update

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

:update
echo Downloading the latest version of the app...
curl -L "%repo_url%/archive/main.zip" -o "%zip_file_name%"

echo Unzipping the repository...
mkdir "%temp_extract_path%"
tar -xf "%zip_file_name%" -C "%temp_extract_path%"
xcopy /E /I /Y "%temp_extract_path%\repo-main\*" "%project_path%\"
rd /s /q "%temp_extract_path%"

echo Removing the ZIP file...
del "%zip_file_name%"

echo Updating Python dependencies...
call "%project_path%\venv\Scripts\activate.bat"
pip install -r "%project_path%\requirements.txt"
call "%project_path%\venv\Scripts\deactivate.bat"

echo Update complete.
goto end

:end
pause
