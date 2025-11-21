# OpenExtract 快速测试指南

## 测试环境已就绪 ✓

测试用例已全部准备完毕，包含以下文件：

### 测试数据
- **Excel 文件**: `data/test/test_policies.xlsx`
  - 包含 3 条示例政策文档
  - 列：`Id`, `articleTitle`, `articleContent`

### 提示词
- **提示词文件**: `prompt/test/policy_extract.txt`
  - 提取：文档类型、主题领域、发文目的、关键措施

### 配置文件
- **Pipeline 配置**: `examples/pipelines/test_extraction.yaml`
  - 使用 DeepSeek-V3 模型
  - 输出到 `output/test_results/`

## 运行测试

### 1. 设置 API Key

```powershell
# Windows PowerShell
$env:SILICONFLOW_API_KEY = "sk-your-key-here"
```

### 2. 运行测试流水线

```bash
uv run python scripts/run_pipeline.py --config examples/pipelines/test_extraction.yaml
```

### 3. 查看结果

```bash
# JSON 格式（推荐用编辑器查看）
cat output/test_results/results.json

# JSONL 格式（逐行）
cat output/test_results/jsonl/results.jsonl
```

## 预期输出示例

```json
{
  "doc_id": "1",
  "title": "关于加强网络安全管理的通知",
  "structured_tags": {
    "policy_extract": {
      "文档类型": "通知",
      "主题领域": "网络安全",
      "发文目的": "加强网络安全管理",
      "关键措施": [
        "建立健全管理制度",
        "加强技术防护",
        "定期安全评估"
      ]
    }
  },
  "errors": []
}
```

## 故障排查

### 如果出现 API 错误
- 检查 `SILICONFLOW_API_KEY` 是否正确设置
- 确认 API 有足够的额度

### 如果出现文件找不到
- 确认当前目录是项目根目录 `OpenExtract/`
- 确认 `data/test/test_policies.xlsx` 已生成

### 如果想修改测试
- 编辑 `prompt/test/policy_extract.txt` 修改提示词
- 编辑 `examples/pipelines/test_extraction.yaml` 修改配置
- 运行 `uv run python scripts/generate_test_data.py` 重新生成测试数据

## 下一步

测试成功后，您可以：
1. 准备自己的 Excel 数据
2. 编写自己的提示词
3. 创建新的 pipeline 配置文件
4. 开始实际的抽取任务！
