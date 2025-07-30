from ..client import APIClient


class UsageService:
  path = "/v1/usage"

  def __init__(self, client: APIClient) -> None:
    self.client = client

  def get(self) -> str:
    data, _ = self.client.get(self.path)
    if isinstance(data, bytes):
      return data.decode()
    return data
