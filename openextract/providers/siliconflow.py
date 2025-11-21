"""SiliconFlow provider adapter for OpenExtract."""
from __future__ import annotations

import time
from typing import Any, Dict

import requests

from openextract.providers.base import Provider, ProviderConfig


class SiliconFlowProvider:
    """SiliconFlow API provider implementation."""
    
    def __init__(self, config: ProviderConfig):
        """Initialize SiliconFlow provider with configuration."""
        self.config = config
        self._last_request_time = 0.0
    
    def prepare_payload(self, prompt_payload: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare payload for SiliconFlow API."""
        messages = prompt_payload.get("messages", [])
        
        payload = {
            "model": self.config.model,
            "messages": messages,
            "temperature": prompt_payload.get("temperature", 0.2),
            "max_tokens": prompt_payload.get("max_tokens", 1500),
        }
        
        # Add think mode if configured
        if self.config.think_mode is not None:
            payload["stream"] = False
            payload["response_format"] = {"type": "json_object"}
        
        return payload
    
    def dispatch(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Execute HTTP request to SiliconFlow API."""
        # Rate limiting
        if self.config.sleep_seconds > 0:
            elapsed = time.time() - self._last_request_time
            if elapsed < self.config.sleep_seconds:
                time.sleep(self.config.sleep_seconds - elapsed)
        
        headers = {
            "Authorization": f"Bearer {self.config.api_key}",
            "Content-Type": "application/json",
        }
        
        url = f"{self.config.api_base}/chat/completions"
        
        try:
            response = requests.post(
                url,
                json=payload,
                headers=headers,
                timeout=self.config.timeout,
            )
            response.raise_for_status()
            self._last_request_time = time.time()
            return response.json()
        except requests.exceptions.RequestException as e:
            raise RuntimeError(f"SiliconFlow API request failed: {e}") from e
    
    def parse_response(self, response: Dict[str, Any]) -> Dict[str, Any]:
        """Extract structured result from SiliconFlow response."""
        try:
            content = response["choices"][0]["message"]["content"]
            
            # Try to parse as JSON if response_format was json_object
            if self.config.think_mode:
                import json
                return json.loads(content)
            
            # Otherwise return as-is wrapped in a dict
            return {"content": content}
        except (KeyError, IndexError, ValueError) as e:
            raise ValueError(f"Failed to parse SiliconFlow response: {e}") from e
    
    def invoke(self, prompt, document, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Execute full request cycle: prepare -> dispatch -> parse."""
        prepared = self.prepare_payload(payload)
        response = self.dispatch(prepared)
        return self.parse_response(response)
