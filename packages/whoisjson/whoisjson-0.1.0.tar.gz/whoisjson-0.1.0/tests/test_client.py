import unittest
from unittest.mock import patch
from whoisjson import WhoisJsonClient

class TestWhoisJsonClient(unittest.TestCase):
    def setUp(self):
        self.client = WhoisJsonClient()
        self.client_with_key = WhoisJsonClient(api_key="test-key")
        self.test_domain = "example.com"

    def test_init(self):
        self.assertIsNone(self.client.api_key)
        self.assertEqual(self.client_with_key.api_key, "test-key")

    def test_validates_domain(self):
        with self.assertRaises(ValueError):
            self.client.whois("")
        with self.assertRaises(ValueError):
            self.client.nslookup("")
        with self.assertRaises(ValueError):
            self.client.ssl_cert_check("")

    @patch("requests.get")
    def test_whois_success(self, mock_get):
        mock_response = {
            "domain": "example.com",
            "registrar": "Example Registrar"
        }
        mock_get.return_value.json.return_value = mock_response
        mock_get.return_value.raise_for_status.return_value = None

        result = self.client.whois(self.test_domain)
        self.assertEqual(result, mock_response)
        
        # Test backward compatibility
        result = self.client.lookup(self.test_domain)
        self.assertEqual(result, mock_response)

        # Verify API key is sent when provided
        result = self.client_with_key.whois(self.test_domain)
        headers = mock_get.call_args[1]["headers"]
        self.assertEqual(headers["Authorization"], "Bearer test-key")

    @patch("requests.get")
    def test_nslookup_success(self, mock_get):
        mock_response = {
            "domain": "example.com",
            "records": {
                "A": ["93.184.216.34"],
                "AAAA": ["2606:2800:220:1:248:1893:25c8:1946"]
            }
        }
        mock_get.return_value.json.return_value = mock_response
        mock_get.return_value.raise_for_status.return_value = None

        result = self.client.nslookup(self.test_domain)
        self.assertEqual(result, mock_response)

    @patch("requests.get")
    def test_ssl_cert_check_success(self, mock_get):
        mock_response = {
            "domain": "example.com",
            "valid": True,
            "expires": "2024-12-31",
            "issuer": "Example CA"
        }
        mock_get.return_value.json.return_value = mock_response
        mock_get.return_value.raise_for_status.return_value = None

        result = self.client.ssl_cert_check(self.test_domain)
        self.assertEqual(result, mock_response)

if __name__ == "__main__":
    unittest.main() 