"""Pipeline engine skeleton for OpenExtract.

This module sketches the core interfaces and orchestration flow.
Concrete implementations will extend these classes to provide
Excel readers, prompt planning, provider execution, and result sinks.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, Iterable, List, Protocol


@dataclass
class Document:
    """Standardized representation of one row/article."""

    doc_id: str
    title: str
    payload: str
    meta: Dict[str, Any] = field(default_factory=dict)


class PromptUnit(Protocol):
    """Single prompt execution unit definition."""

    name: str
    section: str

    def render_input(self, document: Document, context: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare the prompt payload for the provider."""


class ProviderAdapter(Protocol):
    """Adapter interface (mirrors providers.base.Provider)."""

    def invoke(
        self,
        prompt: PromptUnit,
        document: Document,
        payload: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Execute prompt via provider and return parsed JSON."""


@dataclass
class PipelineResult:
    """Final structured output for a document."""

    doc_id: str
    title: str
    structured_tags: Dict[str, Any]
    errors: List[Dict[str, Any]] = field(default_factory=list)


class BasePipeline:
    """Minimal pipeline skeleton."""

    def __init__(
        self,
        prompts: Iterable[PromptUnit],
        provider: ProviderAdapter,
    ) -> None:
        self.prompts = list(prompts)
        self.provider = provider

    def run(self, documents: Iterable[Document]) -> List[PipelineResult]:
        """Execute prompts for all documents and return structured results."""

        results: List[PipelineResult] = []
        for document in documents:
            structured_sections: Dict[str, Any] = {}
            context: Dict[str, Any] = {}
            errors: List[Dict[str, Any]] = []
            for prompt in self.prompts:
                payload = prompt.render_input(document, context)
                try:
                    response = self.provider.invoke(prompt, document, payload)
                except Exception as exc:  # placeholder error handling
                    errors.append({"prompt": prompt.name, "error": str(exc)})
                    continue
                structured_sections[prompt.section] = response
                context[prompt.section] = response
            results.append(
                PipelineResult(
                    doc_id=document.doc_id,
                    title=document.title,
                    structured_tags=structured_sections,
                    errors=errors,
                )
            )
        return results
