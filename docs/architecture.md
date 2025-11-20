# OpenExtract Architecture

本文档描述 OpenExtract 的模块拆分、数据流程与主要扩展点，帮助贡献者快速理解框架意图。

## 模块划分

```
openextract/
├── pipelines/
│   ├── base.py          # 抽象 Pipeline 引擎，负责读取配置、调度步骤、聚合结果
│   └── registry.py?     # （规划中）管理可用 Pipeline/步骤实现
├── providers/
│   ├── base.py          # Provider Adapter 接口：鉴权、速率限制、请求/响应清洗
│   ├── siliconflow.py   # TBD
│   ├── deepseek.py      # TBD
│   └── gemini.py        # TBD
├── prompts/
│   └── loader.py        # 负责读取 prompt 目录、解析 `<index>. <label>.md`、拆分子提示词
├── io/
│   ├── readers.py       # Excel/CSV/JSON/自定义 Source 读取器
│   └── writers.py       # JSON/JSONL/HTML/S3 等输出
├── qc/
│   ├── visualizer.py    # 生成 HTML 质检页面（参考 LangExtract）
│   └── validators.py    # Schema 校验、兜底策略
└── utils/
    ├── chunking.py      # 长文分块、多 pass 逻辑
    └── logging.py       # 结构化日志、可观测性钩子
```

（目前 repo 中仅提交 `pipelines/base.py`、`providers/base.py` 骨架，其余模块将在后续迭代）

## 数据流

1. **Reader** 把数据源标准化为 `Article`/`Document` 对象，提供元数据（ID、标题、正文、附加字段）。
2. **Prompt Planner** 根据配置/提示词目录生成 `PromptUnit` 列表，包含所有执行参数（system/user prompt、schema、温度覆盖、重试策略）。
3. **Pipeline Engine** 逐个或并发执行 PromptUnit：
   - 为每个单元准备输入（如 `render_user_message`、历史提示结果）。
   - 调用 Provider Adapter 发送请求、处理重试、解析流式/非流式响应。
   - 根据 schema/兜底逻辑填补缺失字段，或触发 salvage/repair。
4. **Merger** 将多 PromptUnit 的结果按配置合并，例如 `实体关系` 的 4.1~4.4 重组、分类字段归一。
5. **Sink** 把结构化结果写入目标（JSON、JSONL、数据库等），并可同步触发 `qc.visualizer` 生成审阅页面。
6. **Metrics/Logs** 贯穿上述步骤，记录耗时、错误、重试、Content Risk 等信息。

## 扩展点

- **Provider Adapter**：只需实现 `prepare_request()`、`execute()`、`parse_response()`，即可接入新的 LLM 服务。
- **Prompt Parser**：支持 Markdown、YAML、甚至 LangExtract 风格的 Few-shot JSON；未来可加入“提示词包”概念。
- **Chunk Strategy**：引入策略模式，允许选择“固定长度切分”“段落感知切分”“检索增强”等。
- **Result Sink**：除了 JSON 以外，可以扩展到数据库、消息队列、PostgreSQL JSONB 等场景。

## 与现有项目的接口

- `PolicyKnowledgeBase`：未来可以把 `scripts/API.py` 拆成若干 `Pipeline Step`，直接运行在 OpenExtract 的 CLI 上。
- `LangExtract`：其 JSONL/HTML 可视化逻辑可作为 `qc.visualizer` 的实现参考，Provider 则可借鉴其 `Gemini`/`Ollama` 集成方式。

## 当前工作

- `pipelines/base.py`：提供一个最简骨架类，阐明需要实现的钩子与数据结构，便于贡献者并行开发。
- `providers/base.py`：定义 Adapter 抽象，明确我们期望 Provider 具备的功能（速率限制、思考模式配置等）。

更多细节请查阅 `docs/roadmap.md`，了解当前迭代的优先级和已有 issue。*** End Patch
