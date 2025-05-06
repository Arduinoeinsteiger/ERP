#!/usr/bin/env python3
"""
Dieses Skript aktualisiert Pydantic-Konfigurationen in der gesamten Codebasis,
indem es 'from_attributes = True' durch 'from_attributes = True' ersetzt.
"""

import os
import re

def update_pydantic_configs(directory):
    """Aktualisiert Pydantic-Konfigurationen in allen Python-Dateien im angegebenen Verzeichnis."""
    count = 0
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith('.py'):
                file_path = os.path.join(root, file)
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Suche nach "from_attributes = True" in Konfigurationsklassen
                if 'from_attributes = True' in content:
                    print(f"Aktualisiere {file_path}")
                    updated_content = re.sub(
                        r'(\s+)class Config:\s+(\s+)from_attributes = True', 
                        r'\1class Config:\2from_attributes = True', 
                        content
                    )
                    
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(updated_content)
                    
                    count += 1
    
    return count

if __name__ == "__main__":
    directories = ['swissairdry', 'build']
    total_updated = 0
    
    for directory in directories:
        if os.path.exists(directory):
            updated = update_pydantic_configs(directory)
            total_updated += updated
            print(f"Aktualisierte {updated} Dateien in {directory}")
    
    print(f"Insgesamt {total_updated} Dateien aktualisiert")