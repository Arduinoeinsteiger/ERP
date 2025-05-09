# SwissAirDry v1.0.0 - Domainverwaltung

Diese Installationsdateien sind Teil des SwissAirDry v1.0.0 Releases, das die Domainverwaltung mit Cloudflare-Integration implementiert.

## Features

- Domain-Management mit Cloudflare API-Integration
- Umfassende DNS-Eintrags-Verwaltung
- Service-Mapping für verschiedene Anwendungskomponenten
- Dunkles Design für moderne Benutzeroberfläche
- Automatisches Setup für mehrere Dienste

## Installation

### Für Linux/Mac

Führen Sie das folgende Kommando im Terminal aus:

```bash
chmod +x install.sh
./install.sh
```

### Für Windows

Doppelklicken Sie auf `install.bat` oder führen Sie es in der Kommandozeile aus:

```
install.bat
```

## Nach der Installation

1. Konfigurieren Sie Ihren Cloudflare API-Token in der `.env`-Datei:
   ```
   CLOUDFLARE_API_TOKEN=Ihr_Cloudflare_API_Token_hier
   ```

2. Starten Sie die Anwendung:
   ```
   python main.py
   ```

3. Greifen Sie auf die Domainverwaltung zu unter:
   ```
   http://localhost:5000/domains
   ```

## Manuelles Setup

Falls die automatische Installation fehlschlägt, können Sie die folgenden Schritte manuell durchführen:

1. Installieren Sie die benötigten Python-Pakete:
   ```
   pip install flask sqlalchemy requests paho-mqtt==2.1.0 bleak psycopg2-binary gunicorn jinja2
   ```

2. Stellen Sie sicher, dass die Domain-Management-Module korrekt installiert sind.

3. Fügen Sie den Cloudflare API-Token zur `.env`-Datei hinzu:
   ```
   CLOUDFLARE_API_TOKEN=Ihr_Cloudflare_API_Token_hier
   ```

4. Initialisieren Sie die Datenbank:
   ```python
   from main import models
   from sqlalchemy import create_engine
   import os
   
   engine = create_engine(os.environ.get('DATABASE_URL'))
   models.Base.metadata.create_all(bind=engine)
   ```

## Release-Informationen

- **Version**: v1.0.0
- **Commit-Hash**: f307b0c
- **Release-Tag**: ins

## Support

Bei Problemen oder Fragen besuchen Sie bitte:
- Die Dokumentation im Code
- Das GitHub-Repository: [https://github.com/Arduinoeinsteiger/ERP](https://github.com/Arduinoeinsteiger/ERP)