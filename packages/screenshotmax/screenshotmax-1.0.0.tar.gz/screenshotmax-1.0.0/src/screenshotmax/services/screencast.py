from typing import Any, Dict, Optional, Tuple
from ..client import APIClient
from ..options import ScreencastOptions


class ScreencastService:
  path = "/v1/screencast"

  def __init__(self, client: APIClient) -> None:
    self.client = client
    self._options: Optional[ScreencastOptions] = None
    self._request_kwargs = {
      "stream": True
    }

  def set_options(self, options: ScreencastOptions) -> "ScreencastService":
    self._options = options
    return self

  def get_url(self, signed: bool = True) -> str:
    if self._options is None:
      raise ValueError("Options not set.")
    params = self._options.to_dict()
    return (
      self.client.generate_signed_url(self.path, params)
      if signed
      else self.client.generate_url(self.path, params)
    )

  def fetch(self, signed: bool = True) -> Tuple[bytes, Dict[str, Any]]:
    if self._options is None:
      raise ValueError("Options not set.")
    data, headers = self.client.get(
      self.path,
      self._options.to_dict(),
      signed,
      **self._request_kwargs,
    )
    return data, headers
