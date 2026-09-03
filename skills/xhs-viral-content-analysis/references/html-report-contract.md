# HTML 分析报告契约

## 定位

`analysis-report.html` 是面向用户阅读、审阅和交付确认的主要文件。JSON 只能作为机器伴随文件，不能替代 HTML。

HTML 主体必须作为独立内容研究报告成立。用户即使不启动复刻，也应能仅凭主体理解样本、证据、内容机制、路线差异、说服结构和结论边界。复刻准备度、复用蓝图和下游交接只能作为可选附录，不得成为报告完成条件。

## 文件要求

- 输出单个 HTML 文件，使用 `<!doctype html>`、`lang="zh-CN"` 和 UTF-8。
- CSS 和必要的 JavaScript 全部内嵌，不引用 CDN、在线字体、外部样式表或外部脚本。
- 正式交付中的证据图片使用 `data:` URI 内嵌。不得引用本机绝对路径、`file://` 或只有分析者机器存在的相对素材目录。
- 页面在桌面和手机宽度均可阅读，不出现正文横向滚动、文字遮挡或表格溢出。
- 证据图片提供清晰说明；图片较多时允许折叠，图片应支持点击放大。
- 页面直接呈现分析对象、证据和结论，不把制作过程或工具说明写进报告。
- 必须遵守 [审计报告视觉系统](html-report-visual-system.md)。除非用户明确要求新设计，不得更换为另一套报告主题。

## 稳定板式标记

为避免只满足章节字段但生成不同板式，HTML 必须包含以下机器可读标记：

- 图文使用 `<body data-report-template="xhs-image-post-audit">`。
- 视频使用 `<body data-report-template="xhs-video-post-audit">`。
- `data-report-part="navigation"`
- `data-report-part="audit-hero"`
- `data-report-part="audit-meta"`
- `data-report-part="executive-summary"`
- `data-report-part="evidence-gallery"`
- `data-report-part="lightbox"`

这些标记分别对应顶部导航、审计首屏、审计元信息、首屏核心结论、逐篇证据区域和图片放大容器。`executive-summary` 仅是稳定机器标记，可见标题必须写“核心结论”，不得显示“执行摘要”。不得用空节点或隐藏节点应付校验。

核心分析还必须包含不少于 4 个 `data-evidence-group` 结论证据组，并包含相应的非空 `data-evidence-source`。证据组应分布在核心发现、组成要素、主要载体、内容路线或说服结构中，而不是全部集中在末尾逐篇证据章节。

## 标准模板资产与固定组件

生成报告时必须按媒体类型复制 `assets/XHS-Image-Post-Audit-Template.html` 或 `assets/XHS-Video-Post-Audit-Template.html`，再替换占位内容。两种模板的页面骨架不是视觉参考，而是同一实现契约。

以下核心组件必须沿用原 DOM 语义和 CSS 类名：

- 页面与章节：`.topbar`、`.topbar-inner`、`.topnav`、`.section`、`.wrap`、`.section-heading`。
- 审计首屏：`.hero`、`.hero-copy`、`.audit-meta`、`.hero-conclusion`、`.hero-summary-grid`。
- 结论证据组：`.finding-grid` → `.finding-copy` → `.finding-points`，随后同组内使用 `.evidence-stack` → `figure.evidence`。
- 路线与逐篇证据：`.route-list`、`.route`、`.case-list`、`.case`、`.case-header`、`.case-metrics`、`.case-layout`、`.full-shot`、`.case-analysis`、`.case-line`、`details.gallery`、`.image-strip`。
- 风险边界：`.limit-grid`。

每个 `data-evidence-group` 至少包含：

1. 一个 `.finding-copy`，其中包含非空标题、说明和 `.finding-points`。
2. `.finding-points` 中 2 至 4 个 `.finding-point`，用于展示结论维度、适用范围或边界。
3. 一个 `.evidence-stack`，其中至少包含一个 `figure.evidence`。
4. 每个 `figure.evidence` 使用非空 `data-evidence-source`，包含原帖图片和解释“图片支持什么判断”的图注。

不得创建 `.evidence-led`、`.evidence-led-head`、`.evidence-cards`、`.evidence-card`、`.evidence-slot` 等平行组件来模拟相近外观。若标准组件不能表达新增内容，应扩展标准组件本身，并同步更新模板资产、契约和校验器。

逐篇证据卡片固定沿用模板 3 的层级：

1. `.case-header` 左侧使用原帖标题作为主标题，副标题展示作者、内容类型和所属路线；右侧 `.case-metrics` 分项展示互动快照与配图数。
2. `.case-layout` 左侧 `.full-shot` 展示完整页面，右侧 `.case-analysis` 默认使用“标题、正文、图片、风险”4 行。可以根据样本语义调整单行名称，但不得退回“样本编号 + 七项组成 + 正文六变量”的另一套卡片版式。
3. 原始配图使用 `details.gallery` 折叠，并在 `.image-strip` 中保持原始顺序与图注。
4. 不得使用 `.case-title`、`.case-body`、`.page-shot` 等旧平行类名重建相似组件。

## 图文必需章节

使用以下稳定属性标记章节，便于校验和下游处理：

1. `data-section="scope"`：分析对象、目标、纳入、排除、缺失字段和数据时点。
2. `data-section="findings"`：核心发现，区分共性、路线差异、单样本结论和未验证范围。
3. `data-section="components"`：标题、封面、开头钩子、正文、图片序列与主要载体、决策收口、证据与风险七项组成分析。
4. `data-section="carriers"`：每篇及每条路线的主要信息载体与模块分工。
5. `data-section="routes"`：路线的用户任务、核心张力、主要载体、产品位置与角色、使用前提，以及支持样本和限制。
6. `data-section="persuasion"`：正文六变量、模块承接、可选说服节点和价值转译。
7. `data-section="evidence"`：逐篇完整成品证据、图片顺序、证据 ID、反例和主张上限。
8. `data-section="limits"`：当前证据支持什么、不支持什么、需要补充什么。

章节可以按阅读逻辑调整顺序，也可以增加目录、指标快照或附录，但不得删除必需章节。

## 视频必需章节

视频使用以下稳定属性：

1. `data-section="scope"`：样本、视频资产、缺失字段、表现数据口径和时点。
2. `data-section="findings"`：关键结论、路线差异、单样本结论和未验证范围。
3. `data-section="decision"`：观众决策链及节点前后的认知变化。
4. `data-section="screen-copy"`：画面文字原文或准确摘要、文案任务、观众作用、声画配合和风险。
5. `data-section="voiceover"`：口播原文或准确摘要、说服任务、观众变化、声画配合和风险。无可辨识口播时保留章节并如实说明。
6. `data-section="opening"`：前 5 秒逐点核读和继续观看理由。
7. `data-section="carriers"`：画面文字、口播、同步字幕、视觉序列、音乐或环境声的分工。
8. `data-section="routes"`：内容路线、适用条件、不适用条件、证据状态和限制。
9. `data-section="persuasion"`：产品进入、信任建立、异议处理、选择收口和声画关系。
10. `data-section="evidence"`：逐条视频关键帧、时间码、证据 ID、评论信号和主张上限。
11. `data-section="limits"`：支持、不支持和待补充证据。

视频报告还必须包含 `.timeline-wrap`、`.timeline` 和 `.av-grid`。这些是同一视觉系统内的内容组件，不得另建独立主题。

## 可选复用附录

当用户需要复刻，或报告确有可交接的结构依据时，可以增加 `data-section="handoff"`。该章节不是图文或视频报告的必需章节，缺少它不影响独立分析报告完成。

- 可见标题使用“可选复用参考”或同等独立语义，不把主体的“说服结构”改名为“复刻蓝图”。
- 明确说明附录不影响报告独立成立，仅供下游内容生产流程按需读取。
- 分开展示路线分析状态与复刻准备度；`research_only` 路线不得包装成推荐生产路线。
- 附录可以列出可复用的功能结构、阻塞输入和禁止假设，但不得把报告改成必须执行的制作流程。

## 内容表达

- 先写结论，再给证据和适用范围。
- 主要结论后立即给对应原帖图片和图注。标题、封面、正文、图片载体或路线判断不能只引用样本编号而不展示可核验图片。
- 区分原始事实、重复观察、分析推断、待验证假设和人工确认事实。
- 路线名称描述用户任务或决策方式，不使用“高点击”“高转化”等未经因果证据支持的名称。
- 互动指标注明采集时点和不可比条件，不解释为结构效果。
- 对健康、功效、机理、结果、竞品比较、真实体验和商业关系明确证据边界。

## 不得出现

- 与内容分析无关的版本、里程碑、任务状态或工作过程。
- 修改记录、工具调用说明、制作人员或 Agent 解释。
- `SKILL.md`、脚本调用说明、文件结构或技能自证内容。
- “执行摘要”、面向制作者的阅读指令、制作备注或沟通问答。
- 本机用户名、绝对路径、临时目录、账号凭证或服务商配置。
- 未实现能力预告、效果保证或把正样本共性写成爆款因果公式。

## 校验

在技能目录中运行：

```bash
python3 scripts/validate_html_report.py output/analysis-report.html
```

校验器检查基本文档结构、统一板式标记、固定组件、结论证据组层级、必需章节、外部依赖、本机路径和常见内部语言。它不能替代人工检查内容准确性、视觉质量、响应式表现和证据判断。
