"""Provider adapter abstraction.

Concrete adapters will translate PromptUnit payloads into actual API calls
and normalize responses to dictionaries that downstream steps can consume.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Protocol


@dataclass
class ProviderConfig:
    """Runtime configuration for provider adapters."""

    name: str
    api_base: str
    model: str
    api_key: str
    concurrency: int = 1
    sleep_seconds: float = 0.0
    timeout: float = 120.0
    think_mode: bool | None = None


class Provider(Protocol):
    """Protocol all concrete adapters should follow."""

    config: ProviderConfig

    def prepare_payload(self, prompt_payload: Dict[str, Any]) -> Dict[str, Any]:
        """Enrich payload with provider-specific options before dispatch."""

    def dispatch(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Perform the HTTP/API call and return raw JSON."""

    def parse_response(self, response: Dict[str, Any]) -> Dict[str, Any]:
        """Extract the structured result from provider response."""

    def invoke(self, prompt, document, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Convenience method chaining prepare -> dispatch -> parse."""
        prepared = self.prepare_payload(payload)
        response = self.dispatch(prepared)
        return self.parse_response(response)
