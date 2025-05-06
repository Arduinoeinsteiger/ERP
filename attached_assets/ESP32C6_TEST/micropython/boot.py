"""
SwissAirDry MicroPython Boot-Datei für ESP32-S6
-----------------------------------------------

Diese Datei wird beim Booten des ESP32 automatisch ausgeführt
und konfiguriert grundlegende Einstellungen.
"""

import gc
import webrepl
from machine import freq

# Erhöhen der CPU-Frequenz für bessere Leistung
# ESP32-S6 kann mit 240 MHz betrieben werden
freq(240000000)

# Speicher freigeben
gc.collect()

# WebREPL für Remote-Zugriff aktivieren
# (nur bei Entwicklung/Debugging - kann später deaktiviert werden)
try:
    webrepl.start(password='swissairdry')
    print("WebREPL gestartet")
except:
    print("WebREPL konnte nicht gestartet werden")

# GC-Schwellwert anpassen für bessere Leistung
gc.threshold(4096)

print("Boot-Sequenz abgeschlossen")