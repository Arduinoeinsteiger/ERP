@echo off
REM SwissAirDry - Installationsscript für Windows
REM 
REM Dieses Script installiert die Domainverwaltung und alle benötigten Abhängigkeiten.

echo ============================================
echo        SwissAirDry Installation            
echo ============================================
echo.

REM Überprüfen von Systemvoraussetzungen
echo Systemvoraussetzungen werden überprüft...

REM Python überprüfen
python --version > nul 2>&1
if %errorlevel% neq 0 (
    echo [FEHLER] Python ist nicht installiert oder nicht im PATH.
    echo Bitte installieren Sie Python von https://www.python.org/downloads/
    echo.
    set PYTHON_OK=0
) else (
    echo [OK] Python ist installiert.
    set PYTHON_OK=1
)

REM pip überprüfen
pip --version > nul 2>&1
if %errorlevel% neq 0 (
    echo [FEHLER] pip ist nicht installiert oder nicht im PATH.
    echo.
    set PIP_OK=0
) else (
    echo [OK] pip ist installiert.
    set PIP_OK=1
)

REM Git überprüfen
git --version > nul 2>&1
if %errorlevel% neq 0 (
    echo [FEHLER] Git ist nicht installiert oder nicht im PATH.
    echo.
    set GIT_OK=0
) else (
    echo [OK] Git ist installiert.
    set GIT_OK=1
)

echo.

REM Python-Pakete installieren
if %PYTHON_OK%==1 if %PIP_OK%==1 (
    echo Python-Abhängigkeiten werden installiert...
    pip install flask sqlalchemy requests paho-mqtt==2.1.0 bleak psycopg2-binary gunicorn jinja2
    
    if %errorlevel% equ 0 (
        echo [OK] Python-Abhängigkeiten erfolgreich installiert.
    ) else (
        echo [FEHLER] Fehler beim Installieren der Python-Abhängigkeiten.
        echo Versuchen Sie, die folgenden Pakete manuell zu installieren:
        echo pip install flask sqlalchemy requests paho-mqtt==2.1.0 bleak psycopg2-binary gunicorn jinja2
    )
) else (
    echo [FEHLER] Python oder pip ist nicht installiert. Python-Abhängigkeiten können nicht installiert werden.
    echo Bitte installieren Sie Python und pip und führen Sie das Script erneut aus.
)

echo.

REM Domain-Management-Module installieren
echo Domain-Management wird installiert...

REM Verzeichnis erstellen, falls es nicht existiert
if not exist "..\domain_management" (
    mkdir "..\domain_management"
    echo [OK] Verzeichnis 'domain_management' erstellt.
)

REM Dateien kopieren
if exist "..\domain_management" (
    xcopy /E /I /Y "..\domain_management" "..\domain_management"
    echo [OK] Domain-Management-Module wurden installiert.
) else (
    echo [FEHLER] Verzeichnis 'domain_management' konnte nicht erstellt werden.
)

echo.

REM Umgebungsvariablen konfigurieren
echo Umgebungsvariablen werden konfiguriert...

REM .env-Datei erstellen oder aktualisieren
set ENV_FILE=..\.env

REM Überprüfen, ob die .env-Datei existiert
if exist "%ENV_FILE%" (
    REM Sichern der bestehenden .env-Datei
    copy "%ENV_FILE%" "%ENV_FILE%.backup" > nul
    echo [OK] Bestehende .env-Datei gesichert unter %ENV_FILE%.backup
)

REM Überprüfen, ob CLOUDFLARE_API_TOKEN bereits in der .env-Datei ist
findstr /C:"CLOUDFLARE_API_TOKEN" "%ENV_FILE%" > nul 2>&1
if %errorlevel% equ 0 (
    echo [OK] CLOUDFLARE_API_TOKEN ist bereits in der .env-Datei konfiguriert.
) else (
    echo. >> "%ENV_FILE%"
    echo # Domain Management >> "%ENV_FILE%"
    echo CLOUDFLARE_API_TOKEN= >> "%ENV_FILE%"
    echo [OK] CLOUDFLARE_API_TOKEN zur .env-Datei hinzugefügt.
    echo [HINWEIS] Bitte setzen Sie Ihren Cloudflare API-Token in der .env-Datei.
)

echo.

REM Datenbank-Migration
echo Datenbank wird initialisiert...
if exist "..\main.py" (
    cd ..
    python -c "import os; from main import models; from sqlalchemy import create_engine; engine = create_engine(os.environ.get('DATABASE_URL')); models.Base.metadata.create_all(bind=engine)" 2>nul
    if %errorlevel% equ 0 (
        echo [OK] Datenbank erfolgreich initialisiert.
    ) else (
        echo [FEHLER] Fehler beim Initialisieren der Datenbank.
        echo Bitte führen Sie die Datenbank-Migration manuell durch.
    )
    cd install
) else (
    echo [FEHLER] Hauptanwendungsdatei (main.py) nicht gefunden. Datenbank-Migration wird übersprungen.
)

echo.

REM Abschluss
echo ============================================
echo Installation abgeschlossen!
echo ============================================
echo.
echo Nächste Schritte:
echo 1. Setzen Sie Ihren Cloudflare API-Token in der .env-Datei
echo 2. Starten Sie die Anwendung mit: python main.py
echo 3. Greifen Sie auf die Domainverwaltung zu unter: http://localhost:5000/domains
echo.
echo Bei Problemen konsultieren Sie bitte die Dokumentation in domain_management\README.md
echo.

pause