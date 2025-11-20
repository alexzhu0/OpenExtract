# OpenExtract

OpenExtract 是一个可复用的结构化抽取框架，旨在把 `PolicyKnowledgeBase` 项目（该项目是笔者在实际工作中构建政策知识库时的一个经历结晶）中沉淀下来的 “Excel → 多提示词 → 结构化 JSON” 流程模块化，并借鉴 LangExtract 在分块处理、可视化复核方面的优秀实践，帮助更多团队快速搭建自己的抽取流水线。

## 主要目标

- **声明式流水线**：通过 YAML/JSON 描述 “数据源 → 提示词计划 → 模型调用 → 结果合并”，减少硬编码。
- **提示词库与 Schema 注册**：集中管理提示词、Few-shot 示例与字段定义，支持版本化与跨项目复用。
- **Provider 插件化**：统一封装 SiliconFlow、DeepSeek、Gemini、Ollama 等服务，内建速率限制、重试与思考模式控制。
- **分块与并行**：可选 chunking、multi-pass、并发配置，兼顾长文支持与 API 负载。
- **质检与复核**：输出 JSON/JSONL 的同时生成交互式 HTML，方便人工审核与追踪。

## 可能应用场景

- **政策/法规标签**：复用示例 pipeline 对政府政策、部门规章、规划方案等做多字段抽取。
- **报告要素提取**：在研究报告、审计报告、可研文件中抽取章节、指标、风险、建议等要素，输出结构化 JSON 便于统计。
- **企业 SOP / 制度知识库**：对内部制度、流程文档进行 chunking + 提示词抽取，生成可检索的流程图谱。
- **合规 / 尽调摘要**：针对海量条款、合同文本，按章节抽取义务、限制、违约责任等，辅助合规审查。
- **培训与质检**：结合 JSONL + HTML 可视化，快速搭建人工复核界面，支撑批量审核或训练数据制作。

## 仓库结构

```
OpenExtract/
├── README.md
├── docs/
│   ├── overview.md
│   ├── architecture.md
│   └── roadmap.md
├── examples/
│   └── pipelines/
│       └── policy_labeling.yaml
├── config/
│   └── settings.example.yaml
├── openextract/
│   ├── __init__.py
│   ├── pipelines/
│   │   ├── __init__.py
│   │   └── base.py
│   └── providers/
│       ├── __init__.py
│       └── base.py
└── scripts/
    └── run_pipeline.py
```

## 快速开始

1. 克隆仓库并进入 `OpenExtract/` 目录。
2. 复制配置：`cp config/settings.example.yaml config/settings.yaml`，根据环境填写 API Key、并发、限流等参数。
3. 在 `examples/pipelines/` 中复制示例 YAML，调整 Excel 路径、提示词目录、Provider 选择等信息。
4. 运行占位版 CLI：`python scripts/run_pipeline.py --config examples/pipelines/policy_labeling.yaml`（即将迭代引入真正的流水线执行）。

## 与 PolicyKnowledgeBase 的关系

这是作者在构建政策数据库知识库集中找到的 OpenExtract 的灵感点。

- `PolicyKnowledgeBase` 继续承担具体政策标注任务。
- `OpenExtract` 萃取其中的共性能力（提示词执行、速率控制、实体合并、兜底策略等），对外提供标准化框架。
- 未来可以逐步把 `scripts/API.py` 拆分并迁移到 `openextract` 包内，形成统一的流水线引擎。

## 参考与灵感

- LangExtract：多 Provider 支持、JSONL+HTML 可视化、chunking 策略等。
- PolicyKnowledgeBase：经验证的多提示词流程、DeepSeek 内容风险处理、字段兜底逻辑。

## 下一步

查看 `docs/roadmap.md` 获取当前迭代计划。如果你愿意贡献或有新的需求，欢迎提交 issue/PR，一起打造通用的中文政策抽取框架。
