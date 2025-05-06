#!/usr/bin/env python3
"""
Dieses Skript aktualisiert alle GitHub Actions auf stabile Versionen in den CI-Workflow-Dateien.
Es aktualisiert:
- actions/checkout von v4 auf v3 (stabiler)
- actions/setup-python bleibt auf v4
- actions/cache von v4 auf v3 (stabiler)
- actions/upload-artifact von v4 auf v3 (stabiler)
- actions/setup-node von v3 auf v4
- andstor/file-existence-action bleibt auf v2
- shivammathur/setup-php bleibt auf v2

Diese Änderungen sind notwendig, um CI-Build-Fehler zu vermeiden, insbesondere:
"Missing command type for actions/checkout@v4.0.0"
"""

import re
import os

def update_action_versions(file_path):
    """GitHub Actions auf stabile Versionen aktualisieren."""
    updates = {
        # Wir kehren zu v3 zurück, das stabiler ist
        r'uses: actions/checkout@v4': 'uses: actions/checkout@v3',
        # Cache v3 ist stabiler
        r'uses: actions/cache@v4': 'uses: actions/cache@v3',
        # Upload artifact v3 ist stabiler
        r'uses: actions/upload-artifact@v4': 'uses: actions/upload-artifact@v3',
        # Node bleibt auf v4
        r'uses: actions/setup-node@v3': 'uses: actions/setup-node@v4',
    }
    
    if not os.path.exists(file_path):
        print(f"Datei nicht gefunden: {file_path}")
        return False
    
    with open(file_path, 'r') as file:
        content = file.read()
    
    original_content = content
    for pattern, replacement in updates.items():
        content = re.sub(pattern, replacement, content)
    
    if content != original_content:
        with open(file_path, 'w') as file:
            file.write(content)
        print(f"Datei {file_path} aktualisiert.")
        return True
    else:
        print(f"Keine Änderungen in {file_path} notwendig.")
        return False

def main():
    """Hauptfunktion, die alle CI-Workflow-Dateien aktualisiert."""
    workflows_dir = '.github/workflows'
    
    if not os.path.exists(workflows_dir):
        print(f"Verzeichnis nicht gefunden: {workflows_dir}")
        return
    
    updated_files = 0
    for filename in os.listdir(workflows_dir):
        if filename.endswith('.yml') or filename.endswith('.yaml'):
            file_path = os.path.join(workflows_dir, filename)
            if update_action_versions(file_path):
                updated_files += 1
    
    print(f"{updated_files} Dateien wurden aktualisiert.")

if __name__ == "__main__":
    main()