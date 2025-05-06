@echo off
REM SwissAirDry Windows-Installationsskript

echo =================================================================
echo          SwissAirDry Platform - Windows Installer
echo =================================================================
echo.

REM Prüfen, ob Python installiert ist
python --version > nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python ist nicht installiert oder nicht im PATH.
    echo Bitte installieren Sie Python 3.10 oder höher von https://www.python.org/downloads/
    echo und stellen Sie sicher, dass "Add Python to PATH" während der Installation aktiviert ist.
    pause
    exit /b 1
)

REM Prüfen, ob Git installiert ist
git --version > nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Git ist nicht installiert oder nicht im PATH.
    echo Bitte installieren Sie Git von https://git-scm.com/download/win
    pause
    exit /b 1
)

REM Frage nach Installationsordner
set "install_dir=%CD%\ERP"
set /p custom_dir="Installationsordner (Standard: %install_dir%): "
if not "%custom_dir%"=="" set "install_dir=%custom_dir%"

REM Repository klonen oder aktualisieren
if exist "%install_dir%\.git" (
    echo [INFO] Repository existiert bereits. Aktualisiere...
    cd "%install_dir%"
    git pull
) else (
    echo [INFO] Klone Repository...
    git clone https://github.com/Arduinoeinsteiger/ERP.git "%install_dir%"
)

if %errorlevel% neq 0 (
    echo [ERROR] Fehler beim Klonen oder Aktualisieren des Repositories.
    pause
    exit /b 1
)

REM Wechsele in das Projektverzeichnis
cd "%install_dir%"

REM Virtuelle Umgebung erstellen
echo [INFO] Erstelle virtuelle Python-Umgebung...
python -m venv venv
if %errorlevel% neq 0 (
    echo [ERROR] Fehler beim Erstellen der virtuellen Umgebung.
    pause
    exit /b 1
)

REM Aktiviere virtuelle Umgebung und installiere Abhängigkeiten
echo [INFO] Installiere Abhängigkeiten...
call venv\Scripts\activate.bat
python -m pip install --upgrade pip
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo [ERROR] Fehler beim Installieren der Abhängigkeiten.
    pause
    exit /b 1
)

REM Konfigurationsdatei erstellen
echo [INFO] Erstelle Konfigurationsdatei...

REM Generiere zufälligen Secret Key
set "chars=ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789"
set "secret_key="
for /L %%i in (1,1,32) do call :append_random_char
goto :create_env_file

:append_random_char
set /a rand_index=!random! %% 62
for /f "tokens=1,2" %%a in ("!rand_index! !chars!") do set "secret_key=!secret_key!!chars:~%%a,1!"
exit /b

:create_env_file
REM Erstelle .env Datei
echo [INFO] Bitte geben Sie die Datenbankverbindungsdaten ein
set /p db_host="Datenbank-Host (Standard: localhost): "
if "%db_host%"=="" set "db_host=localhost"

set /p db_port="Datenbank-Port (Standard: 5432): "
if "%db_port%"=="" set "db_port=5432"

set /p db_name="Datenbankname (Standard: swissairdry): "
if "%db_name%"=="" set "db_name=swissairdry"

set /p db_user="Datenbankbenutzer: "
set /p db_pass="Datenbankpasswort: "

echo [INFO] Bitte geben Sie die MQTT-Verbindungsdaten ein
set /p mqtt_broker="MQTT-Broker (Standard: localhost): "
if "%mqtt_broker%"=="" set "mqtt_broker=localhost"

set /p mqtt_port="MQTT-Port (Standard: 1883): "
if "%mqtt_port%"=="" set "mqtt_port=1883"

set /p mqtt_user="MQTT-Benutzer (optional): "
set /p mqtt_pass="MQTT-Passwort (optional): "

REM Schreibe Konfiguration in .env-Datei
echo DATABASE_URL=postgresql://%db_user%:%db_pass%@%db_host%:%db_port%/%db_name% > .env
echo MQTT_BROKER=%mqtt_broker% >> .env
echo MQTT_PORT=%mqtt_port% >> .env
echo MQTT_USERNAME=%mqtt_user% >> .env
echo MQTT_PASSWORD=%mqtt_pass% >> .env
echo FLASK_SECRET_KEY=%secret_key% >> .env

REM Erstelle Startskript
echo [INFO] Erstelle Startskript...
echo @echo off > start_swissairdry.bat
echo cd "%install_dir%" >> start_swissairdry.bat
echo call venv\Scripts\activate.bat >> start_swissairdry.bat
echo python main.py >> start_swissairdry.bat

REM Fertig!
echo.
echo =================================================================
echo      SwissAirDry Platform wurde erfolgreich installiert!
echo =================================================================
echo.
echo Die Anwendung kann über start_swissairdry.bat gestartet werden.
echo Bitte stellen Sie sicher, dass PostgreSQL und MQTT-Broker installiert
echo und erreichbar sind, wie in der Konfiguration angegeben.
echo.
echo PostgreSQL: https://www.postgresql.org/download/windows/
echo Mosquitto MQTT: https://mosquitto.org/download/
echo.
echo Um das Programm jetzt zu starten, geben Sie "start_swissairdry.bat" ein.
echo.

REM Frage, ob die Anwendung gestartet werden soll
set /p start_now="Möchten Sie SwissAirDry jetzt starten? (j/n): "
if /i "%start_now%"=="j" (
    echo [INFO] Starte SwissAirDry...
    call start_swissairdry.bat
)

pause