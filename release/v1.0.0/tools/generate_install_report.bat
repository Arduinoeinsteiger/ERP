@echo off
REM SwissAirDry - Installations-Report-Generator
REM Dieses Skript generiert einen Bericht über die Systemumgebung und Installationsstatus
REM von SwissAirDry v1.0.0

REM Variablen
set REPORT_FILE=swissairdry_install_report_%date:~-4%%date:~3,2%%date:~0,2%_%time:~0,2%%time:~3,2%%time:~6,2%.txt
set REPORT_FILE=%REPORT_FILE: =0%

REM Report-Header
echo ============================================ > %REPORT_FILE%
echo        SwissAirDry Installation Report      >> %REPORT_FILE%
echo              Version: v1.0.0                >> %REPORT_FILE%
echo ============================================ >> %REPORT_FILE%
echo Datum: %date% %time% >> %REPORT_FILE%
echo Computername: %COMPUTERNAME% >> %REPORT_FILE%
echo. >> %REPORT_FILE%

REM Betriebssystem-Informationen
echo ## Betriebssystem >> %REPORT_FILE%
systeminfo | findstr /B /C:"OS Name" /C:"OS Version" /C:"System Type" >> %REPORT_FILE%
echo. >> %REPORT_FILE%

REM Python-Umgebung
echo ## Python-Umgebung >> %REPORT_FILE%
python --version 2>&1 | find "Python" > nul
if %errorlevel% equ 0 (
    python --version 2>&1 >> %REPORT_FILE%
    where python >> %REPORT_FILE%
    
    echo Installierte Pakete: >> %REPORT_FILE%
    pip list | findstr /I "flask sqlalchemy requests paho-mqtt bleak psycopg2 gunicorn jinja2" >> %REPORT_FILE%
) else (
    echo Python ist nicht installiert >> %REPORT_FILE%
)
echo. >> %REPORT_FILE%

REM Systemressourcen
echo ## Systemressourcen >> %REPORT_FILE%
echo Arbeitsspeicher: >> %REPORT_FILE%
systeminfo | findstr /C:"Gesamter physischer Speicher" /C:"Verfügbarer physischer Speicher" >> %REPORT_FILE%

echo Festplattenspeicher: >> %REPORT_FILE%
wmic logicaldisk where "DeviceID='C:'" get Size,FreeSpace,Caption | more >> %REPORT_FILE%
echo. >> %REPORT_FILE%

REM Netzwerk-Informationen
echo ## Netzwerk >> %REPORT_FILE%
echo Computername: %COMPUTERNAME% >> %REPORT_FILE%
echo IP-Adressen: >> %REPORT_FILE%
ipconfig | findstr /i "IPv4" >> %REPORT_FILE%
echo. >> %REPORT_FILE%

REM Docker-Status
echo ## Docker-Status >> %REPORT_FILE%
docker --version > nul 2>&1
if %errorlevel% equ 0 (
    docker --version >> %REPORT_FILE%
    echo Docker Compose installiert: || findstr /C:"docker-compose" > nul 2>&1 && (echo Ja) || (echo Nein) >> %REPORT_FILE%
    
    REM Prüfen, ob Docker-Daemon läuft
    docker info > nul 2>&1
    if %errorlevel% equ 0 (
        echo Docker-Daemon: Läuft >> %REPORT_FILE%
        
        REM SwissAirDry Docker-Container auflisten
        echo SwissAirDry Container: >> %REPORT_FILE%
        docker ps --filter "name=swissairdry" >> %REPORT_FILE%
    ) else (
        echo Docker-Daemon: Gestoppt >> %REPORT_FILE%
    )
) else (
    echo Docker ist nicht installiert >> %REPORT_FILE%
)
echo. >> %REPORT_FILE%

REM SwissAirDry-Konfiguration
echo ## SwissAirDry-Konfiguration >> %REPORT_FILE%
REM Prüfen, ob .env-Datei existiert
if exist ..\.env (
    echo .env-Datei: Vorhanden >> %REPORT_FILE%
    REM Prüfen, ob CLOUDFLARE_API_TOKEN konfiguriert ist (ohne den Wert anzuzeigen)
    findstr /C:"CLOUDFLARE_API_TOKEN=" ..\.env > nul
    if %errorlevel% equ 0 (
        echo Cloudflare API-Token: Konfiguriert >> %REPORT_FILE%
    ) else (
        echo Cloudflare API-Token: Nicht konfiguriert >> %REPORT_FILE%
    )
) else (
    echo .env-Datei: Nicht vorhanden >> %REPORT_FILE%
)

REM Prüfen, ob Domain-Management-Module vorhanden sind
if exist ..\domain_management (
    echo Domain-Management-Module: Installiert >> %REPORT_FILE%
) else (
    echo Domain-Management-Module: Nicht installiert >> %REPORT_FILE%
)
echo. >> %REPORT_FILE%

REM Zusammenfassung
echo ## Zusammenfassung >> %REPORT_FILE%
echo SwissAirDry v1.0.0 Installationsbericht wurde erstellt. >> %REPORT_FILE%
echo Für Support besuchen Sie: https://github.com/Arduinoeinsteiger/ERP >> %REPORT_FILE%
echo. >> %REPORT_FILE%
echo Report-Datei: %REPORT_FILE% >> %REPORT_FILE%

REM Ausgabe des Dateipfades
echo Installationsbericht wurde erstellt: %REPORT_FILE%
echo Sie können diesen Bericht für Support-Anfragen verwenden.

REM Öffnen des Berichts
type %REPORT_FILE%