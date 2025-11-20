"""CLI placeholder for OpenExtract pipelines."""
from __future__ import annotations

import argparse
import sys


def main() -> None:
    parser = argparse.ArgumentParser(description="Run OpenExtract pipeline (placeholder).")
    parser.add_argument("--config", required=True, help="Path to pipeline YAML config.")
    args = parser.parse_args()
    print(
        "OpenExtract CLI 还在开发中，当前仅占位。\n"
        f"收到配置文件：{args.config}\n"
        "后续迭代将加载 YAML 并执行 pipeline."
    )


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        sys.exit(1)
