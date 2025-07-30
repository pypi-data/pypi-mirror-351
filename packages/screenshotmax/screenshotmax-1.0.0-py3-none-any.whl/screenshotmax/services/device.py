from ..client import APIClient


class DeviceService:
  path = "/v1/devices"

  def __init__(self, client: APIClient) -> None:
    self.client = client

  def get(self) -> str:
    data, _ = self.client.get(self.path)
    if isinstance(data, bytes):
      return data.decode()
    return data
