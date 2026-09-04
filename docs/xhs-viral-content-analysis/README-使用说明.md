# XHS Viral Content Analysis 使用说明

`xhs-viral-content-analysis` 支持两种独立任务：分析一批小红书原始图文或视频笔记；综合多份已经完成的内容分析报告。它以可回溯证据为基础识别内容机制、路线、差异与边界，不直接生成或发布新笔记。

## 工作流选择

### 单批内容解析

适用于用户要求分析一条或一批原始笔记、拆解图文或视频结构、识别单批内容路线的任务。

图文输入应尽量包含标题、封面、发布区正文、完整配图顺序，以及可用的标签、评论和互动字段。视频输入应尽量包含原视频或稳定来源，以及可用的音轨、转录、字幕、关键帧、页面正文、评论和互动字段。

每条样本应有稳定 ID，并说明来源、采集时间、媒体类型和缺失字段。图文和视频应分批分析，避免把两种媒体的结构统计混在一起。

### 跨报告综合

适用于用户明确要求从多份既有报告中总结共性、比较差异、提炼综合框架或生成综合报告的任务。自然语言提出上述目标即可触发，不要求固定命令。

跨报告综合至少需要两份能够回溯研究范围和证据的分析报告。只有 HTML、缺少结构化结果时可以降级综合，但必须记录字段缺口。文件数量多本身不构成综合任务；用户没有提出跨报告归纳目标时，不自动启动该工作流。

## 调用示例

单批图文解析：

```text
$xhs-viral-content-analysis 分析这批小红书图文笔记，识别主要信息载体、内容路线和说服结构，并输出单文件 HTML 报告和结构化 JSON。
```

单批视频解析：

```text
$xhs-viral-content-analysis 分析这批小红书视频，重点核读前 5 秒、画面文字、口播、同步字幕、镜头动作和声画关系。
```

跨报告综合：

```text
$xhs-viral-content-analysis 综合这几份已经完成的小红书内容分析报告，提炼反复出现的内容机制、内容路线、媒体与产品差异，并生成综合 HTML 报告和结构化 JSON。
```

## 输出

单批内容解析：

- `analysis-report.html`：面向人工阅读和审阅的单文件报告，证据图片内嵌，无网络资源依赖。
- `analysis-result.json`：保存稳定字段、证据引用、内容路线、价值转译和主张边界的机器结果。

跨报告综合：

- `synthesis-report.html`：面向内容团队的综合分析报告，呈现共性机制、开放路线、差异、诊断问题与适用边界。
- `synthesis-result.json`：保存来源报告、跨报告证据映射、共性机制、路线及结论等级的机器结果。

HTML 是主要交付文件，JSON 用于复核、归档或按需交给其他流程，不能替代 HTML。

## 能力边界

- “爆款”只作为研究目标或样本标签，不构成流量、互动、转化或销售因果结论。
- 只有正向样本或缺少统一数据条件时，不能把共同特征解释为成功原因。
- 跨报告共性必须由至少两份来源报告支持，不能用同一报告内的重复代替跨报告重复。
- 代表截图用于帮助理解，来源映射用于证明共性，二者不能互相替代。
- 产品事实、个人体验、健康效果、成分机理和比较主张必须分开处理。
- 缺少完整成品、音轨、截图或关键字段时，报告必须明确降级或列出阻塞输入。
- Skill 不执行内容发布，也不代替人工确认产品主张、商业关系或素材权利。

## 本地验证

运行全部校验器测试：

```bash
python3 skills/xhs-viral-content-analysis/scripts/test_validate_analysis_result.py
python3 skills/xhs-viral-content-analysis/scripts/test_validate_html_report.py
python3 skills/xhs-viral-content-analysis/scripts/test_validate_synthesis_result.py
python3 skills/xhs-viral-content-analysis/scripts/test_validate_synthesis_html.py
```

验证具体结果包：

```bash
python3 skills/xhs-viral-content-analysis/scripts/validate_analysis_result.py analysis-result.json
python3 skills/xhs-viral-content-analysis/scripts/validate_html_report.py analysis-report.html
python3 skills/xhs-viral-content-analysis/scripts/validate_synthesis_result.py synthesis-result.json
python3 skills/xhs-viral-content-analysis/scripts/validate_synthesis_html.py synthesis-report.html
```
