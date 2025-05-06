"""
Tests für den QR-Code-Generator

Dieser Testfall prüft die Funktionalität des QR-Code-Generators
in der SwissAirDry-API.

@author Swiss Air Dry Team <info@swissairdry.com>
@copyright 2023-2025 Swiss Air Dry Team
"""

import unittest
import json
import io
import base64
from unittest.mock import patch, MagicMock

class QRCodeGeneratorTests(unittest.TestCase):
    """
    Testfälle für den QR-Code-Generator
    """
    
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
        
        # PIL Image Mock
        self.mock_pil_image = MagicMock()
        self.mock_image.return_value = self.mock_pil_image
        
        # Font Mock
        self.mock_font_instance = MagicMock()
        self.mock_font.return_value = self.mock_font_instance
        self.mock_font_instance.getlength = lambda x: len(x) * 10  # Einfache Berechnung für Textlänge
    
    def tearDown(self):
        """
        Aufräumen nach dem Test
        """
        self.qrcode_patcher.stop()
        self.image_patcher.stop()
        self.draw_patcher.stop()
        self.font_patcher.stop()
    
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
        
    def test_qrcode_with_title(self):
        """
        Testet die Erstellung eines QR-Codes mit Titel
        """
        from swissairdry_new.api.minimal_http_server import SwissAirDryRequestHandler
        
        # Mock für HTTP-Handler
        handler = MagicMock()
        handler._send_image_response = MagicMock()
        
        # Query-Parameter
        query_params = {
            'content': ['TestContent'],
            'size': ['200'],
            'title': ['Custom Title']
        }
        
        # QR-Code generieren
        SwissAirDryRequestHandler._handle_qrcode_api(handler, query_params)
        
        # Überprüfen, ob die Mock-Methoden aufgerufen wurden
        self.mock_qrcode.assert_called_once()
        self.mock_qr_instance.add_data.assert_called_once_with('TestContent')
        
        # Bei Verwendung eines Titels sollte ein neues PIL-Bild erstellt werden
        self.mock_image.assert_called_once()
        
        # Überprüfen, ob die Antwort gesendet wurde
        handler._send_image_response.assert_called_once()
    
    def test_qrcode_error_handling(self):
        """
        Testet die Fehlerbehandlung bei der QR-Code-Generierung
        """
        from swissairdry_new.api.minimal_http_server import SwissAirDryRequestHandler
        
        # Mock für HTTP-Handler
        handler = MagicMock()
        handler._send_json_response = MagicMock()
        
        # Query-Parameter ohne Inhalt
        query_params = {
            'size': ['200'],
            'title': ['Test Title']
        }
        
        # QR-Code generieren
        SwissAirDryRequestHandler._handle_qrcode_api(handler, query_params)
        
        # Überprüfen, ob eine Fehlermeldung gesendet wurde
        handler._send_json_response.assert_called_once()
        args, kwargs = handler._send_json_response.call_args
        self.assertEqual(kwargs['status_code'], 400)  # HTTP 400 Bad Request
        self.assertIn('error', args[0])  # Fehlermeldung in der Antwort
        
    def test_qrcode_size_validation(self):
        """
        Testet die Validierung der QR-Code-Größe
        """
        from swissairdry_new.api.minimal_http_server import SwissAirDryRequestHandler
        
        # Mock für HTTP-Handler
        handler = MagicMock()
        handler._send_json_response = MagicMock()
        
        # Query-Parameter mit ungültiger Größe
        query_params = {
            'content': ['TestContent'],
            'size': ['2000'],  # Zu groß (über dem Maximum von 1000)
            'title': ['Test Title']
        }
        
        # QR-Code generieren
        SwissAirDryRequestHandler._handle_qrcode_api(handler, query_params)
        
        # Überprüfen, ob eine Fehlermeldung gesendet wurde
        handler._send_json_response.assert_called_once()
        args, kwargs = handler._send_json_response.call_args
        self.assertEqual(kwargs['status_code'], 400)  # HTTP 400 Bad Request
        self.assertIn('error', args[0])  # Fehlermeldung in der Antwort
        

if __name__ == '__main__':
    unittest.main()