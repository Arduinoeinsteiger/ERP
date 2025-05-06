# SwissAirDry Tests

Diese Dokumentation beschreibt die Teststruktur und Vorgehensweise für das SwissAirDry-Projekt.

## Übersicht

SwissAirDry verwendet Unit-Tests, um die Funktionalität der Komponenten sicherzustellen. Die Tests verwenden das Standard-Python-Unittest-Framework und Mocking, um externe Abhängigkeiten zu isolieren.

## Teststruktur

Die Tests sind wie folgt organisiert:

```
swissairdry_new/
└── api/
    └── tests/
        ├── __init__.py
        ├── test_qrcode_generator.py
        └── ...
```

Jede Komponente hat ihre eigene Testdatei, die alle relevanten Tests für diese Komponente enthält.

## Ausführen der Tests

Führen Sie die Tests mit dem folgenden Befehl aus:

```bash
# Alle Tests ausführen
python -m unittest discover -s swissairdry_new

# Einen spezifischen Test ausführen
python -m unittest swissairdry_new.api.tests.test_qrcode_generator
```

## QR-Code-Generator-Tests

Die QR-Code-Generator-Tests (`test_qrcode_generator.py`) enthalten Tests für die QR-Code-Generierung Funktionalität:

1. **Basic QR-Code Creation**: Prüft, ob ein einfacher QR-Code mit Standardeinstellungen korrekt erstellt wird
2. **QR-Code mit Titel**: Prüft, ob ein QR-Code mit Titel korrekt erstellt wird
3. **Fehlerbehandlung**: Prüft, ob Fehler korrekt behandelt werden
4. **Größenvalidierung**: Prüft, ob die Validierung der QR-Code-Größe korrekt funktioniert

Beispiel für einen Test:

```python
def test_qrcode_creation_basic(self):
    """
    Testet die grundlegende Erstellung eines QR-Codes
    """
    from swissairdry_new.api.minimal_http_server import SwissAirDryRequestHandler
    
    # Mock für HTTP-Handler
    handler = MagicMock()
    handler._send_image_response = MagicMock()
    
    # Query-Parameter
    query_params = {
        'content': ['TestContent'],
        'size': ['200'],
        'title': ['Test Title']
    }
    
    # QR-Code generieren
    SwissAirDryRequestHandler._handle_qrcode_api(handler, query_params)
    
    # Überprüfen, ob die Mock-Methoden aufgerufen wurden
    self.mock_qrcode.assert_called_once()
    self.mock_qr_instance.add_data.assert_called_once_with('TestContent')
    self.mock_qr_instance.make.assert_called_once_with(fit=True)
    self.mock_qr_instance.make_image.assert_called_once()
    
    # Überprüfen, ob die Antwort gesendet wurde
    handler._send_image_response.assert_called_once()
```

## Mocking

Die Tests verwenden Mocking, um externe Abhängigkeiten zu isolieren und die Tests schnell und zuverlässig zu machen. Beispielsweise werden in den QR-Code-Generator-Tests die Abhängigkeiten `qrcode` und `PIL` gemockt.

Beispiel für Mocking-Setup:

```python
def setUp(self):
    """
    Test-Setup
    """
    # Mock-Abhängigkeiten
    self.qrcode_patcher = patch('qrcode.QRCode')
    self.image_patcher = patch('PIL.Image.new')
    self.draw_patcher = patch('PIL.ImageDraw.Draw')
    self.font_patcher = patch('PIL.ImageFont.truetype')
    
    # Mock-Objekte
    self.mock_qrcode = self.qrcode_patcher.start()
    self.mock_image = self.image_patcher.start()
    self.mock_draw = self.draw_patcher.start()
    self.mock_font = self.font_patcher.start()
    
    # Setup der Mock-Objekte
    self.mock_qr_instance = MagicMock()
    self.mock_qrcode.return_value = self.mock_qr_instance
    self.mock_qr_image = MagicMock()
    self.mock_qr_instance.make_image.return_value = self.mock_qr_image
```

## Testabdeckung

Die Tests stellen sicher, dass:

1. Die Hauptfunktionalität korrekt funktioniert
2. Grenzfälle behandelt werden
3. Fehlerbehandlung korrekt implementiert ist
4. Die API-Schnittstellen wie erwartet funktionieren

Es wird empfohlen, die Testabdeckung zu messen und Bereiche mit geringer Abdeckung zu identifizieren, um zusätzliche Tests hinzuzufügen.

## Best Practices

Beim Schreiben von Tests für SwissAirDry sollten Sie diese Richtlinien beachten:

1. **Isolierung**: Jeder Test sollte unabhängig von anderen Tests sein
2. **Mocking**: Externe Abhängigkeiten sollten gemockt werden
3. **Klar und präzise**: Jeder Test sollte einen klaren Zweck haben und gut dokumentiert sein
4. **Schnell ausführbar**: Tests sollten schnell ausgeführt werden können
5. **Reproduzierbar**: Tests sollten immer das gleiche Ergebnis liefern

## Hinzufügen neuer Tests

Um neue Tests hinzuzufügen:

1. Erstellen Sie eine neue Testdatei in `swissairdry_new/api/tests/` für neue Komponenten
2. Importieren Sie die zu testende Komponente
3. Erstellen Sie eine Testklasse, die von `unittest.TestCase` erbt
4. Implementieren Sie Testmethoden, die mit `test_` beginnen

Beispiel:

```python
import unittest
from unittest.mock import patch, MagicMock

class NewComponentTests(unittest.TestCase):
    def setUp(self):
        # Test setup
        pass
        
    def tearDown(self):
        # Test cleanup
        pass
        
    def test_some_functionality(self):
        # Test implementation
        pass
```

## Integrieren in CI/CD

Die Tests sollten in den CI/CD-Prozess integriert werden, um sicherzustellen, dass neue Änderungen keine bestehende Funktionalität beeinträchtigen:

```yaml
# Beispiel für einen GitHub Actions Workflow
name: Tests

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
    - name: Run tests
      run: |
        python -m unittest discover
```