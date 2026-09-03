# 解析结果契约

## 交付文件

默认输出两个文件：

- `analysis-report.html`：主要人类交付。图文呈现组成、载体和正文变量；视频呈现时间轴、开场、画面文字、口播、声画关系和决策链。需要复刻时可增加可选复用附录。具体要求见 `html-report-contract.md`。
- `analysis-result.json`：机器伴随文件，遵循 `analysis-result.schema.json`。

文件名可以按用户项目规则调整，但 JSON 内部字段语义不得改变。不要在结果中写入密钥、令牌、Cookie 或完整凭证。

## JSON 的作用

JSON 不承担人的主要阅读和交付确认。它用于：

- 保存不会随页面排版变化的稳定字段。
- 维持样本 ID、证据 ID、路线 ID 和引用关系。
- 供程序读取路线、条件、风险和证据关系；有复刻需求时，也可供独立的下游内容生产 Skill 读取可复用部分。
- 通过校验器检查字段、枚举、唯一性和引用完整性。
- 支持后续样本验证时进行结构化差异比较。

HTML 与 JSON 应表达同一批事实和结论。HTML 负责可读性、证据展示和人工审阅；JSON 负责机器交接和确定性校验，二者不能互相替代。

## 共用单篇字段

每条 `sample_analyses` 必须包含：

- 用户任务、用户问题、产品角色和主要信息载体。
- 模块承接、说服节点、证据引用和限制。

## 图文单篇要求

`media_type=image_post` 时必须包含：

- `component_analysis`：标题、封面、开头钩子、正文、图片序列与主要载体、决策收口、证据与风险七项。
- `body_variables`：开场、痛点组织、产品进入、价值转译、体验细节、最终判断六项。
- `image_sequence_tasks`：图片序列的信息任务。

## 视频单篇要求

`media_type=video_post` 时必须包含 `video_analysis`：

- `content_promise`：视频向观众承诺完成的判断任务。
- `timeline_segments`：按信息任务变化切分的时间轴。
- `opening_analysis`：前 5 秒逐点观察，默认覆盖 0 至 5 秒的 0.5 秒检查点。
- `on_screen_copy_analysis`：画面文字分段及其文案任务、观众作用和认知变化。
- `voiceover_copy_analysis`：口播分段及其文案任务、观众作用和认知变化。
- `persuasion_chain`：观众决策链和节点前后变化。
- `audio_visual_summary` 与 `comment_signals`：声画分工和评论问题信号。

画面文字与口播至少一类必须有内容。无可辨识口播时保留空数组并在限制中说明，不得补造。

有复刻需求且路线准备度允许时，可在顶层增加 `replication_blueprints`，交接目标人群、开场字段、时间段任务、画面文字字段、口播字段、镜头职责、产品进入、异议收口、成立条件和失效条件。蓝图只复刻功能结构，不复制原作者表达。

`replication_blueprints` 与 `downstream_handoff` 均为可选字段。它们不存在时，JSON 仍可作为完整的独立分析结果；不得因此把 `analysis_status=complete` 降级。若存在，则必须继续满足路线引用、缺失输入和禁止假设约束。

字段描述真实样本中出现的组织关系。缺失内容使用空字符串或限制说明，不得补齐成理想模板。

## JSON 语义要求

### 状态

- `complete`：输入足以完成逐篇和跨样本解析。
- `partial`：可以完成部分解析，但样本、模块或证据缺失限制了结论。
- `blocked`：缺少可读取的完整成品，不能形成可靠解析。

### 路线状态

- `observed`：至少有多个可比较样本支持。
- `single_sample`：只有一个样本支持。
- `hypothesis`：主要由分析推断形成，等待新样本验证。

路线状态只描述分析证据，不表示可以直接用于生产。每条路线可以按需增加 `replication_readiness`：

- `ready`：现有证据与输入足以作为下游结构依据，但仍不等于效果保证。
- `conditional`：可以复用，但必须先补足 `blocking_inputs` 中的条件。
- `research_only`：保留研究价值，不应进入推荐复刻路线，也不应生成复刻蓝图。

`blocking_inputs` 是可选字符串数组；当 `replication_readiness=conditional` 时必须非空。旧结果未提供准备度字段时保持兼容，但不能据此推定为 `ready`。

### 结论类型

使用 `source_fact`、`observed_pattern`、`analysis_inference`、`hypothesis` 或 `human_confirmed`。只有存在明确人工确认记录时才使用 `human_confirmed`。

### 证据引用

- `evidence_records[].evidence_id` 在一个结果包内唯一。
- `evidence_records[].sample_id` 必须引用 `analysis_scope.included_sample_ids` 中的纳入样本。批次级限制写入 `analysis_scope.limitations`，不要虚构批次样本 ID。
- 所有 `evidence_ids` 必须引用已存在的证据记录。
- `supporting_sample_ids` 必须来自纳入样本。
- `locator` 应采用相对于输入根目录的相对位置、平台记录 ID 或稳定 URL；不要为了迁移方便而写入分析者机器的绝对路径。

### 路线字段

每条路线必须明确：用户任务、核心张力、主要信息载体、产品位置与角色、使用前提。另行记录支持样本、不适用条件、模块承接、说服节点、反例、置信程度和限制。

## 可选下游接口

只有在用户需要复刻，或分析结果确有明确复用价值时，才生成 `replication_blueprints` 和 `downstream_handoff`。下游接口是附加能力，不是解析报告成立或完成的前提。

- `recommended_route_ids` 不得包含 `research_only` 路线。
- `conditional` 路线进入推荐列表前，必须明确非空的 `blocking_inputs`。
- `missing_inputs` 与 `prohibited_assumptions` 必须如实传递证据、合规、素材和业务缺口。
- 下游可以选择不消费这些字段；解析结论仍应能被独立阅读、审计和继续研究。

## 校验

在技能目录中运行：

```bash
python3 scripts/validate_analysis_result.py output/analysis-result.json
```

校验器检查结构、枚举、ID 唯一性、证据归属和引用完整性。JSON Schema 负责静态字段形状，无法单独表达证据样本 ID 与动态纳入样本数组之间的成员关系，因此该跨字段约束由校验器执行。两者都不能证明分析判断正确，也不能替代人工证据审查。
