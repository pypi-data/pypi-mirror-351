import hmac
import hashlib
from typing import Any, Dict, Optional, Tuple
import requests


class APIClient:
  base_url = "https://api.screenshotmax.com"

  def __init__(self, access_key: str, secret_key: str) -> None:
    if not access_key or not secret_key:
      raise ValueError("Access and secret keys must both be provided and non-empty.")
    self.access_key = access_key
    self.secret_key = secret_key

  def _sign_request(self, s: str) -> str:
    return hmac.new(self.secret_key.encode(), s.encode(), hashlib.sha256).hexdigest()

  def _compute_query(self, obj: Dict[str, Any]) -> str:
    from urllib.parse import urlencode

    filtered = {k: str(v) for k, v in obj.items() if v is not None}
    return urlencode(filtered)

  def generate_url(self, path: str, params: Optional[Dict[str, Any]] = None) -> str:
    params = params or {}
    query = self._compute_query({**params, "access_key": self.access_key})
    return f"{self.base_url}{path}?{query}"

  def generate_signed_url(self, path: str, params: Optional[Dict[str, Any]] = None) -> str:
    params = params or {}
    query = self._compute_query({**params, "access_key": self.access_key})
    signature = self._sign_request(query)
    return f"{self.base_url}{path}?{query}&signature={signature}"

  def get(self, path: str, options: Optional[Dict[str, Any]] = None, signed: bool = False,
      **request_kwargs: Any) -> Tuple[Any, Dict[str, Any]]:
    url = self.generate_signed_url(path, options) if signed else self.generate_url(path, options)
    response = requests.get(url, **request_kwargs)
    return response.content, dict(response.headers)

  def post(self, path: str, options: Optional[Dict[str, Any]] = None, **request_kwargs: Any) -> Tuple[Any, Dict[str, Any]]:
    url = f"{self.base_url}{path}"
    headers = {"X-Access-Key": self.access_key, **request_kwargs.pop("headers", {})}
    response = requests.post(url, json=options or {}, headers=headers, **request_kwargs)
    return response.json(), dict(response.headers)

  def delete(self, path: str, **request_kwargs: Any) -> Any:
    url = f"{self.base_url}{path}"
    headers = {"X-Access-Key": self.access_key, **request_kwargs.pop("headers", {})}
    response = requests.delete(url, headers=headers, **request_kwargs)
    return response.json()

  def patch(self, path: str, options: Optional[Dict[str, Any]] = None, **request_kwargs: Any) -> Any:
    url = f"{self.base_url}{path}"
    headers = {"X-Access-Key": self.access_key, **request_kwargs.pop("headers", {})}
    response = requests.patch(url, json=options or {}, headers=headers, **request_kwargs)
    return response.json()
