"""CLI entry point for OpenExtract pipelines."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Dict

from dotenv import load_dotenv

from openextract.config import load_config, resolve_api_key
from openextract.pipelines.base import BasePipeline
from openextract.prompts.loader import PromptLoader
from openextract.providers.base import ProviderConfig
from openextract.providers.siliconflow import SiliconFlowProvider
from openextract.sources.excel import ExcelSource


def main() -> None:
    """Main CLI entry point."""
    # Load environment variables from .env file
    load_dotenv()
    
    parser = argparse.ArgumentParser(description="Run OpenExtract pipeline.")
    parser.add_argument("--config", required=True, help="Path to pipeline YAML config.")
    parser.add_argument("--settings", help="Optional path to global settings YAML.")
    args = parser.parse_args()

    try:
        # Load configuration
        print(f"Loading configuration from {args.config}...")
        config = load_config(args.config, args.settings)
        
        pipeline_config = config.get("pipeline", {})
        print(f"Pipeline: {pipeline_config.get('name', 'unnamed')}")
        print(f"Description: {pipeline_config.get('description', 'N/A')}")
        
        # Initialize data source
        source_config = pipeline_config.get("source", {})
        if source_config.get("type") != "excel":
            raise ValueError(f"Unsupported source type: {source_config.get('type')}")
        
        print(f"\nInitializing Excel source: {source_config.get('path')}...")
        source = ExcelSource(
            path=source_config["path"],
            sheet=source_config.get("sheet", 0),
            id_column=source_config.get("id_column", "Id"),
            title_column=source_config.get("title_column", "Title"),
            content_column=source_config.get("content_column", "Content"),
            max_rows=pipeline_config.get("runtime", {}).get("max_rows"),
        )
        
        # Initialize provider
        provider_config = pipeline_config.get("provider", {})
        provider_name = provider_config.get("name", "siliconflow")
        
        if provider_name != "siliconflow":
            raise ValueError(f"Unsupported provider: {provider_name}")
        
        # Resolve API key from settings or environment
        settings_providers = config.get("providers", {})
        provider_settings = settings_providers.get(provider_name, {})
        
        api_key = resolve_api_key(provider_settings)
        
        print(f"\nInitializing {provider_name} provider...")
        provider = SiliconFlowProvider(
            ProviderConfig(
                name=provider_name,
                api_base=provider_settings.get("api_base", "https://api.siliconflow.cn/v1"),
                model=provider_settings.get("model", "deepseek-chat"),
                api_key=api_key,
                concurrency=provider_config.get("concurrency", 1),
                sleep_seconds=provider_config.get("sleep_seconds", 1.0),
                timeout=provider_config.get("timeout", 120.0),
                think_mode=provider_settings.get("think_mode"),
            )
        )
        
        # Load prompts
        prompts_config = pipeline_config.get("prompts", {})
        prompts_dir = prompts_config.get("dir")
        
        if not prompts_dir:
            raise ValueError("No prompts directory specified in config")
        
        print(f"\nLoading prompts from {prompts_dir}...")
        prompt_loader = PromptLoader(
            prompts_dir=prompts_dir,
            temperature_overrides=prompts_config.get("temperature_overrides", {}),
        )
        prompts = prompt_loader.load_prompts()
        print(f"Loaded {len(prompts)} prompts")
        
        # Create and run pipeline
        print("\n" + "=" * 60)
        print("Starting pipeline execution...")
        print("=" * 60 + "\n")
        
        pipeline = BasePipeline(prompts=prompts, provider=provider)
        results = pipeline.run(source)
        
        # Save results
        outputs_config = pipeline_config.get("outputs", {})
        output_base = outputs_config.get("json_path", "output/api_results")
        
        output_path = Path(output_base)
        output_path.mkdir(parents=True, exist_ok=True)
        
        # Save as JSON
        json_file = output_path / "results.json"
        with open(json_file, "w", encoding="utf-8") as f:
            json.dump(
                [
                    {
                        "doc_id": r.doc_id,
                        "title": r.title,
                        "structured_tags": r.structured_tags,
                        "errors": r.errors,
                    }
                    for r in results
                ],
                f,
                ensure_ascii=False,
                indent=2,
            )
        print(f"\nResults saved to {json_file}")
        
        # Save as JSONL if configured
        if outputs_config.get("jsonl_dump"):
            jsonl_path = Path(outputs_config.get("jsonl_dump", output_path / "jsonl"))
            jsonl_path.mkdir(parents=True, exist_ok=True)
            jsonl_file = jsonl_path / "results.jsonl"
            
            with open(jsonl_file, "w", encoding="utf-8") as f:
                for r in results:
                    f.write(
                        json.dumps(
                            {
                                "doc_id": r.doc_id,
                                "title": r.title,
                                "structured_tags": r.structured_tags,
                                "errors": r.errors,
                            },
                            ensure_ascii=False,
                        )
                        + "\n"
                    )
            print(f"JSONL saved to {jsonl_file}")
        
        print("\n" + "=" * 60)
        print(f"Pipeline completed successfully. Processed {len(results)} documents.")
        print("=" * 60)
        
    except Exception as e:
        print(f"\nError: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        sys.exit(1)

