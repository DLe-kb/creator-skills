# XHS Viral Content Analysis 使用说明

`xhs-viral-content-analysis` 用于证据化解析一批小红书图文或视频内容。它帮助识别内容的信息任务、主要载体、路线差异、说服结构、价值转译与风险边界，不直接生成或发布新笔记。

## 适合的输入

- 图文：标题、封面、发布区正文、完整配图顺序，以及可用的标签、评论和互动字段。
- 视频：原视频或稳定来源，以及可用的音轨、转录、字幕、关键帧、页面正文、评论和互动字段。
- 每条样本应有稳定 ID，并说明来源、采集时间、媒体类型和缺失字段。

图文和视频应分批分析，避免把两种媒体的结构统计混在一起。

## 调用示例

```text
$xhs-viral-content-analysis 分析这批小红书图文笔记，识别主要信息载体、内容路线和说服结构，并输出单文件 HTML 报告和结构化 JSON。
```

```text
$xhs-viral-content-analysis 分析这批小红书视频，重点核读前 5 秒、画面文字、口播、同步字幕、镜头动作和声画关系。
```

## 输出

- `analysis-report.html`：面向人工阅读和审阅的单文件报告，证据图片内嵌，无网络资源依赖。
- `analysis-result.json`：保存稳定字段、证据引用、内容路线、价值转译和主张边界的机器结果。

HTML 是主要交付文件，JSON 用于复核、归档或按需交给其他流程，不能替代 HTML。

## 能力边界

- “爆款”只作为研究目标或样本标签，不构成流量、互动、转化或销售因果结论。
- 只有正向样本或缺少统一数据条件时，不能把共同特征解释为成功原因。
- 产品事实、个人体验、健康效果、成分机理和比较主张必须分开处理。
- 缺少完整成品、音轨、截图或关键字段时，报告必须明确降级或列出阻塞输入。
- Skill 不执行内容发布，也不代替人工确认产品主张、商业关系或素材权利。

## 本地验证

```bash
python3 skills/xhs-viral-content-analysis/scripts/test_validate_analysis_result.py
python3 skills/xhs-viral-content-analysis/scripts/test_validate_html_report.py
```

对具体结果包进行验证：

```bash
python3 skills/xhs-viral-content-analysis/scripts/validate_analysis_result.py analysis-result.json
python3 skills/xhs-viral-content-analysis/scripts/validate_html_report.py analysis-report.html
```
