"""Prompt loading and rendering for OpenExtract."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List

from openextract.pipelines.base import Document


@dataclass
class TemplatePrompt:
    """Simple prompt unit with template rendering."""
    
    name: str
    section: str
    template: str
    temperature: float = 0.2
    
    def render_input(self, document: Document, context: Dict[str, Any]) -> Dict[str, Any]:
        """Render prompt template with document and context."""
        # Simple variable substitution
        rendered = self.template.format(
            title=document.title,
            content=document.payload,
            **context
        )
        
        messages = [
            {"role": "user", "content": rendered}
        ]
        
        return {
            "messages": messages,
            "temperature": self.temperature,
        }


class PromptLoader:
    """Load prompts from directory structure."""
    
    def __init__(self, prompts_dir: str | Path, temperature_overrides: Dict[str, float] | None = None):
        """
        Initialize prompt loader.
        
        Args:
            prompts_dir: Directory containing prompt files
            temperature_overrides: Optional dict mapping prompt names to temperatures
        """
        self.prompts_dir = Path(prompts_dir)
        self.temperature_overrides = temperature_overrides or {}
        
        if not self.prompts_dir.exists():
            raise FileNotFoundError(f"Prompts directory not found: {self.prompts_dir}")
    
    def load_prompts(self) -> List[TemplatePrompt]:
        """
        Load all prompt files from directory.
        
        Returns:
            List of TemplatePrompt objects
        """
        prompts: List[TemplatePrompt] = []
        
        # Look for .txt or .md files
        for file_path in sorted(self.prompts_dir.glob("*.txt")):
            prompt = self._load_prompt_file(file_path)
            prompts.append(prompt)
        
        # Also check for .md files if no .txt found
        if not prompts:
            for file_path in sorted(self.prompts_dir.glob("*.md")):
                prompt = self._load_prompt_file(file_path)
                prompts.append(prompt)
        
        return prompts
    
    def _load_prompt_file(self, file_path: Path) -> TemplatePrompt:
        """Load a single prompt file."""
        name = file_path.stem
        section = name  # Use filename as section name
        
        with open(file_path, "r", encoding="utf-8") as f:
            template = f.read()
        
        temperature = self.temperature_overrides.get(name, 0.2)
        
        return TemplatePrompt(
            name=name,
            section=section,
            template=template,
            temperature=temperature,
        )
