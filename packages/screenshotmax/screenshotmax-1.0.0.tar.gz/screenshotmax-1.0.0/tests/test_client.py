import types
import sys
import unittest
from unittest.mock import patch, Mock
import hmac
import hashlib
from urllib.parse import urlencode

# Provide a stub requests module so APIClient can be imported without the real dependency
requests_stub = types.ModuleType('requests')
requests_stub.get = lambda *args, **kwargs: None
requests_stub.post = lambda *args, **kwargs: None
requests_stub.delete = lambda *args, **kwargs: None
requests_stub.patch = lambda *args, **kwargs: None
sys.modules.setdefault('requests', requests_stub)

from screenshotmax.client import APIClient


class TestAPIClient(unittest.TestCase):
  def setUp(self):
    self.access_key = "test-access-key"
    self.secret_key = "test-secret-key"
    self.client = APIClient(self.access_key, self.secret_key)

  def test_generate_url_only_access_key(self):
    result = self.client.generate_url("/v1/test")
    self.assertEqual(
      result,
      "https://api.screenshotmax.com/v1/test?access_key=test-access-key",
    )

  def test_generate_url_with_params(self):
    result = self.client.generate_url(
      "/v1/test", {"format": "pdf", "url": "https://example.com"}
    )
    self.assertTrue(result.startswith("https://api.screenshotmax.com/v1/test?"))
    self.assertIn("access_key=test-access-key", result)
    self.assertIn("format=pdf", result)
    self.assertIn("url=https%3A%2F%2Fexample.com", result)

  def test_generate_url_ignores_none_values(self):
    result = self.client.generate_url(
      "/v1/test", {"format": None, "url": "https://example.com"}
    )
    self.assertIn("url=https%3A%2F%2Fexample.com", result)
    self.assertNotIn("format=", result)

  def test_generate_url_coerces_types(self):
    result = self.client.generate_url(
      "/v1/test", {"delay": 2, "full_page": True}
    )
    self.assertIn("delay=2", result)
    self.assertIn("full_page=True", result)

  def test_generate_url_encodes_special_chars(self):
    result = self.client.generate_url("/v1/test", {"query": "a&b=c"})
    self.assertIn("query=a%26b%3Dc", result)

  def test_constructor_validates_keys(self):
    with self.assertRaises(ValueError):
      APIClient("", "")

  def test_generate_signed_url_signature(self):
    params = {"url": "https://example.com", "format": "pdf"}
    query = urlencode({**params, "access_key": self.access_key})
    expected_signature = hmac.new(
      self.secret_key.encode(), query.encode(), hashlib.sha256
    ).hexdigest()
    result = self.client.generate_signed_url("/v1/pdf", params)
    self.assertIn("/v1/pdf?", result)
    self.assertIn(f"access_key={self.access_key}", result)
    self.assertIn(f"signature={expected_signature}", result)

  def test_generate_signed_url_skips_none(self):
    params = {"url": "https://example.com", "format": None}
    query = urlencode({"url": "https://example.com", "access_key": self.access_key})
    expected_signature = hmac.new(
      self.secret_key.encode(), query.encode(), hashlib.sha256
    ).hexdigest()
    result = self.client.generate_signed_url("/v1/pdf", params)
    self.assertIn("url=https%3A%2F%2Fexample.com", result)
    self.assertNotIn("format=", result)
    self.assertIn(f"signature={expected_signature}", result)

  def test_generate_signed_url_empty_params(self):
    query = urlencode({"access_key": self.access_key})
    expected_signature = hmac.new(
      self.secret_key.encode(), query.encode(), hashlib.sha256
    ).hexdigest()
    result = self.client.generate_signed_url("/v1/pdf")
    self.assertEqual(
      result,
      f"https://api.screenshotmax.com/v1/pdf?access_key={self.access_key}&signature={expected_signature}",
    )

  @patch("requests.get")
  def test_get_signed(self, mock_get: Mock):
    mock_get.return_value = Mock(content=b"get-data", headers={"key": "value"})
    data, headers = self.client.get("/test", {"q": "query"}, True)
    mock_get.assert_called_once()
    self.assertEqual(data, b"get-data")
    self.assertEqual(headers, {"key": "value"})

  @patch("requests.get")
  def test_get_unsigned(self, mock_get: Mock):
    mock_get.return_value = Mock(content=b"unsigned-data", headers={"key": "value"})
    data, headers = self.client.get("/test", {"q": "query"}, False)
    mock_get.assert_called_once()
    self.assertEqual(data, b"unsigned-data")
    self.assertEqual(headers, {"key": "value"})

  @patch("requests.post")
  def test_post(self, mock_post: Mock):
    mock_post.return_value = Mock(json=Mock(return_value="post-data"), headers={"key": "value"})
    data, headers = self.client.post("/test", {"body": "content"})
    mock_post.assert_called_once()
    self.assertEqual(data, "post-data")
    self.assertEqual(headers, {"key": "value"})

  @patch("requests.delete")
  def test_delete(self, mock_delete: Mock):
    mock_delete.return_value = Mock(json=Mock(return_value="delete-data"))
    data = self.client.delete("/test")
    mock_delete.assert_called_once()
    self.assertEqual(data, "delete-data")

  @patch("requests.patch")
  def test_patch(self, mock_patch: Mock):
    mock_patch.return_value = Mock(json=Mock(return_value="patch-data"))
    data = self.client.patch("/test", {"update": "info"})
    mock_patch.assert_called_once()
    self.assertEqual(data, "patch-data")


if __name__ == "__main__":
  unittest.main()
