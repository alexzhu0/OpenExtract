# OpenExtract Overview

## 背景

- **PolicyKnowledgeBase**：沉淀了 Excel→多提示词→结构化 JSON 的政务标签流水线，但耦合度高、复用困难。
- **LangExtract**：展示了通用文档抽取框架的可能性（chunking、多 Provider、可视化），但缺乏我们需要的 Excel/多提示词/兜底逻辑。

OpenExtract 旨在把两者的优势结合起来——既保留业务验证过的策略性抽取能力，又提供 LangExtract 式的模块化体验，让任意团队在配置层面即可搭建自己的流水线。

## 核心术语

- **数据源（Source）**：可来自 Excel、CSV、JSON、数据库或任意自定义 `Reader`。
- **提示词单元（Prompt Unit）**：最小执行单元，包含 system prompt、schema、温度覆盖、兜底规则等。
- **流水线（Pipeline）**：定义 Source→Prompt Units→合并器（Merger）→落盘器（Sink）的完整 DAG。
- **Provider Adapter**：对接 LLM 提供商的抽象层，屏蔽不同 SDK/API 的差异。
- **质检工件**：JSON、JSONL、HTML 可视化等，方便人工审核和回溯。

## 典型场景

1. **政策/规划标签**：复用 PolicyKnowledgeBase 的 14 Prompt 套件，对政府政策做全量字段抽取。
2. **报告抽取**：自定义“章节→指标→风险”提示词，链路与政策场景保持一致。
3. **企业内部 SOP**：结合 LangExtract 的 chunking，把冗长流程文档拆分抽取，再汇总为结构化知识库。

## 设计原则

1. **配置优先**：把业务变化收敛到配置/提示词层面，代码只负责调度与通用能力。
2. **遵循可观测性**：每个 Prompt Unit 的输入/输出、重试情况、耗时都要可追踪。
3. **渐进增强**：允许用户按需启用 chunking、multi-pass、可视化等模块，避免一次性引入复杂度。
4. **无 vendor lock-in**：Provider Adapter 需易于扩展，支持自托管/第三方/云服务混用。

## 当前状态

- 仓库刚初始化，目录结构与文档已准备。
- 代码层面提供了 `pipelines/base.py`、`providers/base.py` 骨架，后续会逐步补全。
- 计划优先把 PolicyKnowledgeBase 的 `scripts/API.py` 能力迁移为可复用模块（详见 `docs/roadmap.md`）。
