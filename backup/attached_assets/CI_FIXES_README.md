# CI/CD Pipeline-Fixes für SwissAirDry

## Durchgeführte Änderungen

### 1. GitHub Actions Version-Fixes

In allen CI-Workflow-Dateien (`.github/workflows/*.yml`) wurden die folgenden Änderungen vorgenommen:

- `actions/upload-artifact` von v3.1.3 auf v3.0.0 geändert, um Probleme mit "Missing download info for article(sha)@v1.3" zu beheben
- Konsistente Verwendung von `actions/checkout@v3` in allen Workflows
- Konsistente Verwendung von `actions/cache@v3` in allen Workflows

Diese Änderungen wurden in folgenden Dateien durchgeführt:
- `.github/workflows/ci.yml`
- `.github/workflows/ci_v2.yml`
- `.github/workflows/ci_fix.yml`
- `.github/workflows/ci_build_fix.yml`

### 2. Python Testabhängigkeiten

Um das Problem mit der fehlenden HTTP-Client-Bibliothek zu beheben, die für den Starlette Testclient erforderlich ist, wurden diese Änderungen vorgenommen:

- `httpx>=0.22.0` zur `requirements-dev.txt` hinzugefügt
- `httpx>=0.22.0` zu den Abhängigkeiten in `setup.py` hinzugefügt

### 3. Setuptools Version-Fix

Wir haben die Setuptools-Version auf eine feste Version gesetzt:
- `setuptools==59.8.0` in allen Workflow-Dateien verwendet
- Shell-Befehl entsprechend angepasst, um Versionsprobleme zu vermeiden

## Weitere Maßnahmen

Die Tests schlagen jetzt fehl mit Exit-Code 1, was darauf hindeutet, dass die Tests selbst Probleme haben, aber die Pipeline kann nun ohne die GitHub Actions-bezogenen Fehler ausgeführt werden.

## Empfehlungen für zukünftige Updates

1. Verwenden Sie stets stabile Versionen der GitHub Actions:
   - `actions/checkout@v3` statt der neueren v4-Version
   - `actions/upload-artifact@v3.0.0` statt v3.1.3 oder v4
   - `actions/cache@v3` statt der neueren v4-Version

2. Stellen Sie sicher, dass alle Test-Abhängigkeiten sowohl in `requirements-dev.txt` als auch in `setup.py` vorhanden sind.

3. Nach jedem größeren Dependency-Update sollten Sie die CI-Pipeline testen, um sicherzustellen, dass keine neuen Konflikte aufgetreten sind.

## Dokumentation

Diese Änderungen ergänzen die bereits dokumentierten Fixes in:
- `fix_ci_workflow_report.md`
- `fix_ci_build_report.md`
- `swissairdry/api/docs/MQTT_CLIENT_ID_FIX.md`