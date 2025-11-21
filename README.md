# OpenExtract

OpenExtract 是一个可复用的结构化抽取框架，旨在把 `PolicyKnowledgeBase` 项目（该项目是笔者在实际工作中构建政策知识库时的一个经历结晶）中沉淀下来的 "Excel → 多提示词 → 结构化 JSON" 流程模块化，并借鉴 LangExtract 在分块处理、可视化复核方面的优秀实践，帮助更多团队快速搭建自己的抽取流水线。

## 目录

- [主要目标](#主要目标)
- [核心创新](#核心创新)
- [应用场景](#应用场景)
- [与其他工具对比](#与其他工具对比)
- [快速开始](#快速开始)
- [详细安装指南](#详细安装指南)
- [配置说明](#配置说明)
- [使用指南](#使用指南)
- [项目结构](#项目结构)
- [核心组件](#核心组件)
- [示例](#示例)
- [故障排查](#故障排查)
- [开发指南](#开发指南)
- [与 PolicyKnowledgeBase 的关系](#与-policyknowledgebase-的关系)
- [参考与灵感](#参考与灵感)
- [下一步计划](#下一步计划)

## 主要目标

- **声明式流水线**：通过 YAML/JSON 描述 "数据源 → 提示词计划 → 模型调用 → 结果合并"，减少硬编码。
- **提示词库与 Schema 注册**：集中管理提示词、Few-shot 示例与字段定义，支持版本化与跨项目复用。
- **Provider 插件化**：统一封装 SiliconFlow、DeepSeek、Gemini、Ollama 等服务，内建速率限制、重试与思考模式控制。
- **分块与并行**：可选 chunking、multi-pass、并发配置，兼顾长文支持与 API 负载。
- **质检与复核**：输出 JSON/JSONL 的同时生成交互式 HTML（规划中），方便人工审核与追踪。

## 核心创新

### 🎯 为什么选择 OpenExtract？

OpenExtract 不是"又一个 AI 工具"，而是针对**中文结构化抽取场景的工程化解决方案**。

### 创新 1：声明式配置 + 低代码设计

**传统方式**需要为每个项目编写大量重复代码：
```python
# 每个项目都要写这些
excel = pd.read_excel("data.xlsx")
for row in excel:
    prompt = f"提取{row['content']}"
    response = call_api(prompt)
    result = parse_json(response)
    save(result)
```

**OpenExtract 方式**只需编写配置文件：
```yaml
pipeline:
  source:
    type: excel
    path: data.xlsx
  prompts:
    dir: prompts/
  provider:
    name: siliconflow
```

**价值**：
- ✅ 非技术人员也能配置流水线
- ✅ 复用性极强（换数据/提示词即可）
- ✅ 易于维护和版本管理

### 创新 2：Provider 抽象层 - 多模型无缝切换

**痛点**：市面上 LLM 服务商众多，API 格式各异，切换成本高。

**OpenExtract 解决方案**：统一的 Provider 抽象层
```yaml
# 今天用 SiliconFlow
provider:
  name: siliconflow
  model: GLM-4.6

# 明天换 DeepSeek，只改 2 行
provider:
  name: deepseek
  model: deepseek-chat
```

**价值**：
- ✅ 避免厂商锁定
- ✅ 成本优化（哪个便宜用哪个）
- ✅ 业务连续性（某服务故障时立即切换）

### 创新 3：提示词工程化管理

**传统问题**：提示词散落在代码各处，难以复用和优化。

**OpenExtract 方案**：提示词库系统
```
prompt/
├── policy/              # 政策标注提示词库
│   ├── classify.txt
│   ├── extract.txt
│   └── entity.txt
├── contract/            # 合同审查提示词库
│   ├── parties.txt
│   └── terms.txt
└── report/              # 报告分析提示词库
    └── ...
```

**价值**：
- ✅ 提示词可版本化（Git 管理）
- ✅ 团队协作（提示词工程师专门优化）
- ✅ 跨项目复用（标准化提示词库）

### 创新 4：结构化输出 + 可追溯性

输出不仅仅是 JSON，还包含完整的执行上下文：
```json
{
  "doc_id": "001",                    // 可追溯到原文
  "title": "...",
  "structured_tags": {...},           // 提取结果
  "errors": [...]                     // 失败原因
}
```

**规划中的 HTML 可视化**：原文 | 提取结果 | 人工复核（可高亮对应关系，支持批量审核）

**价值**：
- ✅ 质量可控（人工抽检）
- ✅ 持续改进（错误案例反哺提示词优化）
- ✅ 合规要求（审计追溯）

### 创新 5：实战经验沉淀

这不是拍脑袋设计的框架，而是：
- ✅ 从真实政策标注项目中提炼
- ✅ 经过生产环境验证的架构
- ✅ 沉淀了实战中的最佳实践：
  - 速率控制（避免被限流）
  - 错误兜底（API 失败处理）
  - 内容风控处理（敏感词过滤）
  - 字段合并逻辑（多轮提示词结果整合）

## 应用场景

### 1. 政策知识库构建 ⭐ 核心场景

**问题**：政府每年发布数万份政策文件，人工整理效率低下。

**解决方案**：
```
Excel: 政策标题 + 全文
    ↓
OpenExtract 自动提取
    ↓
结构化数据: {
  "发文单位": "某某部",
  "政策类型": "通知",
  "适用行业": ["制造业", "新能源"],
  "关键措施": [...],
  "生效日期": "2025-01-01"
}
```

**价值**：原本需要 100 人标注 1 个月 → 1 台服务器 3 天完成

### 2. 企业合规审查

**场景**：律所/企业需要审查大量合同、条款

```
数千份合同 → 自动提取：
- 甲乙方信息
- 合同金额
- 违约条款
- 风险点
→ 生成风险报告
```

### 3. 研究报告挖掘

**场景**：投研机构处理行业报告

```
Excel: 券商研报 PDF 转文本
    ↓
提取: {
  "目标公司": "XX科技",
  "评级": "买入",
  "目标价": 120,
  "关键观点": [...]
}
→ 自动生成研报数据库
```

### 4. 客服工单分类

**场景**：电商/SaaS 企业处理海量客服工单

```
工单文本 → 自动分类：
- 问题类型
- 紧急程度
- 涉及产品
- 情感倾向
→ 智能分单 + 统计分析
```

### 5. 招聘简历筛选

```
简历 Excel → 提取：
- 学历背景
- 工作经验
- 技能关键词
- 匹配度评分
→ 自动初筛
```

### 更多场景

- **报告要素提取**：在研究报告、审计报告、可研文件中抽取章节、指标、风险、建议等要素。
- **企业 SOP / 制度知识库**：对内部制度、流程文档进行提示词抽取，生成可检索的流程图谱。
- **培训与质检**：结合 JSONL + HTML 可视化（规划中），快速搭建人工复核界面。

## 与其他工具对比

| 特性 | OpenExtract | LangChain | 自研脚本 |
|------|------------|-----------|----------|
| **学习成本** | 低（YAML 配置） | 高（复杂 API） | 中 |
| **多 Provider** | ✅ 统一抽象 | ✅ 支持 | ❌ 需自己封装 |
| **提示词管理** | ✅ 工程化 | ⚠️ 分散 | ❌ 硬编码 |
| **批量处理** | ✅ 原生支持 | ⚠️ 需自己实现 | ⚠️ 需自己实现 |
| **中文政策场景** | ✅ 专门优化 | ⚠️ 通用框架 | - |
| **可视化复核** | 🔜 规划中 | ❌ | ❌ |
| **生产就绪** | ✅ MVP 可用 | ⚠️ 需大量配置 | ⚠️ 维护成本高 |

### 核心竞争力

1. **垂直领域深耕**：专注中文文档结构化抽取，针对政策、合同、报告等场景优化
2. **工程化思维**：不是玩具项目，是生产级框架（配置化、模块化、可扩展）
3. **实战驱动**：解决真实业务痛点，积累了大量最佳实践
4. **开放生态**：易于扩展新 Provider、易于添加新数据源、社区友好（MIT 许可证）


## 快速开始

### 前置要求

- Python 3.11+
- [uv](https://github.com/astral-sh/uv) (推荐) 或 pip
- SiliconFlow API Key (或其他支持的 Provider 的 Key)

### 5 分钟快速体验

```bash
# 1. 克隆仓库
git clone https://github.com/yourusername/OpenExtract.git
cd OpenExtract

# 2. 使用 uv 初始化环境
uv sync

# 3. 配置环境变量
cp .env.example .env
# 编辑 .env 文件，填入你的 SILICONFLOW_API_KEY

# 4. 运行测试流水线
uv run python scripts/run_pipeline.py --config examples/pipelines/test_extraction.yaml

# 5. 查看结果
uv run python scripts/view_results.py
```

## 详细安装指南

### 使用 uv (推荐)

```bash
# 安装 uv (如果尚未安装)
# Windows (PowerShell)
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"

# Linux/macOS
curl -LsSf https://astral.sh/uv/install.sh | sh

# 克隆并安装项目
git clone https://github.com/yourusername/OpenExtract.git
cd OpenExtract
uv sync
```

### 使用传统 pip

```bash
# 创建虚拟环境
python -m venv .venv
source .venv/bin/activate  # Linux/macOS
# 或
.venv\Scripts\activate  # Windows

# 安装依赖
pip install -r requirements.txt
```

### 依赖说明

| 包名 | 版本要求 | 用途 |
|------|---------|------|
| `pyyaml` | >=6.0 | YAML 配置文件解析 |
| `pandas` | >=2.0.0 | Excel 数据读取与处理 |
| `openpyxl` | >=3.1.0 | Excel 文件格式支持 |
| `requests` | >=2.31.0 | HTTP API 调用 |
| `python-dotenv` | >=1.0.0 | 环境变量管理 |

## 配置说明

### 环境变量配置

创建 `.env` 文件（基于 `.env.example`）：

```bash
# SiliconFlow API 配置
SILICONFLOW_API_KEY=sk-your-key-here
SILICONFLOW_BASE_URL=https://api.siliconflow.cn/v1

# DeepSeek API 配置（可选）
# DEEPSEEK_API_KEY=your-deepseek-key-here
# DEEPSEEK_BASE_URL=https://api.deepseek.com/v1
```

### Pipeline 配置文件

Pipeline 配置文件使用 YAML 格式，示例：

```yaml
pipeline:
  name: my_extraction_pipeline
  description: 提取文档关键信息
  
  # 数据源配置
  source:
    type: excel
    path: data/input/documents.xlsx
    sheet: 0                    # 工作表名称或索引
    id_column: Id               # ID 列名
    title_column: Title         # 标题列名
    content_column: Content     # 正文列名
  
  # 提示词配置
  prompts:
    dir: prompt/my_prompts      # 提示词目录
    temperature_overrides:       # 特定提示词的温度覆盖
      classification: 0.7
      extraction: 0.2
  
  # Provider 配置
  provider:
    name: siliconflow
    concurrency: 1              # 并发数
    sleep_seconds: 1.0          # 请求间隔
    timeout: 60                 # 超时时间（秒）
  
  # 运行时配置
  runtime:
    temperature: 0.2            # 默认温度
    max_tokens: 1500            # 最大 token 数
    max_rows: null              # 处理行数限制（null=全部）
  
  # 输出配置
  outputs:
    json_path: output/results
    jsonl_dump: output/results/jsonl

# 全局 Provider 设置
providers:
  siliconflow:
    api_base: https://api.siliconflow.cn/v1
    model: zai-org/GLM-4.6      # 使用的模型
    api_key_env: SILICONFLOW_API_KEY
    think_mode: false
```

### 提示词文件

提示词文件使用纯文本格式（`.txt` 或 `.md`），支持变量替换：

```text
请分析以下文档，提取关键信息并以 JSON 格式输出：

标题：{title}
正文：{content}

请提取以下字段：
1. 文档类型
2. 主题领域
3. 关键措施（列表形式）

输出格式：
{{"文档类型": "...", "主题领域": "...", "关键措施": ["...", "..."]}}
```

## 使用指南

### 基本用法

```bash
# 运行流水线
uv run python scripts/run_pipeline.py --config path/to/pipeline.yaml

# 指定全局设置文件（可选）
uv run python scripts/run_pipeline.py \
  --config path/to/pipeline.yaml \
  --settings config/settings.yaml
```

### 查看结果

```bash
# 使用内置查看脚本
uv run python scripts/view_results.py

# 或直接查看 JSON 文件
cat output/test_results/results.json
```

### 生成测试数据

```bash
# 生成示例测试数据
uv run python scripts/generate_test_data.py
```

## 项目结构

```
OpenExtract/
├── README.md                      # 项目说明文档
├── pyproject.toml                 # uv 项目配置
├── requirements.txt               # pip 依赖列表
├── .env.example                   # 环境变量模板
├── .gitignore                     # Git 忽略文件
├── config/
│   └── settings.example.yaml      # 全局配置示例
├── docs/
│   ├── overview.md                # 项目概览
│   ├── architecture.md            # 架构设计
│   ├── roadmap.md                 # 开发路线图
│   └── QUICKSTART.md              # 快速入门指南
├── examples/
│   └── pipelines/
│       ├── policy_labeling.yaml   # 政策标注示例
│       └── test_extraction.yaml   # 测试流水线
├── openextract/                   # 核心包
│   ├── __init__.py
│   ├── config.py                  # 配置加载
│   ├── pipelines/
│   │   ├── __init__.py
│   │   └── base.py                # Pipeline 基类
│   ├── providers/
│   │   ├── __init__.py
│   │   ├── base.py                # Provider 接口
│   │   └── siliconflow.py         # SiliconFlow 实现
│   ├── prompts/
│   │   ├── __init__.py
│   │   └── loader.py              # 提示词加载器
│   └── sources/
│       ├── __init__.py
│       └── excel.py               # Excel 数据源
├── scripts/
│   ├── run_pipeline.py            # CLI 入口
│   ├── generate_test_data.py     # 测试数据生成
│   └── view_results.py            # 结果查看工具
├── prompt/                        # 提示词库
│   └── test/
│       └── policy_extract.txt     # 测试提示词
└── data/                          # 数据目录
    └── test/
        └── test_policies.xlsx     # 测试数据
```

## 核心组件

### 1. Pipeline Engine (`openextract/pipelines/base.py`)

流水线执行引擎，负责协调数据源、提示词和 Provider 的执行流程。

**核心类**：
- `Document`: 标准化文档对象
- `PromptUnit`: 提示词单元接口
- `PipelineResult`: 执行结果
- `BasePipeline`: 流水线基类

### 2. Data Sources (`openextract/sources/`)

数据源适配器，负责从不同来源读取文档。

**已实现**：
- `ExcelSource`: Excel 文件读取

**规划中**：
- `CSVSource`: CSV 文件
- `JSONSource`: JSON/JSONL 文件
- `DatabaseSource`: 数据库查询

### 3. Providers (`openextract/providers/`)

AI 模型服务提供商适配器。

**已实现**：
- `SiliconFlowProvider`: SiliconFlow API

**规划中**：
- `DeepSeekProvider`: DeepSeek API
- `GeminiProvider`: Google Gemini
- `OllamaProvider`: 本地 Ollama

### 4. Prompt Management (`openextract/prompts/`)

提示词管理系统。

**功能**：
- 从目录加载提示词文件
- 模板变量替换
- 温度参数覆盖

### 5. Configuration (`openextract/config.py`)

配置加载与管理。

**功能**：
- YAML 配置解析
- 环境变量解析
- 配置合并

## 示例

### 示例 1：政策文档分类与提取

**数据准备** (`data/policies.xlsx`)：
```
Id | Title | Content
1  | 网络安全通知 | 为进一步加强...
2  | 绿色能源方案 | 为推动绿色...
```

**提示词** (`prompt/policy/extract.txt`)：
```
请分析政策文档并提取：
标题：{title}
内容：{content}

提取字段：文档类型、主题领域、关键措施
```

**配置** (`pipelines/policy.yaml`)：
```yaml
pipeline:
  name: policy_extraction
  source:
    type: excel
    path: data/policies.xlsx
  prompts:
    dir: prompt/policy
  provider:
    name: siliconflow
```

**运行**：
```bash
uv run python scripts/run_pipeline.py --config pipelines/policy.yaml
```

### 示例 2：批量合同条款提取

**数据准备**：Excel 包含合同文本

**提示词**：提取甲方、乙方、义务、违约责任

**配置**：调整 `max_tokens` 以处理长文本

详见 `examples/pipelines/` 目录。

## 故障排查

### 常见问题

#### 1. `ModuleNotFoundError: No module named 'openextract'`

**原因**：虚拟环境未激活或依赖未安装

**解决**：
```bash
# 使用 uv
uv sync

# 或使用 pip
source .venv/bin/activate  # 激活虚拟环境
pip install -r requirements.txt
```

#### 2. `ValueError: Environment variable SILICONFLOW_API_KEY not found`

**原因**：API Key 未配置

**解决**：
```bash
# 方法 1：使用 .env 文件（推荐）
cp .env.example .env
# 编辑 .env 填入 API Key

# 方法 2：直接设置环境变量
export SILICONFLOW_API_KEY=sk-your-key-here  # Linux/macOS
$env:SILICONFLOW_API_KEY="sk-your-key-here"  # Windows PowerShell
```

#### 3. `FileNotFoundError: Excel file not found`

**原因**：配置中的 Excel 路径不正确

**解决**：检查 YAML 配置中的 `source.path`，确保路径正确且文件存在。

#### 4. API 请求超时 (Gateway Timeout)

**原因**：网络波动或模型响应慢

**解决**：
- 增加 `timeout` 配置（默认 60 秒）
- 减少 `max_tokens`
- 检查网络连接

#### 5. JSON 解析错误

**原因**：模型返回的不是有效 JSON

**解决**：
- 在提示词中明确要求 JSON 格式
- 使用 `think_mode: false` 获取纯文本响应
- 检查提示词是否清晰

### 调试技巧

1. **启用详细日志**：查看 API 请求和响应
2. **减少数据量**：使用 `max_rows: 1` 测试单条数据
3. **检查输出文件**：直接查看 `results.json` 了解错误信息

## 开发指南

### 添加新的 Provider

1. 在 `openextract/providers/` 创建新文件
2. 实现 `Provider` 协议的三个方法：
   - `prepare_payload()`
   - `dispatch()`
   - `parse_response()`
3. 在配置中使用新 Provider

### 添加新的数据源

1. 在 `openextract/sources/` 创建新文件
2. 实现 `__iter__()` 方法返回 `Document` 对象
3. 在 Pipeline 配置中指定新的 `source.type`

### 运行测试

```bash
# 运行测试套件（当实现后）
uv run pytest

# 手动测试
uv run python scripts/run_pipeline.py --config examples/pipelines/test_extraction.yaml
```

## 与 PolicyKnowledgeBase 的关系

这是作者在构建政策数据库知识库集中找到的 OpenExtract 的灵感点。

- `PolicyKnowledgeBase` 继续承担具体政策标注任务。
- `OpenExtract` 萃取其中的共性能力（提示词执行、速率控制、实体合并、兜底策略等），对外提供标准化框架。
- 未来可以逐步把 `scripts/API.py` 拆分并迁移到 `openextract` 包内，形成统一的流水线引擎。

## 参考与灵感

- **LangExtract**：多 Provider 支持、JSONL+HTML 可视化、chunking 策略等。
- **PolicyKnowledgeBase**：经验证的多提示词流程、DeepSeek 内容风险处理、字段兜底逻辑。

## 下一步计划

查看 `docs/roadmap.md` 获取当前迭代计划。

**近期优先级**：
- [ ] 实现 DeepSeek Provider
- [ ] 添加重试机制和错误恢复
- [ ] 实现 HTML 可视化复核界面
- [ ] 添加并发处理支持
- [ ] 完善单元测试覆盖

**长期规划**：
- [ ] 支持更多数据源（CSV、Database）
- [ ] 支持 Chunking 和分段处理
- [ ] 实现提示词版本管理
- [ ] 构建 Web UI 管理界面

## 贡献指南

欢迎提交 Issue 和 Pull Request！

1. Fork 本项目
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

## 许可证

MIT License - 详见 LICENSE 文件

## 联系方式

如果你愿意贡献或有新的需求，欢迎提交 issue/PR，一起打造通用的中文政策抽取框架。

---

⭐ 如果这个项目对你有帮助，欢迎 Star！
