from .client import APIClient
from .services import (
  ScreenshotService,
  ScreencastService,
  ScrapeService,
  PDFService,
  TaskService,
  UsageService,
  DeviceService,
)


class SDK:
  def __init__(self, access_key: str, secret_key: str) -> None:
    client = APIClient(access_key, secret_key)
    self.screenshot = ScreenshotService(client)
    self.screencast = ScreencastService(client)
    self.scrape = ScrapeService(client)
    self.pdf = PDFService(client)
    self.task = TaskService(client)
    self.usage = UsageService(client)
    self.device = DeviceService(client)
