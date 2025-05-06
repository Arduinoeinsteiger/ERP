Import("env")

# Diese Funktion wird vor dem Bauen ausgeführt
def before_build(source, target, env):
    print("ESP32-C6 Bibliotheks-Handler wird ausgeführt")
    
    # AsyncTCP_RP2040W ausschließen, falls es installiert wurde
    if env.get("PIOPLATFORM") == "espressif32" and "esp32c6" in env.get("PIOENV"):
        # Möglichen Pfad zur AsyncTCP_RP2040W-Bibliothek ermitteln
        import os
        import platform
        import shutil
        
        system = platform.system()
        home_dir = os.path.expanduser("~")
        
        # Standardpfade für verschiedene Betriebssysteme
        pio_lib_dirs = []
        
        if system == "Windows":
            pio_lib_dirs.append(os.path.join(home_dir, ".platformio", "lib"))
        elif system == "Linux" or system == "Darwin":
            pio_lib_dirs.append(os.path.join(home_dir, ".platformio", "lib"))
        
        # Lokale Projektverzeichnisse
        pio_lib_dirs.append(os.path.join(env.get("PROJECT_DIR"), ".pio", "libdeps", "esp32c6"))
        
        # Suche und deaktiviere die AsyncTCP_RP2040W-Bibliothek
        for lib_dir in pio_lib_dirs:
            if os.path.exists(lib_dir):
                rp2040w_lib_path = os.path.join(lib_dir, "AsyncTCP_RP2040W")
                
                if os.path.exists(rp2040w_lib_path):
                    print(f"AsyncTCP_RP2040W gefunden in {rp2040w_lib_path}")
                    print("Deaktiviere die inkompatible Bibliothek")
                    
                    # Bibliothek umbenennen, um sie zu deaktivieren
                    try:
                        os.rename(rp2040w_lib_path, f"{rp2040w_lib_path}_disabled")
                        print("Bibliothek erfolgreich deaktiviert")
                    except:
                        print("Konnte Bibliothek nicht umbenennen. Versuche umbenennen der library.json")
                        try:
                            lib_json = os.path.join(rp2040w_lib_path, "library.json")
                            if os.path.exists(lib_json):
                                os.rename(lib_json, f"{lib_json}.disabled")
                                print("library.json erfolgreich deaktiviert")
                        except:
                            print("Fehler beim Deaktivieren der Bibliothek")
    
    print("ESP32-C6 Bibliotheks-Handler abgeschlossen")

# Registrieren der Funktion
env.AddPreAction("$BUILD_DIR/src/main.cpp.o", before_build)