# CI Build Fix Report

## Identifiziertes Problem:
In den GitHub Actions CI/CD Workflows trat ein Fehler auf, der mit der setuptools-Version zusammenhängt. Die Angabe `<60.0.0` wurde von der Shell als Umleitungsoperator interpretiert:

```
/home/runner/work/_temp/1a24dbe9-65c5-4c19-ac97-86a4944097e1.sh: line 2: 60.0.0: No such file or directory
```

## Durchgeführte Anpassungen:

1. **setup.py**: 
   - Die Version wurde von `setuptools>=42,<60.0.0` auf `setuptools==59.8.0` geändert
   - Doppelte Einträge und Syntaxfehler wurden entfernt
   - Die komplette Datei wurde strukturell vereinfacht

2. **pyproject.toml**:
   - Änderung der setuptools-Version von `requires = ["setuptools>=42,<60.0.0", "wheel>=0.37.0", "build>=0.7.0"]` auf `requires = ["setuptools==59.8.0", "wheel>=0.37.0", "build>=0.7.0"]`
   - Entfernung des Versionsbereichs zugunsten einer festen Version

3. **CI/CD-Workflows**:
   - In `.github/workflows/ci.yml` wurde `setuptools==59.8.0` mit Anführungszeichen versehen, um Shell-Interpretation zu verhindern
   - In `.github/workflows/ci_fix.yml` wurden beide setuptools-Einträge korrigiert
   - In `.github/workflows/ci_build_fix.yml` wurde die setuptools-Version entsprechend angepasst

4. **GitHub Actions Fix Skripte**:
   - In `.github/workflows/ensure_minimal_package.py` wurde die setuptools-Version korrigiert
   - In `.github/workflows/fix_package_structure.py` wurde die setuptools-Version korrigiert

## Weitere identifizierte Probleme:

1. **MQTT-Client-ID-Konflikte**:
   Die API-Server zeigen Warnungen bezüglich MQTT-Client-ID-Konflikten. Dies ist ein erwartetes Verhalten, da mehrere Clients mit ähnlichen IDs versuchen, sich zu verbinden. Die Server behandeln dieses Problem bereits durch Wiederverbindung mit neuen IDs.

2. **FastAPI on_event Deprecation-Warnung**:
   Es gibt eine Deprecation-Warnung in der FastAPI-App, die auf die Verwendung von `@app.on_event()` hinweist. Dies sollte in Zukunft durch den neuen Lifespan-Event-Mechanismus ersetzt werden.

## Erfolgreicher Status:

- SwissAirDry API-Server läuft auf Port 5000
- SwissAirDry Simple API-Server läuft auf Port 5001
- MQTT-Broker läuft auf Port 1883 (MQTT) und 9001 (WebSocket)
- Die Server kommunizieren erfolgreich miteinander

Die Änderungen sollten das CI-Build-Problem beheben, indem Shell-Interpretationsfehler durch die Verwendung einer exakten Version anstelle eines Versionsbereichs vermieden werden.