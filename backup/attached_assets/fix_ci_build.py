#!/usr/bin/env python3
"""
Dieses Skript behebt die Probleme mit den CI-Builds, indem es eine verbesserte Version 
der Paketstruktur erstellt und fehlerhafte Dateien korrigiert.
"""

import os
import sys
import shutil
from pathlib import Path


def ensure_directories(base_dir):
    """Stellt sicher, dass alle wichtigen Verzeichnisse existieren."""
    critical_dirs = [
        'swissairdry',
        'swissairdry/api',
        'swissairdry/api/app',
        'swissairdry/api/app/routes',
        'swissairdry/api/app/routers',
        'swissairdry/db',
        'swissairdry/mqtt',
        'swissairdry/nextcloud',
        'swissairdry/integration',
        'swissairdry/integration/deck',
        'swissairdry/ExApp',
        'swissairdry/esp',
        'swissairdry/mobile',
        'swissairdry/docs'
    ]
    
    for d in critical_dirs:
        full_path = os.path.join(base_dir, d)
        if not os.path.exists(full_path):
            os.makedirs(full_path, exist_ok=True)
            print(f"Verzeichnis erstellt: {full_path}")


def create_init_files(base_dir):
    """Erstellt __init__.py Dateien in allen Python-Package-Verzeichnissen."""
    created_files = []

    # Iteriere durch alle Unterverzeichnisse
    for root, dirs, files in os.walk(os.path.join(base_dir, 'swissairdry')):
        # Überspringe versteckte Verzeichnisse und spezielle Verzeichnisse
        dirs[:] = [d for d in dirs if not d.startswith('.') and d not in ['__pycache__', 'tests', 'build', 'dist']]
        
        # Erstelle in jedem Verzeichnis eine __init__.py Datei
        init_file = os.path.join(root, '__init__.py')
        
        # Wenn noch keine __init__.py existiert, erstelle eine
        if not os.path.exists(init_file):
            package_name = os.path.basename(root)
            with open(init_file, 'w') as f:
                f.write(f'"""\n{package_name} Package\n\nDieses Modul ist Teil des SwissAirDry-Projekts.\n"""\n\n')
            created_files.append(init_file)
            print(f"Erstellt: {init_file}")
    
    return created_files


def fix_paho_mqtt_compatibility():
    """Behebt Kompatibilitätsprobleme mit paho-mqtt."""
    mqtt_client_path = os.path.join('swissairdry', 'api', 'mqtt_client.py')
    
    if not os.path.exists(mqtt_client_path):
        print(f"MQTT-Client-Datei nicht gefunden: {mqtt_client_path}")
        return False
    
    with open(mqtt_client_path, 'r') as f:
        content = f.read()
    
    # Füge MQTT-Konstanten-Definition hinzu
    if "MQTT_ERR_SUCCESS = 0" not in content:
        content = content.replace(
            "import paho.mqtt.client as mqtt",
            "import paho.mqtt.client as mqtt\n# Definiere Konstanten für alle paho-mqtt-Versionen\nMQTT_ERR_SUCCESS = 0\nif not hasattr(mqtt, 'MQTT_ERR_SUCCESS'):\n    mqtt.MQTT_ERR_SUCCESS = MQTT_ERR_SUCCESS"
        )
    
    # Verbessere Client-Initialisierung
    if "callback_api_version" in content and "CallbackAPIVersion" in content:
        content = content.replace(
            "if hasattr(mqtt, 'CallbackAPIVersion'):",
            "# Vermeide Fehler mit callback_api_version Parameter\ntry:\n    if hasattr(mqtt, 'CallbackAPIVersion'):"
        )
        content = content.replace(
            "else:\n                    self.client = mqtt.Client(client_id=self.client_id)",
            "else:\n                    self.client = mqtt.Client(client_id=self.client_id)\nexcept (TypeError, AttributeError):\n    self.client = mqtt.Client(client_id=self.client_id)"
        )
    
    with open(mqtt_client_path, 'w') as f:
        f.write(content)
    
    print(f"MQTT-Client-Datei angepasst: {mqtt_client_path}")
    return True


def fix_setup_py():
    """Behebt Probleme in setup.py."""
    setup_py_path = 'setup.py'
    
    if not os.path.exists(setup_py_path):
        print(f"setup.py nicht gefunden: {setup_py_path}")
        # Create minimal setup.py if missing
        with open(setup_py_path, 'w') as f:
            f.write('''from setuptools import setup, find_packages

setup(
    name="swissairdry",
    version="0.1.0",
    packages=find_packages(include=['swissairdry', 'swissairdry.*']),
    install_requires=[
        'fastapi>=0.68.0',
        'uvicorn>=0.15.0',
        'pydantic>=1.8.0',
        'paho-mqtt>=1.6.1',
    ],
    python_requires='>=3.9',
)''')
        return True
    
    with open(setup_py_path, 'r') as f:
        content = f.read()
    
    # Verwende find_packages
    if "from setuptools import find_packages" not in content:
        content = content.replace(
            "from setuptools import setup",
            "from setuptools import setup, find_packages"
        )
    
    if "packages=find_packages(include=['swissairdry', 'swissairdry.*'])" not in content:
        content = content.replace(
            "packages=packages",
            "packages=find_packages(include=['swissairdry', 'swissairdry.*'])"
        )
    
    with open(setup_py_path, 'w') as f:
        f.write(content)
    
    print(f"setup.py angepasst: {setup_py_path}")
    return True


def fix_manifest_in():
    """Erstellt oder korrigiert MANIFEST.in."""
    manifest_path = 'MANIFEST.in'
    
    content = """include README.md
include SECURITY.md
include LICENSE
include pyproject.toml
include setup.py
include .flake8

recursive-include swissairdry/api/app/templates *.html
recursive-include swissairdry/api/app/static *.css *.js *.png *.jpg *.svg
recursive-include swissairdry/mqtt *.conf
recursive-include swissairdry/nextcloud *.xml *.json *.php
recursive-include swissairdry *.md *.txt *.json *.yaml *.yml

prune tests
prune .github
prune build
prune dist
prune *.egg-info
prune */__pycache__
prune */*/__pycache__
prune */*/*/__pycache__
"""
    
    with open(manifest_path, 'w') as f:
        f.write(content)
    
    print(f"MANIFEST.in erstellt/aktualisiert: {manifest_path}")
    return True


def fix_pyproject_toml():
    """Behebt Probleme in pyproject.toml."""
    pyproject_path = 'pyproject.toml'
    
    if not os.path.exists(pyproject_path):
        print(f"pyproject.toml nicht gefunden: {pyproject_path}")
        return False
    
    with open(pyproject_path, 'r') as f:
        content = f.read()
    
    # Aktualisiere Build-Abhängigkeiten
    if "wheel>=0.37.0" not in content:
        content = content.replace(
            'requires = ["setuptools>=42,<60.0.0", "wheel", "setuptools_scm[toml]>=6.0"]',
            'requires = ["setuptools==59.8.0", "wheel>=0.37.0", "build>=0.7.0"]'
        )
    
    # Verwende package-finder
    if 'packages = { find = { include = ["swissairdry", "swissairdry.*"] } }' not in content:
        if "[tool.setuptools]" in content and "packages = [" in content:
            # Finde den Anfang und das Ende des packages-Blocks
            start = content.find("[tool.setuptools]")
            packages_start = content.find("packages = [", start)
            packages_end = content.find("]", packages_start)
            
            # Ersetze den Block
            old_block = content[packages_start:packages_end+1]
            new_block = 'packages = { find = { include = ["swissairdry", "swissairdry.*"] } }'
            content = content.replace(old_block, new_block)
    
    # Füge package-dir hinzu, falls nicht vorhanden
    if 'package-dir = { "" = "." }' not in content:
        if "[tool.setuptools]" in content:
            # Finde das Ende des tool.setuptools-Blocks
            start = content.find("[tool.setuptools]")
            next_section = content.find("[", start + 1)
            
            # Füge package-dir vor dem nächsten Abschnitt ein
            if next_section > 0:
                insert_pos = content.rfind("\n", start, next_section) + 1
                content = content[:insert_pos] + 'package-dir = { "" = "." }\n\n' + content[insert_pos:]
    
    with open(pyproject_path, 'w') as f:
        f.write(content)
    
    print(f"pyproject.toml angepasst: {pyproject_path}")
    return True


def main():
    """Hauptfunktion für die Ausführung des Skripts."""
    # Verwende das aktuelle Verzeichnis als Basis
    base_dir = os.path.abspath('.')
    
    print(f"Basis-Verzeichnis: {base_dir}")
    
    # CI-Build-Probleme beheben
    ensure_directories(base_dir)
    created_files = create_init_files(base_dir)
    print(f"Insgesamt {len(created_files)} __init__.py Dateien erstellt.")
    
    fix_paho_mqtt_compatibility()
    fix_setup_py()
    fix_manifest_in()
    fix_pyproject_toml()
    
    print("\nCI-Build-Probleme behoben! Die Builds sollten jetzt erfolgreich sein.")
    return 0


if __name__ == "__main__":
    sys.exit(main())