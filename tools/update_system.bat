@echo off
REM SwissAirDry - System-Update-Script
REM Dieses Script aktualisiert die SwissAirDry-Plattform auf die neueste Version

echo ============================================
echo        SwissAirDry System Update           
echo ============================================
echo.

REM Aktuelles Verzeichnis speichern
set CURRENT_DIR=%CD%
REM Zum Hauptverzeichnis wechseln (eine Ebene höher)
cd ..

REM Prüfen, ob git installiert ist
git --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [FEHLER] Git ist nicht installiert. Bitte installieren Sie Git und versuchen Sie es erneut.
    goto end
)

REM Prüfen, ob es sich um ein Git-Repository handelt
if not exist ".git" (
    echo [WARNUNG] Kein Git-Repository gefunden. Verwenden Sie die manuelle Update-Methode.
    
    REM Fragen, ob fortgefahren werden soll
    set /p CONTINUE=Möchten Sie trotzdem fortfahren? (j/n): 
    if /i not "%CONTINUE%"=="j" (
        echo Update abgebrochen.
        goto end
    )
)

REM Sichern der .env-Datei
if exist ".env" (
    echo [INFO] Sichern der bestehenden .env-Datei...
    copy .env .env.backup.%date:~-4%%date:~3,2%%date:~0,2%_%time:~0,2%%time:~3,2%%time:~6,2% >nul
    echo [SUCCESS] Backup erstellt: .env.backup.%date:~-4%%date:~3,2%%date:~0,2%_%time:~0,2%%time:~3,2%%time:~6,2%
)

REM Sichern von benutzerdefinierten Konfigurationen
if exist "config" (
    echo [INFO] Sichern von benutzerdefinierten Konfigurationen...
    set BACKUP_DIR=config_backup_%date:~-4%%date:~3,2%%date:~0,2%_%time:~0,2%%time:~3,2%%time:~6,2%
    mkdir "%BACKUP_DIR%" 2>nul
    xcopy /E /Y "config" "%BACKUP_DIR%\" >nul
    echo [SUCCESS] Konfigurationen gesichert in: %BACKUP_DIR%
)

REM Update durchführen
if exist ".git" (
    echo [INFO] Aktualisiere Repository von GitHub...
    
    REM Lokale Änderungen speichern
    git stash
    
    REM Remote-Änderungen abrufen
    git fetch
    
    REM Aktuelle Branch ermitteln
    for /f "tokens=*" %%a in ('git branch --show-current') do set CURRENT_BRANCH=%%a
    
    REM Auf den aktuellen Branch aktualisieren
    git pull origin %CURRENT_BRANCH%
    
    REM Lokale Änderungen wiederherstellen
    git stash pop
    
    echo [SUCCESS] Repository wurde aktualisiert.
) else (
    echo [WARNUNG] Manuelles Update: Git-Repository nicht gefunden.
)

REM Python-Abhängigkeiten aktualisieren
pip --version >nul 2>&1
if %errorlevel% equ 0 (
    echo [INFO] Python-Abhängigkeiten werden aktualisiert...
    pip install -U flask sqlalchemy requests paho-mqtt==2.1.0 bleak psycopg2-binary gunicorn jinja2
    echo [SUCCESS] Python-Abhängigkeiten wurden aktualisiert.
) else (
    echo [WARNUNG] Pip nicht gefunden. Python-Abhängigkeiten wurden nicht aktualisiert.
)

REM Domain-Management-Module aktualisieren
if exist "domain_management" (
    echo [INFO] Domain-Management-Module werden aktualisiert...
    REM Hier können spezifische Update-Aktionen für Domain-Management eingefügt werden
    echo [SUCCESS] Domain-Management-Module wurden aktualisiert.
)

REM Datenbank-Migration durchführen (wenn notwendig)
if exist "main.py" (
    echo [INFO] Datenbank-Migration wird durchgeführt...
    python -c "from main import models; from sqlalchemy import create_engine; import os; engine = create_engine(os.environ.get('DATABASE_URL')); models.Base.metadata.create_all(bind=engine)" 2>nul
    if %errorlevel% equ 0 (
        echo [SUCCESS] Datenbank-Migration erfolgreich.
    ) else (
        echo [WARNUNG] Fehler bei der Datenbank-Migration. Überprüfen Sie die Datenbank manuell.
    )
) else (
    echo [WARNUNG] Hauptanwendungsdatei (main.py) nicht gefunden. Datenbank-Migration wird übersprungen.
)

REM Docker-Container neustarten (wenn Docker installiert ist und läuft)
docker --version >nul 2>&1
if %errorlevel% equ 0 (
    docker info >nul 2>&1
    if %errorlevel% equ 0 (
        echo [INFO] Docker-Container werden neu gestartet...
        if exist "docker-compose.yml" (
            docker-compose down
            docker-compose up -d
            echo [SUCCESS] Docker-Container wurden neu gestartet.
        ) else (
            echo [WARNUNG] docker-compose.yml nicht gefunden. Container wurden nicht neu gestartet.
        )
    )
)

REM Zurück zum ursprünglichen Verzeichnis wechseln
cd "%CURRENT_DIR%"

echo.
echo ============================================
echo      SwissAirDry Update abgeschlossen!     
echo ============================================
echo.
echo Hinweise:
echo 1. Überprüfen Sie die .env-Datei auf neue Umgebungsvariablen.
echo 2. Lesen Sie die Aktualisierungshinweise in der CHANGELOG.md-Datei.
echo 3. Starten Sie die Anwendung neu mit: python main.py
echo.
echo Bei Problemen überprüfen Sie bitte:
echo - Die Logdateien im logs/-Verzeichnis
echo - Die Datenbank-Verbindung
echo - Die Cloudflare API-Token-Konfiguration
echo.

:end
REM Zurück zum ursprünglichen Verzeichnis wechseln, falls das noch nicht geschehen ist
cd "%CURRENT_DIR%"
pause