@echo off
REM SwissAirDry - Setup Script for Windows
REM This script helps with initial setup of the SwissAirDry platform

echo ============================================
echo        SwissAirDry Platform Setup
echo ============================================
echo.

REM Check for required commands
echo Checking for required commands...
where docker >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo Error: docker is required but not installed.
    echo Please install Docker Desktop and try again.
    exit /b 1
)

where docker-compose >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo Error: docker-compose is required but not installed.
    echo Please install Docker Desktop and try again.
    exit /b 1
)

where git >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo Error: git is required but not installed.
    echo Please install Git and try again.
    exit /b 1
)

echo All required commands are available.
echo.

REM Setup environment file
if exist .env (
    echo An .env file already exists.
    set /p overwrite="Do you want to overwrite it? (y/N): "
    if /i "%overwrite%"=="y" (
        copy .env.example .env /y
        echo .env file has been reset from example.
    ) else (
        echo Keeping existing .env file.
    )
) else (
    copy .env.example .env
    echo .env file created from example.
)

echo Generating secure secret keys...
REM Generate a random secret key for Flask
set "CHARS=ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789"
set "FLASK_SECRET_KEY="
for /L %%i in (1,1,32) do call :append_random_char FLASK_SECRET_KEY

REM Update the .env file with the new secret key
powershell -Command "(Get-Content .env) -replace 'FLASK_SECRET_KEY=.*', 'FLASK_SECRET_KEY=%FLASK_SECRET_KEY%' | Set-Content .env"

REM Generate a random secret key for ExApp
set "EXAPP_SECRET="
for /L %%i in (1,1,32) do call :append_random_char EXAPP_SECRET

REM Update the .env file with the new ExApp secret
powershell -Command "(Get-Content .env) -replace 'EXAPP_SECRET=.*', 'EXAPP_SECRET=%EXAPP_SECRET%' | Set-Content .env"

echo Secret keys updated.
echo.

REM Check if requirements.txt exists in backup/attached_assets
if not exist backup\attached_assets\requirements.txt (
    echo requirements.txt not found in backup/attached_assets directory.
    echo Creating directory structure...
    
    if not exist backup\attached_assets mkdir backup\attached_assets
    
    if exist requirements.txt (
        copy requirements.txt backup\attached_assets\
        echo requirements.txt copied to backup/attached_assets/.
    ) else (
        echo Creating requirements.txt from example...
        (
            echo Flask^>=2.3.3
            echo flask-cors^>=4.0.0
            echo requests^>=2.31.0
            echo paho-mqtt^>=2.2.1
            echo python-dotenv^>=1.0.0
            echo gunicorn^>=22.0.0
            echo psycopg2-binary^>=2.9.9
            echo jinja2^>=3.1.3
            echo email-validator^>=2.0.0
            echo flask-sqlalchemy^>=3.0.5
            echo bleak^>=0.21.1
        ) > backup\attached_assets\requirements.txt
        echo requirements.txt created in backup/attached_assets/.
    )
) else (
    echo requirements.txt already exists in backup/attached_assets/.
)
echo.

REM Ask if user wants to build and start containers
set /p start_now="Do you want to build and start the containers now? (y/N) "
if /i "%start_now%"=="y" (
    echo Building and starting Docker containers...
    docker-compose build
    
    if %ERRORLEVEL% EQU 0 (
        echo Docker build completed successfully.
        echo Starting containers...
        docker-compose up -d
        
        if %ERRORLEVEL% EQU 0 (
            echo Docker containers started successfully.
        ) else (
            echo Error starting Docker containers.
            exit /b 1
        )
    ) else (
        echo Docker build failed.
        exit /b 1
    )
    echo.
    
    echo Checking container status...
    docker-compose ps
    echo.
    
    echo SwissAirDry Platform should now be available at:
    echo http://localhost:5000
    echo.
    
    echo ============================================
    echo SwissAirDry Platform setup is complete!
    echo ============================================
    echo.
    echo Use the following commands to manage the system:
    echo   docker-compose up -d    - Start all services
    echo   docker-compose down     - Stop all services
    echo   docker-compose logs -f  - View service logs
    echo.
    echo For more information, refer to the documentation:
    echo   docs\docker_installation.md
    echo.
) else (
    echo ============================================
    echo SwissAirDry Platform environment is prepared!
    echo ============================================
    echo.
    echo To build and start the containers later, run:
    echo   docker-compose up -d
    echo.
    echo For more information, refer to the documentation:
    echo   docs\docker_installation.md
    echo.
)

goto :eof

:append_random_char
REM Get a random number between 0 and the length of CHARS
set /a rand_index=%random% %% 62
REM Append the character at that position to the specified variable
call set "%1=%%%1%%%CHARS:~%rand_index%,1%%"
goto :eof