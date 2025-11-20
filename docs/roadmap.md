# OpenExtract Roadmap

## Q1：基础骨架

- [x] 初始化仓库结构与文档（README、overview、architecture、roadmap）。
- [ ] 完成 `pipelines.base` 的可运行实现，支持最小 Excel→Prompt→JSON 流。
- [ ] 实现 `providers.siliconflow`、`providers.deepseek`，包含速率限制、Content Risk 处理、思考模式开关。
- [ ] 搭建 `scripts/run_pipeline.py` CLI，支持 `--config` 指向 YAML。
- [ ] 提供 `config/settings.example.yaml`、`examples/pipelines/policy_labeling.yaml` 的解释文档。

## Q2：增强能力

- [ ] 引入 Prompt Registry：支持从目录加载 `<index>. <label>.md` 及子提示词。
- [ ] 支持 chunking/multi-pass 策略，处理超长政策/报告（参考 LangExtract 做法）。
- [ ] 增加 JSONL 输出与 HTML 可视化（质检视图）。
- [ ] Metrics/Logging 归一化，支持 Prometheus/OTEL Hook。
- [ ] 完成单元/集成测试框架，覆盖 Provider 模拟、Prompt Parser、Merger。

## Q3：生态扩展

- [ ] 引入更多 Provider（Gemini、Ollama、本地推理服务），并提供社区贡献模板。
- [ ] 支持 Label Studio/Doccano 等外部标注平台的输出格式。
- [ ] 打通 `PolicyKnowledgeBase`，实现“现有流水线迁移到 OpenExtract”的示例指南。
- [ ] 发布首个 pip 包或 Docker 镜像，方便 CI/CD 集成。

## 未决问题

- Prompt 版本管理策略：是否引入 Git 子模块或包管理。
- HTML 可视化的技术选型（纯静态 vs. 依赖前端框架）。
- 如何在多 Provider 混用时共享速率限制与重试策略。

欢迎在 issue 中提出新的需求或补充路线，如果你正在实现其中某个模块，请提前认领，避免重复劳动。*** End Patch
