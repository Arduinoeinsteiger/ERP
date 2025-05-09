# Domain Management System

Ein wiederverwendbares Domainverwaltungssystem für Python-Webanwendungen auf Basis von Flask und SQLAlchemy.

## Features

- Verwaltung von Domains und DNS-Einträgen in einer zentralen Oberfläche
- Unterstützung für verschiedene DNS-Provider (derzeit Cloudflare, erweiterbar)
- Automatische Konfiguration von Dienst-Domains für verschiedene Services
- Dunkles Design für moderne Benutzeroberflächen
- REST-API für programmgesteuerte Verwaltung
- Einfache Integration in bestehende Flask-Anwendungen

## Installation

1. Kopieren Sie das `domain_management`-Verzeichnis in Ihr Projekt
2. Installieren Sie die benötigten Abhängigkeiten:

```bash
pip install flask sqlalchemy requests
```

## Integration in bestehende Flask-Anwendungen

Fügen Sie in Ihrer Hauptanwendungsdatei folgende Zeilen hinzu:

```python
from flask import Flask
from sqlalchemy import create_engine
from domain_management import init_app

app = Flask(__name__)

# Konfigurieren Sie Ihre Datenbank
engine = create_engine("sqlite:///app.db")  # Oder Ihre bestehende Engine

# Initialisieren Sie das Domainverwaltungssystem
init_app(app, engine)

if __name__ == '__main__':
    app.run(debug=True)
```

## Verwendung eigener SQL-Modelle

Wenn Sie die Modelle in Ihre eigene Datenbankstruktur integrieren möchten, können Sie die Basisklassen verwenden:

```python
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

# Ihre eigene Base-Klasse
Base = declarative_base()

# Importieren Sie die Domain-Management-Modelle
from domain_management.models import (
    DomainZone as BaseDomainZone,
    DNSRecord as BaseDNSRecord,
    DomainServiceMapping as BaseDomainServiceMapping,
    DNSProviderSettings as BaseDNSProviderSettings
)

# Erstellen Sie Ihre angepassten Modelle
class DomainZone(BaseDomainZone):
    __tablename__ = "domain_zones"
    # Fügen Sie eigene Felder hinzu...
    organization_id = Column(Integer, ForeignKey("organizations.id"))
    organization = relationship("Organization", back_populates="domains")

# Initialisieren Sie die Datenbank
from domain_management import init_db
init_db(engine)
```

## API-Endpunkte

Das System stellt folgende API-Endpunkte bereit:

- `GET /domains/api/status` - Status der Domainverwaltung
- `GET /domains/api/services` - Verfügbare Dienste
- `POST /domains/api/setup` - Konfiguration von Domains

## Eigene DNS-Provider hinzufügen

Um eigene DNS-Provider hinzuzufügen, erstellen Sie eine neue Klasse, die von `DNSApiProvider` erbt:

```python
from domain_management.api_manager import DNSApiProvider, DNSRecord, DomainInfo

class MyDNSProvider(DNSApiProvider):
    def __init__(self, api_key):
        self.api_key = api_key
        
    def verify_token(self):
        # Implementieren Sie die Token-Verifizierung
        ...
        
    def get_zones(self):
        # Implementieren Sie das Abrufen von Domains
        ...
        
    # Implementieren Sie alle anderen abstractmethods
```

Registrieren Sie dann Ihren Provider:

```python
from domain_management.api_manager import get_dns_provider

# Patchen Sie die Factory-Funktion
original_get_dns_provider = get_dns_provider

def custom_get_dns_provider(provider_type='cloudflare', api_token=None):
    if provider_type == 'my_provider':
        return MyDNSProvider(api_token)
    return original_get_dns_provider(provider_type, api_token)

# Überschreiben Sie die Factory-Funktion
domain_management.api_manager.get_dns_provider = custom_get_dns_provider
```

## Konfiguration der Templates

Die Templates verwenden das Bootstrap-Framework und Font Awesome Icons. Stellen Sie sicher, dass diese in Ihrer Anwendung eingebunden sind.

Standardmäßig werden die Templates aus dem Verzeichnis `templates/domain_management/` geladen. Sie können diese Templates anpassen oder durch eigene ersetzen.

## Anpassen des Dunklen Designs

Das dunkle Design verwendet CSS-Variablen, die Sie in Ihrem Haupt-CSS-File überschreiben können:

```css
:root {
    /* Anpassen der Hauptfarben */
    --primary: #your-primary-color;
    --bg-primary: #your-bg-color;
    --text-primary: #your-text-color;
    /* ... */
}
```

## Sicherheitshinweise

- Das System speichert API-Tokens und Schlüssel im Klartext in der Datenbank. Für Produktionsumgebungen sollten Sie eine sichere Speichermethode implementieren.
- Verwenden Sie HTTPS für die Kommunikation mit dem DNS-Provider und für die Web-Oberfläche.
- Schützen Sie die API-Endpunkte mit geeigneter Authentifizierung.

## Lizenz

MIT License