@echo off
REM SwissAirDry - Quickstart Script
REM Startet die SwissAirDry-Plattform mit allen Komponenten

echo ============================================
echo        SwissAirDry Quickstart v1.0.0       
echo ============================================
echo.

REM Aktualisierung prüfen
if "%1"=="--update" goto update
if "%1"=="-u" goto update
goto continue

:update
echo Aktualisierung wird gestartet...
if exist "tools\update_system.bat" (
    call tools\update_system.bat
) else (
    echo [FEHLER] Update-Script nicht gefunden.
    echo Bitte führen Sie die Aktualisierung manuell durch.
)
echo.

:continue
REM Umgebungsvariablen aus .env-Datei laden
if exist ".env" (
    echo Umgebungsvariablen werden geladen...
    for /f "tokens=*" %%a in (.env) do (
        set %%a
    )
    echo Umgebungsvariablen geladen.
) else (
    echo [WARNUNG] Keine .env-Datei gefunden. Umgebungsvariablen müssen manuell gesetzt werden.
)
echo.

REM Prüfen, ob der Cloudflare API-Token konfiguriert ist
if "%CLOUDFLARE_API_TOKEN%"=="" (
    echo [WARNUNG] CLOUDFLARE_API_TOKEN ist nicht konfiguriert.
    echo Die Domainverwaltung wird nicht funktionieren.
    echo Bitte setzen Sie den Token in der .env-Datei:
    echo CLOUDFLARE_API_TOKEN=Ihr_Cloudflare_API_Token
    echo.
)

REM Prüfen, ob Python installiert ist
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [FEHLER] Python ist nicht installiert.
    echo Bitte installieren Sie Python und versuchen Sie es erneut.
    exit /b 1
)

REM Prüfen, ob Docker installiert ist und läuft
set USE_DOCKER=false
docker --version >nul 2>&1
if %errorlevel% equ 0 (
    echo Docker ist installiert.
    
    REM Prüfen, ob docker-compose.yml vorhanden ist
    if exist "docker-compose.yml" (
        echo [FRAGE] Möchten Sie die Anwendung mit Docker starten? (j/n)
        set /p START_WITH_DOCKER="> "
        
        if /i "%START_WITH_DOCKER%"=="j" set USE_DOCKER=true
    )
    echo.
)

REM Anwendung starten (mit Docker oder direkt)
if "%USE_DOCKER%"=="true" (
    echo Starte SwissAirDry mit Docker...
    docker-compose down
    docker-compose up -d
    
    echo SwissAirDry wurde erfolgreich mit Docker gestartet.
    echo Zugangsdaten:
    echo - Web-Interface: http://localhost:5000
    echo - Domain-Verwaltung: http://localhost:5000/domains
    echo - MQTT-Broker: localhost:1883
    
    echo.
    echo Container-Status:
    docker-compose ps
) else (
    echo Starte SwissAirDry direkt...
    
    REM Datenbank initialisieren (falls notwendig)
    if exist "main.py" (
        echo Initialisiere Datenbank...
        python -c "from main import models; from sqlalchemy import create_engine; import os; engine = create_engine(os.environ.get('DATABASE_URL')); models.Base.metadata.create_all(bind=engine)" 2>nul
    )
    
    REM Anwendung starten
    echo Starte Hauptanwendung...
    start /B python main.py
    
    REM Warten, bis die Anwendung gestartet ist
    timeout /t 2 /nobreak >nul
    
    echo SwissAirDry wurde gestartet.
    echo Zugangsdaten:
    echo - Web-Interface: http://localhost:5000
    echo - Domain-Verwaltung: http://localhost:5000/domains
)

echo.
echo ============================================
echo       SwissAirDry läuft jetzt!       
echo ============================================
echo.
echo Informationen:
echo - Version: v1.0.0
echo - Release-Tag: ins
echo - Commit-Hash: f307b0c
echo.
echo Bei Problemen:
echo - Überprüfen Sie die Logdateien
echo - Führen Sie 'tools\generate_install_report.bat' aus
echo - Besuchen Sie die GitHub-Seite: https://github.com/Arduinoeinsteiger/ERP
echo.
echo Zum Beenden: STRG+C drücken und dann 'j' eingeben

REM Warten auf Benutzerinteraktion
if "%USE_DOCKER%"=="false" (
    pause
)