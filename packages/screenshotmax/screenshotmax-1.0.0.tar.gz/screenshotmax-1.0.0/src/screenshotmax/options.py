from dataclasses import dataclass, field, asdict
from typing import Optional, List, Dict, Any
from .enums import (
    PDFPaperFormat, ImageFormat, VideoFormat, ScrapeFormat,
    ViewportDevice, MediaType, VisionDeficiency,
    BlockAnnoyance, BlockRessources, Timezone, IpLocation,
    WaitUntil, ScrollEasing, Scenario
)
from enum import Enum


@dataclass
class BaseOptions:
  url: Optional[str] = None
  gpu_rendering: Optional[bool] = None
  capture_beyond_viewport: Optional[bool] = None
  viewport_device: Optional[ViewportDevice] = None
  viewport_width: Optional[int] = None
  viewport_height: Optional[int] = None
  viewport_landscape: Optional[bool] = None
  viewport_has_touch: Optional[bool] = None
  viewport_mobile: Optional[bool] = None
  device_scale_factor: Optional[float] = None
  attachment_name: Optional[str] = None
  dark_mode: Optional[bool] = None
  reduced_motion: Optional[bool] = None
  media_type: Optional[MediaType] = None
  vision_deficiency: Optional[VisionDeficiency] = None
  clip_x: Optional[int] = None
  clip_y: Optional[int] = None
  clip_width: Optional[int] = None
  clip_height: Optional[int] = None
  block_annoyance: Optional[BlockAnnoyance] = None
  block_ressources: Optional[List[BlockRessources]] = field(default_factory=list)
  geolocation_accuracy: Optional[int] = None
  geolocation_latitude: Optional[float] = None
  geolocation_longitude: Optional[float] = None
  timezone: Optional[Timezone] = None
  hide_selectors: Optional[List[str]] = field(default_factory=list)
  click_selector: Optional[str] = None
  authorization: Optional[str] = None
  user_agent: Optional[str] = None
  cookies: Optional[List[str]] = field(default_factory=list)
  headers: Optional[List[str]] = field(default_factory=list)
  bypass_csp: Optional[bool] = None
  ip_location: Optional[IpLocation] = None
  proxy: Optional[str] = None
  delay: Optional[int] = None
  timeout: Optional[int] = None
  wait_until: Optional[List[WaitUntil]] = field(default_factory=list)
  cache: Optional[bool] = None
  cache_ttl: Optional[int] = None
  metadata_icon: Optional[bool] = None
  metadata_fonts: Optional[bool] = None
  metadata_title: Optional[bool] = None
  metadata_hash: Optional[bool] = None
  metadata_status: Optional[bool] = None
  metadata_headers: Optional[bool] = None
  async_mode: Optional[bool] = field(default=None, metadata={"name": "async"})
  webhook_url: Optional[str] = None
  webhook_signed: Optional[bool] = None

  def to_dict(self) -> Dict[str, Any]:
    data = asdict(self)
    if "async_mode" in data:
      data["async"] = data.pop("async_mode")

    result = {}
    for k, v in data.items():
      if v is None:
        continue
      if isinstance(v, list) and len(v) == 0:
        continue
      if isinstance(v, Enum):
        result[k] = v.value
      elif isinstance(v, list) and v and isinstance(v[0], Enum):
        result[k] = [item.value for item in v]
      else:
        result[k] = v
    return result


@dataclass
class ScreenshotOptions(BaseOptions):
  html: Optional[str] = None
  format: Optional[ImageFormat] = None
  full_page: Optional[bool] = None
  full_page_scroll: Optional[bool] = None
  full_page_scroll_by_amount: Optional[int] = None
  full_page_scroll_by_duration: Optional[int] = None
  image_quality: Optional[int] = None
  image_width: Optional[int] = None
  image_height: Optional[int] = None
  omit_background: Optional[bool] = None
  metadata_image_size: Optional[bool] = None
  signature: Optional[str] = None


@dataclass
class PDFOptions(BaseOptions):
  html: Optional[str] = None
  pdf_paper_format: Optional[PDFPaperFormat] = None
  pdf_landscape: Optional[bool] = None
  pdf_print_background: Optional[bool] = None
  signature: Optional[str] = None


@dataclass
class ScreencastOptions(BaseOptions):
  format: Optional[VideoFormat] = None
  duration: Optional[int] = None
  scenario: Optional[Scenario] = None
  scroll_by_amount: Optional[int] = None
  scroll_by_delay: Optional[int] = None
  scroll_by_duration: Optional[int] = None
  scroll_back: Optional[bool] = None
  scroll_back_delay: Optional[int] = None
  scroll_easing: Optional[ScrollEasing] = None
  signature: Optional[str] = None


@dataclass
class ScrapeOptions(BaseOptions):
  format: Optional[ScrapeFormat] = None
  js_enabled: Optional[bool] = None
  signature: Optional[str] = None
