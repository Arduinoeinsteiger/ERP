#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Diese Datei ist für die Kompatibilität mit älteren pip-Versionen und Installationswerkzeugen,
die noch kein pyproject.toml unterstützen.
"""

import sys
from setuptools import setup, find_packages

# Kompatibilität mit älteren Versionen der Build-Tools sicherstellen
print(f"Running setup.py with Python {sys.version}")

setup(
    name="swissairdry",
    version="0.1.0",
    description="SwissAirDry - Eine Anwendung für die Verwaltung von Trocknungsgeräten und Felddienstoperationen",
    author="Swiss Air Dry Team",
    author_email="info@swissairdry.com",
    packages=find_packages(include=['swissairdry', 'swissairdry.*']),
    package_dir={"": "."},
    package_data={'swissairdry': ['api/templates/*', 'api/static/*']},
    python_requires=">=3.9",
    include_package_data=True,
    install_requires=[
        "aiofiles>=0.8.0",
        "bcrypt>=3.2.0",
        "bleak>=0.14.0",
        "fastapi>=0.70.0",
        "flake8>=4.0.0",
        "flask>=2.0.0",
        "flask-cors>=3.0.10",
        "flask-sqlalchemy>=2.5.0",
        "httpx>=0.22.0",  # Für starlette.testclient
        "jinja2>=3.0.0",
        "markdown>=3.3.0",
        "paho-mqtt>=1.6.0",
        "pandas>=1.3.0",
        "pillow>=9.0.0",
        "psutil>=5.9.0",
        "psycopg2-binary>=2.9.3",
        "pydantic>=1.9.0",
        "python-dotenv>=0.19.0",
        "python-multipart>=0.0.5",
        "qrcode>=7.3.0",
        "requests>=2.27.0",
        "setuptools==59.8.0",
        "sqlalchemy>=1.4.0,<2.0.0",
        "trafilatura>=1.2.0",
        "uvicorn>=0.17.0",
    ],
)