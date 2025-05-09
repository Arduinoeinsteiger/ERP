# SwissAirDry - Installationsanleitung

Diese Installationsscripts installieren die Domainverwaltung und alle benötigten Abhängigkeiten für das SwissAirDry-Projekt.

## Für Linux/Mac

Führen Sie das folgende Kommando im Terminal aus:

```bash
chmod +x install.sh
./install.sh
```

## Für Windows

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

2. Kopieren Sie das `domain_management`-Verzeichnis in das Stammverzeichnis Ihrer Anwendung.

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

## Support

Bei Problemen oder Fragen besuchen Sie bitte:
- Die Dokumentation in `domain_management/README.md`
- Das GitHub-Repository: [https://github.com/Arduinoeinsteiger/ERP](https://github.com/Arduinoeinsteiger/ERP)