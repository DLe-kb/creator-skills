# 综合结果契约

## 交付文件

- `synthesis-report.html`：主要人类交付，按 `synthesis-html-contract.md` 呈现。
- `synthesis-result.json`：机器伴随文件，遵循 `synthesis-result.schema.json`。

## 核心关系

`report_records` 保存参与综合的报告；`evidence_records` 保存从报告结论、原帖页面、配图或关键帧提取的综合证据；所有机制、路线、差异和边界通过 ID 回溯这两层资料。

每条 `observed_pattern` 共性至少由 2 份不同报告支持。每条 `cross_report_observed` 路线族至少由 2 份不同报告支持。相同样本在不同报告中重复出现时不得重复计算独立支持。

## 状态

- `complete`：至少 2 份可比较报告，核心结论可以回溯到稳定证据。
- `partial`：可以综合，但部分报告只有 HTML、状态为 `partial`、字段不完整或可比范围有限。
- `blocked`：不足 2 份可用报告，或报告之间没有可识别的共同研究问题。

## 结论类型

沿用 `source_fact`、`observed_pattern`、`analysis_inference`、`hypothesis` 和 `human_confirmed`。综合层不得把来源报告的结论自动升级；`partial` 或低置信来源不能在综合后变成高置信事实。

## 证据

`supporting_evidence_ids` 用于证明跨报告支持，通常应覆盖不同报告。`representative_evidence_ids` 用于 HTML 中展示代表案例，可以少于完整支持证据，但必须是 `supporting_evidence_ids` 的子集。

证据定位使用相对路径、稳定平台 ID 或公开 URL，不写分析者机器的绝对路径。外部公开候选必须保留来源分类，不能与企业样本合并标记。

## 校验

```bash
python3 scripts/validate_synthesis_result.py output/synthesis-result.json
```

校验器检查报告数、ID 唯一性、跨报告支持、证据引用、路线状态和本地绝对路径。它不能替代人工判断报告是否真的可比，也不能证明内容机制会带来流量或转化。
