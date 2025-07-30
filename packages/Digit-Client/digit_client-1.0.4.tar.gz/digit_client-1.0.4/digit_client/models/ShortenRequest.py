from dataclasses import dataclass, field
from typing import Optional, Dict

@dataclass
class ShortenRequest:
    """
    Model for Shorten Request
    """
    id: Optional[str] = None
    url: str = field(default="")
    valid_from: Optional[int] = None
    valid_till: Optional[int] = None

    def __post_init__(self):
        if not self.url:
            raise ValueError("url is required")
        if len(self.url) > 2000:  # Assuming a reasonable max length for URLs
            raise ValueError("url must not exceed 2000 characters")

    def to_dict(self) -> Dict[str, Optional[str]]:
        """
        Convert the model to a dictionary for API requests or serialization.
        """
        return {
            "id": self.id,
            "url": self.url,
            "validFrom": self.valid_from,
            "validTill": self.valid_till,
        }

# Builder class for ShortenRequest
class ShortenRequestBuilder:
    """
    Builder class for creating ShortenRequest objects.
    """
    def __init__(self):
        self._id: Optional[str] = None
        self._url: Optional[str] = None
        self._valid_from: Optional[int] = None
        self._valid_till: Optional[int] = None

    def with_id(self, id: str) -> 'ShortenRequestBuilder':
        self._id = id
        return self

    def with_url(self, url: str) -> 'ShortenRequestBuilder':
        self._url = url
        return self

    def with_valid_from(self, valid_from: int) -> 'ShortenRequestBuilder':
        self._valid_from = valid_from
        return self

    def with_valid_till(self, valid_till: int) -> 'ShortenRequestBuilder':
        self._valid_till = valid_till
        return self

    def build(self) -> ShortenRequest:
        if not self._url:
            raise ValueError("url is required")
        
        return ShortenRequest(
            id=self._id,
            url=self._url,
            valid_from=self._valid_from,
            valid_till=self._valid_till,
        )

