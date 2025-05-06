# QR-Code-Generator Dokumentation

## Übersicht

Der QR-Code-Generator ist eine Komponente des SwissAirDry API-Servers, die es ermöglicht, 
QR-Codes für verschiedene Zwecke zu generieren, darunter Gerätekonfiguration, WLAN-Setup 
und benutzerdefinierte Inhalte.

![QR-Code-Generator](../images/qrcode_generator.svg)

## Funktionen

Der QR-Code-Generator bietet folgende Hauptfunktionen:

1. **Benutzerdefinierte QR-Codes**
   - Generierung von QR-Codes mit beliebigem Inhalt
   - Anpassbare Größe (50-1000px)
   - Optionaler Titel unter dem QR-Code

2. **WLAN-Konfiguration**
   - Erstellt QR-Codes im standardisierten WIFI-Format
   - Unterstützt verschiedene Verschlüsselungstypen (WPA/WPA2/WPA3, WEP, offen)
   - Option für versteckte Netzwerke

3. **Gerät-Setup**
   - Generiert QR-Codes mit Gerätekonfigurationsdaten im JSON-Format
   - Enthält Geräte-ID, MQTT-Server-Informationen und Zeitstempel

## Endpunkte

### Web-Interface

```
GET /qrcode
```

Das Web-Interface bietet eine benutzerfreundliche Oberfläche zur Generierung von QR-Codes mit verschiedenen Optionen.

### API-Endpunkt

```
GET /api/qrcode?content=TEXT&size=SIZE&title=TITLE
```

Parameter:
- `content` (erforderlich): Der zu codierende Inhalt (Text, URL, JSON, etc.)
- `size` (optional): Größe des QR-Codes in Pixeln (Standard: 200, Bereich: 50-1000)
- `title` (optional): Titel, der unter dem QR-Code angezeigt wird (Standard: "SwissAirDry QR-Code")

### Beispiele

#### Einfacher QR-Code

```
GET /api/qrcode?content=SwissAirDry
```

#### QR-Code mit angepasster Größe und Titel

```
GET /api/qrcode?content=SwissAirDry&size=300&title=Mein%20QR-Code
```

#### WLAN-Konfiguration

```
GET /api/qrcode?content=WIFI:S:MeinNetzwerk;P:MeinPasswort;T:WPA;;
```

#### Gerätekonfiguration

```
GET /api/qrcode?content={"device_id":"12345","mqtt":{"server":"mqtt.beispiel.com","port":1883}}
```

## Implementierungsdetails

Der QR-Code-Generator verwendet die Python-Bibliotheken `qrcode` und `PIL` (Pillow) für die Generierung und Bildverarbeitung. Er unterstützt folgende Features:

- Fehlerkorrektur-Level H (höchste Stufe)
- PNG-Bildformat mit transparentem Hintergrund
- Automatische Größenanpassung je nach Inhaltsmenge
- Text-Annotation unter dem QR-Code (wenn ein Titel angegeben ist)

## Sicherheitshinweise

Bei der Generierung von QR-Codes mit sensiblen Informationen (z.B. WLAN-Passwörter) sollten Sie bedenken, dass:

1. Die generierten QR-Codes nicht verschlüsselt sind
2. Der Inhalt für jeden lesbar ist, der den QR-Code scannen kann
3. Der Server keine generierten QR-Codes speichert, aber der Inhalt könnte in Server-Logs erscheinen

Für höhere Sicherheit empfehlen wir:

- Vermeiden Sie die Übertragung sensibler Informationen in QR-Codes
- Beschränken Sie die Gültigkeit von QR-Codes mit Konfigurationsdaten zeitlich
- Fügen Sie einen Einmal-Token hinzu, wenn der QR-Code für die Authentifizierung verwendet wird

## Fehlerbehebung

### Häufige Probleme

1. **"QR-Code-Funktionalität nicht verfügbar"**
   - Stellen Sie sicher, dass die `qrcode`-Bibliothek installiert ist
   - Installieren Sie mit `pip install qrcode[pil]`

2. **"Parameter 'content' ist erforderlich"**
   - Der Parameter `content` fehlt in der Anfrage
   - Fügen Sie `?content=IhrInhalt` zur URL hinzu

3. **"Größe muss zwischen 50 und 1000 liegen"**
   - Der angegebene Größenwert liegt außerhalb des gültigen Bereichs
   - Verwenden Sie einen Wert zwischen 50 und 1000

## Beispiel-Code

### Python-Client

```python
import requests
from PIL import Image
from io import BytesIO

def generate_qrcode(content, size=200, title="SwissAirDry QR-Code"):
    """
    Generiert einen QR-Code über die SwissAirDry API.
    
    Args:
        content: Der zu codierende Inhalt
        size: QR-Code-Größe in Pixeln
        title: Optionaler Titel
    
    Returns:
        PIL Image-Objekt mit dem QR-Code
    """
    url = f"http://localhost:5000/api/qrcode"
    params = {
        "content": content,
        "size": size,
        "title": title
    }
    
    response = requests.get(url, params=params)
    
    if response.status_code == 200:
        return Image.open(BytesIO(response.content))
    else:
        raise Exception(f"Fehler beim Generieren des QR-Codes: {response.text}")

# Beispiel: QR-Code generieren und speichern
qr_img = generate_qrcode("https://swissairdry.com", 300, "Besuchen Sie uns!")
qr_img.save("swissairdry_qrcode.png")
```

### JavaScript-Client

```javascript
/**
 * Generiert einen QR-Code über die SwissAirDry API.
 * 
 * @param {string} content - Der zu codierende Inhalt
 * @param {number} size - QR-Code-Größe in Pixeln (optional)
 * @param {string} title - Optionaler Titel (optional)
 * @returns {Promise<Blob>} - Blob mit dem QR-Code-Bild
 */
async function generateQRCode(content, size = 200, title = "SwissAirDry QR-Code") {
    const url = new URL("http://localhost:5000/api/qrcode");
    url.searchParams.append("content", content);
    url.searchParams.append("size", size);
    url.searchParams.append("title", title);
    
    const response = await fetch(url);
    
    if (response.ok) {
        return await response.blob();
    } else {
        const errorText = await response.text();
        throw new Error(`Fehler beim Generieren des QR-Codes: ${errorText}`);
    }
}

// Beispiel: QR-Code generieren und anzeigen
generateQRCode("https://swissairdry.com", 300, "Besuchen Sie uns!")
    .then(blob => {
        const img = document.createElement("img");
        img.src = URL.createObjectURL(blob);
        document.body.appendChild(img);
    })
    .catch(error => console.error(error));
```