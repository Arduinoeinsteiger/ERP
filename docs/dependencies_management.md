# Abhängigkeitsmanagement für SwissAirDry

Diese Dokumentation beschreibt die korrekte Verwaltung von Abhängigkeiten im SwissAirDry-Projekt, mit besonderem Fokus auf Python-Pakete und Docker-Integration.

## 1. Überblick der Requirements-Dateien

Das Projekt verwendet mehrere `requirements.txt`-Dateien:

1. **Hauptanwendung**: `/backup/attached_assets/requirements.txt`
   - Wird von der Hauptanwendung und MQTT-Bridge verwendet
   - Wird in `Dockerfile` und `Dockerfile.bridge` referenziert

2. **Nextcloud ExApp**: `/nextcloud/apps/swissairdry/daemon/requirements.txt`
   - Wird vom Nextcloud-ExApp-Daemon verwendet

## 2. Kritische Abhängigkeiten und Versionseinschränkungen

| Paket | Version | Hinweise |
|-------|---------|----------|
| paho-mqtt | 2.1.0 | Muss exakt diese Version sein (`==2.1.0`). Höhere Versionen wie 2.2.1 existieren nicht auf PyPI und führen zu Build-Fehlern |
| Flask | >=2.3.3 | Kompatibilität mit anderen Komponenten |
| psycopg2-binary | >=2.9.9 | PostgreSQL-Verbindung |
| bleak | >=0.21.1 | BLE-Funktionalität |

## 3. Aktualisierung der Abhängigkeiten

### 3.1 Vorsichtsmaßnahmen vor Updates

Bevor Abhängigkeiten aktualisiert werden:

1. **Backups erstellen**:
   ```bash
   cp backup/attached_assets/requirements.txt backup/attached_assets/requirements.txt.bak
   cp nextcloud/apps/swissairdry/daemon/requirements.txt nextcloud/apps/swissairdry/daemon/requirements.txt.bak
   ```

2. **Bestehende Versionen prüfen**:
   ```bash
   docker compose exec api pip freeze | grep 'package-name'
   ```

### 3.2 Prozess zur Aktualisierung

Um Abhängigkeiten zu aktualisieren:

1. **Alle relevanten `requirements.txt` konsistent aktualisieren**:
   - Bearbeiten Sie beide Dateien mit denselben Änderungen

2. **Docker-Images neu bauen**:
   ```bash
   docker compose build --no-cache
   docker compose up -d
   ```

3. **Überprüfen Sie Logs auf Fehler**:
   ```bash
   docker compose logs -f
   ```

### 3.3 Spezielle Hinweise zu paho-mqtt

Das Paket `paho-mqtt` erfordert besondere Vorsicht:

- Verwenden Sie **immer** `paho-mqtt==2.1.0` (exakt diese Version)
- Versionen wie `>=2.2.1` führen zu Build-Fehlern
- Wenn neue kompatible Versionen erscheinen, testen Sie diese gründlich in einer separaten Umgebung, bevor Sie die Produktion aktualisieren

## 4. Docker-Integration

Die Docker-Container verwenden die `requirements.txt`-Dateien wie folgt:

### 4.1 Hauptanwendung (api)

In `Dockerfile`:
```dockerfile
# Install Python dependencies
COPY backup/attached_assets/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt
```

### 4.2 MQTT-Bridge

In `Dockerfile.bridge`:
```dockerfile
# Install Python dependencies
COPY backup/attached_assets/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt
```

### 4.3 ExApp-Daemon

In `nextcloud/apps/swissairdry/daemon/Dockerfile`:
```dockerfile
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
```

## 5. Fehlerbehebung

### 5.1 Häufige Fehler

| Fehler | Ursache | Lösung |
|--------|---------|--------|
| `Could not find a version that satisfies the requirement paho-mqtt>=2.2.1` | Nicht existierende Version wird angefordert | Ändern zu `paho-mqtt==2.1.0` |
| `ImportError: No module named 'package'` | Paket fehlt in einer der requirements.txt | Paket zur relevanten requirements.txt hinzufügen |

### 5.2 Überprüfung der installierten Pakete

```bash
# In der Hauptanwendung
docker compose exec api pip freeze

# In der MQTT-Bridge
docker compose exec mqtt-bridge pip freeze

# Im ExApp-Daemon
docker compose exec exapp-daemon pip freeze
```

## 6. Wartung der Requirements

### 6.1 Regelmäßige Prüfung

Überprüfen Sie regelmäßig alle dependencies auf:

1. Sicherheitsupdates
2. Kompatibilität untereinander
3. Konsistenz zwischen den verschiedenen requirements.txt-Dateien

### 6.2 Aktualisierungsstrategie

1. Aktualisieren Sie kritische Sicherheitsupdates sofort
2. Führen Sie Feature-Updates in einer Testumgebung durch
3. Dokumentieren Sie alle Änderungen im Git-Log

## 7. Anhang: Vollständige Liste der Abhängigkeiten

### 7.1 Hauptanwendung und MQTT-Bridge

```
Flask>=2.3.3
flask-cors>=4.0.0
requests>=2.31.0
paho-mqtt==2.1.0
python-dotenv>=1.0.0
gunicorn>=22.0.0
psycopg2-binary>=2.9.9
jinja2>=3.1.3
email-validator>=2.0.0
flask-sqlalchemy>=3.0.5
bleak>=0.21.1
aiohttp>=3.8.1
websockets>=10.3
```

### 7.2 ExApp-Daemon

```
aiohttp>=3.8.1
paho-mqtt==2.1.0
requests>=2.31.0
websockets>=10.3
python-dotenv>=1.0.0
```

## 8. Aktualisierungshistorie

| Datum | Version | Änderungen | Autor |
|-------|---------|------------|-------|
| 09.05.2025 | 1.0.0 | Initiale Dokumentation, paho-mqtt auf 2.1.0 festgelegt | System |

---

Diese Dokumentation soll als Leitfaden für die konsistente Verwaltung der Projektabhängigkeiten dienen und häufige Fehler vermeiden.