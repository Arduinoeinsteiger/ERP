#!/usr/bin/env python3
"""
Test-Skript für die BLE-API der SwissAirDry-Plattform.

Dieses Skript führt Tests für die BLE-API-Endpunkte durch.
Um es zu verwenden, führen Sie es einfach aus, während der SwissAirDry-Server läuft:

python test_ble_api.py
"""

import sys
import json
import argparse
import requests
from datetime import datetime, timedelta

# Standard-URL des API-Servers
DEFAULT_API_URL = "http://localhost:5000"

def print_response(response, label=None):
    """Gibt eine formatierte API-Antwort aus."""
    if label:
        print(f"\n=== {label} ===")
    
    print(f"Status: {response.status_code}")
    try:
        print(json.dumps(response.json(), indent=2, ensure_ascii=False))
    except json.JSONDecodeError:
        print(f"Keine gültige JSON-Antwort: {response.text}")


def test_get_ble_devices(api_url):
    """Testet den API-Endpunkt zum Abrufen aller BLE-Geräte."""
    print("\n\n=== Teste GET /api/ble/devices ===")
    response = requests.get(f"{api_url}/api/ble/devices")
    print_response(response)
    return response.json().get("devices", [])


def test_power_control(api_url, device_id, state=True):
    """Testet den API-Endpunkt zur Steuerung des Ein/Aus-Zustands."""
    print(f"\n\n=== Teste POST /api/ble/device/{device_id}/power (state={state}) ===")
    response = requests.post(
        f"{api_url}/api/ble/device/{device_id}/power",
        json={"state": state}
    )
    print_response(response)


def test_fan_control(api_url, device_id, speed=50):
    """Testet den API-Endpunkt zur Steuerung der Lüftergeschwindigkeit."""
    print(f"\n\n=== Teste POST /api/ble/device/{device_id}/fan (speed={speed}) ===")
    response = requests.post(
        f"{api_url}/api/ble/device/{device_id}/fan",
        json={"speed": speed}
    )
    print_response(response)


def test_assign_task(api_url, device_id, task_id=1, delay_minutes=5):
    """Testet den API-Endpunkt zur Aufgabenzuweisung."""
    start_time = (datetime.now() + timedelta(minutes=delay_minutes)).isoformat()
    print(f"\n\n=== Teste POST /api/ble/device/{device_id}/assign_task ===")
    print(f"Task-ID: {task_id}, Startzeit: {start_time}")
    
    response = requests.post(
        f"{api_url}/api/ble/device/{device_id}/assign_task",
        json={"task_id": task_id, "start_time": start_time}
    )
    print_response(response)


def test_error_handling(api_url):
    """Testet die Fehlerbehandlung der API."""
    print("\n\n=== Teste Fehlerbehandlung ===")
    
    # Nicht existierendes Gerät
    response = requests.post(
        f"{api_url}/api/ble/device/nicht_existent/power",
        json={"state": True}
    )
    print_response(response, "404 Nicht gefunden (Gerät existiert nicht)")
    
    # Fehlende Parameter
    response = requests.post(
        f"{api_url}/api/ble/device/test_device/fan",
        json={}
    )
    print_response(response, "400 Ungültige Anfrage (Fehlender Parameter)")
    
    # Ungültige Parameter
    response = requests.post(
        f"{api_url}/api/ble/device/test_device/fan",
        json={"speed": 150}
    )
    print_response(response, "400 Ungültige Anfrage (Wert außerhalb des gültigen Bereichs)")


def main():
    parser = argparse.ArgumentParser(description="Test der SwissAirDry BLE-API")
    parser.add_argument("--url", default=DEFAULT_API_URL, help=f"API-URL (Standard: {DEFAULT_API_URL})")
    parser.add_argument("--device", default="test_device", help="Geräte-ID für Tests (Standard: test_device)")
    parser.add_argument("--task", type=int, default=1, help="Aufgaben-ID für Tests (Standard: 1)")
    args = parser.parse_args()
    
    print("SwissAirDry BLE-API Tester")
    print(f"API-URL: {args.url}")
    print(f"Test-Gerät: {args.device}")
    
    # Führe alle Tests durch
    devices = test_get_ble_devices(args.url)
    
    if not devices:
        print("\nKeine BLE-Geräte gefunden. Tests werden trotzdem mit der angegebenen Geräte-ID durchgeführt.")
    else:
        print(f"\nGefundene Geräte: {len(devices)}")
        # Wenn Geräte gefunden wurden, verwende die erste Geräte-ID
        args.device = devices[0].get("device_id", args.device)
        print(f"Verwende Gerät: {args.device}")
    
    # Führe Tests mit dem ausgewählten/gefundenen Gerät durch
    test_power_control(args.url, args.device, True)
    test_power_control(args.url, args.device, False)
    test_fan_control(args.url, args.device, 75)
    test_assign_task(args.url, args.device, args.task)
    test_error_handling(args.url)
    
    print("\n\nAlle Tests abgeschlossen!")


if __name__ == "__main__":
    main()