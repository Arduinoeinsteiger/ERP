@echo off
:: SwissAirDry - Quick Start Script (Plug & Play) für Windows
:: Dieses Skript bietet eine komplett automatisierte Einrichtung der SwissAirDry-Plattform

TITLE SwissAirDry Plug & Play Setup

:: Admin-Rechte prüfen
NET SESSION >nul 2>&1
IF %ERRORLEVEL% NEQ 0 (
    echo Administrator-Rechte werden benötigt.
    echo Bitte dieses Skript als Administrator ausführen.
    pause
    exit
)

cls
echo ================================================
echo        SwissAirDry Plug ^& Play Setup
echo ================================================
echo.
echo Dieses Skript richtet SwissAirDry vollautomatisch ein.
echo In wenigen Minuten ist Ihr System einsatzbereit.
echo Keine manuellen Eingriffe erforderlich!
echo.

:: Erforderliche Programme prüfen
echo Prüfe erforderliche Programme...

:: Docker prüfen/installieren
where docker >nul 2>&1
IF %ERRORLEVEL% NEQ 0 (
    echo Docker wird benötigt, aber ist nicht installiert.
    echo Bitte installieren Sie Docker Desktop von:
    echo https://www.docker.com/products/docker-desktop
    echo und führen Sie dieses Skript erneut aus.
    pause
    exit
)

:: Git prüfen/installieren
where git >nul 2>&1
IF %ERRORLEVEL% NEQ 0 (
    echo Git wird benötigt, aber ist nicht installiert.
    echo Installiere Git...
    powershell -Command "Start-Process -Wait -FilePath winget -ArgumentList 'install -e --id Git.Git'"
)

echo Alle erforderlichen Programme sind verfügbar.

:: Arbeitsverzeichnis erstellen
set INSTALL_DIR=C:\SwissAirDry
echo Erstelle Installationsverzeichnis...
if not exist "%INSTALL_DIR%" mkdir "%INSTALL_DIR%"
cd /d "%INSTALL_DIR%"

:: Repository klonen oder aktualisieren
if not exist "%INSTALL_DIR%\.git" (
    echo Lade SwissAirDry herunter...
    git clone https://github.com/Arduinoeinsteiger/ERP.git .
) else (
    echo Aktualisiere bestehende Installation...
    git pull
)

:: Umgebungsvariablen konfigurieren
echo Konfiguriere Umgebung...
copy .env.example .env

:: Sichere Schlüssel generieren
echo Generiere sichere Schlüssel...
set "CHARS=ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789"
set "FLASK_SECRET_KEY="
for /L %%i in (1,1,32) do call :append_random_char FLASK_SECRET_KEY

:: Update the .env file with the new secret key
powershell -Command "(Get-Content .env) -replace 'FLASK_SECRET_KEY=.*', 'FLASK_SECRET_KEY=%FLASK_SECRET_KEY%' | Set-Content .env"

:: Generate a random secret key for ExApp
set "EXAPP_SECRET="
for /L %%i in (1,1,32) do call :append_random_char EXAPP_SECRET

:: Update the .env file with the new ExApp secret
powershell -Command "(Get-Content .env) -replace 'EXAPP_SECRET=.*', 'EXAPP_SECRET=%EXAPP_SECRET%' | Set-Content .env"

:: Requirements-Verzeichnis erstellen
echo Stelle sicher, dass alle Dateien vorhanden sind...
if not exist "backup\attached_assets" mkdir backup\attached_assets
if not exist "backup\attached_assets\requirements.txt" (
    if exist "requirements.txt" (
        copy requirements.txt backup\attached_assets\
    ) else (
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
    )
)

:: Prüfen, ob Ports verfügbar sind
set WEB_PORT=5000
set API_PORT=8000
set MQTT_PORT=1883

:: Ports anpassen (in Windows weniger zuverlässig als in Linux)
powershell -Command "(Get-Content docker-compose.yml) -replace '- \"5000:5000\"', '- \"%WEB_PORT%:5000\"' | Set-Content docker-compose.yml"
powershell -Command "(Get-Content docker-compose.yml) -replace '- \"8000:8000\"', '- \"%API_PORT%:8000\"' | Set-Content docker-compose.yml"
powershell -Command "(Get-Content docker-compose.yml) -replace '- \"1883:1883\"', '- \"%MQTT_PORT%:1883\"' | Set-Content docker-compose.yml"

:: Container starten
echo Starte SwissAirDry-Container...
docker-compose build && docker-compose up -d

IF %ERRORLEVEL% NEQ 0 (
    echo Fehler beim Starten der Container. Bitte prüfen Sie die Logs.
    docker-compose logs
    pause
    exit
)

:: Steuerungsskript erstellen
echo @echo off > "%INSTALL_DIR%\swissairdry-control.bat"
echo cd /d "%INSTALL_DIR%" >> "%INSTALL_DIR%\swissairdry-control.bat"
echo. >> "%INSTALL_DIR%\swissairdry-control.bat"
echo if "%%1"=="start" goto start >> "%INSTALL_DIR%\swissairdry-control.bat"
echo if "%%1"=="stop" goto stop >> "%INSTALL_DIR%\swissairdry-control.bat"
echo if "%%1"=="restart" goto restart >> "%INSTALL_DIR%\swissairdry-control.bat"
echo if "%%1"=="status" goto status >> "%INSTALL_DIR%\swissairdry-control.bat"
echo if "%%1"=="logs" goto logs >> "%INSTALL_DIR%\swissairdry-control.bat"
echo if "%%1"=="update" goto update >> "%INSTALL_DIR%\swissairdry-control.bat"
echo. >> "%INSTALL_DIR%\swissairdry-control.bat"
echo echo Verwendung: swissairdry {start^|stop^|restart^|status^|logs^|update} >> "%INSTALL_DIR%\swissairdry-control.bat"
echo goto :eof >> "%INSTALL_DIR%\swissairdry-control.bat"
echo. >> "%INSTALL_DIR%\swissairdry-control.bat"
echo :start >> "%INSTALL_DIR%\swissairdry-control.bat"
echo docker-compose up -d >> "%INSTALL_DIR%\swissairdry-control.bat"
echo goto :eof >> "%INSTALL_DIR%\swissairdry-control.bat"
echo. >> "%INSTALL_DIR%\swissairdry-control.bat"
echo :stop >> "%INSTALL_DIR%\swissairdry-control.bat"
echo docker-compose down >> "%INSTALL_DIR%\swissairdry-control.bat"
echo goto :eof >> "%INSTALL_DIR%\swissairdry-control.bat"
echo. >> "%INSTALL_DIR%\swissairdry-control.bat"
echo :restart >> "%INSTALL_DIR%\swissairdry-control.bat"
echo docker-compose restart >> "%INSTALL_DIR%\swissairdry-control.bat"
echo goto :eof >> "%INSTALL_DIR%\swissairdry-control.bat"
echo. >> "%INSTALL_DIR%\swissairdry-control.bat"
echo :status >> "%INSTALL_DIR%\swissairdry-control.bat"
echo docker-compose ps >> "%INSTALL_DIR%\swissairdry-control.bat"
echo goto :eof >> "%INSTALL_DIR%\swissairdry-control.bat"
echo. >> "%INSTALL_DIR%\swissairdry-control.bat"
echo :logs >> "%INSTALL_DIR%\swissairdry-control.bat"
echo docker-compose logs -f >> "%INSTALL_DIR%\swissairdry-control.bat"
echo goto :eof >> "%INSTALL_DIR%\swissairdry-control.bat"
echo. >> "%INSTALL_DIR%\swissairdry-control.bat"
echo :update >> "%INSTALL_DIR%\swissairdry-control.bat"
echo git pull >> "%INSTALL_DIR%\swissairdry-control.bat"
echo docker-compose build >> "%INSTALL_DIR%\swissairdry-control.bat"
echo docker-compose up -d >> "%INSTALL_DIR%\swissairdry-control.bat"
echo goto :eof >> "%INSTALL_DIR%\swissairdry-control.bat"

:: Kurze Pause für Container-Start
echo Warte, bis alle Dienste gestartet sind...
timeout /t 10 /nobreak > nul

:: Lokale IP-Adresse ermitteln
for /f "tokens=2 delims=:" %%a in ('ipconfig ^| findstr /c:"IPv4"') do (
    set IP_ADDR=%%a
    goto :got_ip
)
:got_ip
set IP_ADDR=%IP_ADDR:~1%

:: Verknüpfung auf Desktop erstellen
echo Erstelle Desktop-Verknüpfung...
powershell -Command "$WshShell = New-Object -comObject WScript.Shell; $Shortcut = $WshShell.CreateShortcut([Environment]::GetFolderPath('Desktop') + '\SwissAirDry Steuerung.lnk'); $Shortcut.TargetPath = '%INSTALL_DIR%\swissairdry-control.bat'; $Shortcut.Save()"

echo ================================================
echo SwissAirDry wurde erfolgreich installiert!
echo ================================================
echo.
echo Zugriff auf das Web-Interface:
echo   http://%IP_ADDR%:%WEB_PORT%
echo.
echo MQTT-Broker ist erreichbar unter:
echo   %IP_ADDR%:%MQTT_PORT%
echo.
echo Verwenden Sie folgende Befehle zur Steuerung:
echo   - Doppelklick auf "SwissAirDry Steuerung" auf dem Desktop
echo   - Oder im Installationsverzeichnis: swissairdry-control.bat {Befehl}
echo.
echo Verfügbare Befehle:
echo   start    - Startet alle Dienste
echo   stop     - Stoppt alle Dienste
echo   restart  - Startet alle Dienste neu
echo   status   - Zeigt den Status aller Dienste
echo   logs     - Zeigt die Logs aller Dienste
echo   update   - Aktualisiert auf die neueste Version
echo.

:: Bluetooth-Fähigkeit prüfen
powershell -Command "Get-PnpDevice -Class Bluetooth | Where-Object { $_.Status -eq 'OK' }" >nul 2>&1
IF %ERRORLEVEL% EQU 0 (
    echo Bluetooth-Hardware erkannt. BLE-Funktionalität ist verfügbar.
) else (
    echo Keine Bluetooth-Hardware erkannt. BLE-Funktionalität ist eingeschränkt.
    echo Falls Sie BLE-Funktionalität benötigen, stellen Sie sicher, dass Bluetooth aktiviert ist.
)

echo.
echo Für weitere Informationen besuchen Sie die Dokumentation:
echo   %INSTALL_DIR%\docs\
echo.
echo Installation abgeschlossen! Drücken Sie eine Taste, um zu beenden...
pause > nul
exit

:append_random_char
:: Get a random number between 0 and the length of CHARS
set /a rand_index=%random% %% 62
:: Append the character at that position to the specified variable
call set "%1=%%%1%%%CHARS:~%rand_index%,1%%"
goto :eof