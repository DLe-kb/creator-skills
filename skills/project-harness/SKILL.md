---
name: project-harness
description: "Initialize, audit, simplify, or maintain a lightweight single-project Project Harness for Codex and AI agents. Use for AGENTS.md, PROJECT_STATE.md, decisions, runbooks, task-state splitting, stage contracts, reviewer gates, rework loops, or requests such as 初始化项目记录、精简项目管理、从项目状态继续、拆分臃肿状态文件. Do not use for cross-project portfolio management."
---

# Project Harness（项目脚手架 / 约束系统）

维护单个项目的轻量 Project Harness。Project Harness 是项目内部的执行脚手架：规则、状态真相源、决策、运行手册、阶段契约、审查关卡、返工闭环和 skill 化路径，用来让 Codex / Agent 稳定推进项目。

保持 Harness 小而有用。只有当文件、规则或流程能减少未来上下文重建成本、防止误操作、保存已定决策，或让成熟流程更容易自检和交接时，才创建或更新它。

默认核心只有三类：`AGENTS.md` 管稳定入口和边界，`PROJECT_STATE.md` 管当前真相，`RUNBOOK.md` 管成熟重复流程。其他文件按触发条件自然生长，不预先铺满。

## 语言规则

给用户阅读的内容默认中文主导。必要英文术语保留，并补中文括注，例如 `Project Harness（项目脚手架 / 约束系统）`、`stage contract（阶段契约）`、`reviewer gate（审查关卡）`、`rework loop（返工闭环）`。

文件名、系统字段、标准文件名和 skill 名称可以保留英文，例如 `AGENTS.md`、`PROJECT_STATE.md`、`RUNBOOK.md`。

## 参考文件加载

只读取当前任务需要的 references（参考文件）：

- 新建、审查或精简 Project Harness：读取 `references/protocol-playbook.md`，再读取需要的编号模板。
- 最小初始化：读取 `references/01_AGENTS.md` 和 `references/02_PROJECT_STATE.md`。
- 状态文件臃肿或任务拆分：读取 `references/02_PROJECT_STATE.md` 和 `references/08_TASK_STATE.md`。
- 重复流程、操作步骤、阶段契约、审查关卡或返工闭环：读取 `references/05_RUNBOOK.md`。
- 决策记录：读取 `references/03_DECISIONS.md`。
- 用户待决问题：读取 `references/04_DISCUSSION_QUEUE.md`。
- 重要外部链接或资料：读取 `references/06_REFERENCES.md`。
- 重复错误、协作摩擦或经验沉淀：读取 `references/07_LESSONS_LEARNED.md`。

如果当前项目已经有自己的 `AGENTS.md`，优先遵守当前项目的规则，而不是 bundled template（随 skill 附带模板）。

## 初始化流程

1. 先检查当前项目根目录和已有 Harness 文件，不要直接覆盖。
2. 选择最小有用层级：
   - Level 0（无需更新）：很小的一次性任务，不更新 Harness 文件。
   - Level 1（轻量）：只创建或更新 `AGENTS.md` 和 `PROJECT_STATE.md`。
   - Level 2（持续项目）：项目跨多轮推进，或出现可重复流程、稳定决策、待讨论问题时，再增加 `RUNBOOK.md`、`DECISIONS.md`、`DISCUSSION_QUEUE.md`。
   - Level 3（长期复杂项目）：只有当项目长期维护、资料变多、需要复盘、迁移或 skill 化时，再增加 `REFERENCES.md`、`LESSONS_LEARNED.md`、阶段契约、返工闭环或项目地图。
3. 只创建或更新当前需要的文件，不预先铺满所有模板。
4. 用户可读项目文档默认中文，除非项目、外部平台或代码/API 要求英文。
5. 不把密钥、access token（访问令牌）、refresh token（刷新令牌）、cookie、App Secret 或完整凭证文件写入 Harness 文档。
6. 删除、覆盖、移动、改权限、转移所有权、生产写入、真实发布或付费资源使用前，必须停下来请求当前对话确认。

## PROJECT_STATE.md 规则

`PROJECT_STATE.md` 应保持短、准、当前。它记录项目级目标、当前状态、活跃任务索引、下一步、活跃文件、阻塞项、需要用户决策的问题和最近更新时间。

不要让它变成任务流水账。稳定决策放进 `DECISIONS.md`，重复流程放进 `RUNBOOK.md`，资料放进 `REFERENCES.md`，经验放进 `LESSONS_LEARNED.md`。

只有在真正有用时才启用 `task-states/`：

- `PROJECT_STATE.md` 大约超过 150-200 行，开始拖慢上下文恢复。
- 两个或更多任务并行活跃。
- 某个子任务会跨多轮对话推进，并且有自己的目标、文件、阻塞项和完成标准。
- 用户明确要求按任务或子项目拆分状态。

启用 `task-states/` 后：

- `PROJECT_STATE.md` 只保留项目总览和活跃任务索引。
- 每个真正活跃的任务用 `references/08_TASK_STATE.md` 创建一份任务状态文件。
- 只读取当前相关的任务状态，不默认读取所有历史任务。
- 已完成、废弃或长期暂停的任务状态移动到 `task-states/archive/`。
- 不预先创建空的任务状态文件。

## 成熟流程契约

当一个成熟流程仍然需要用户逐阶段人工检查时，先在 `RUNBOOK.md` 中定义 stage contract（阶段契约），不要优先创建新的流程 skill。

每个阶段契约应写清：

- Input standard（输入标准）。
- Output standard（输出标准）。
- Self-check checklist（自检清单）。
- Downstream acceptance standard（下游验收标准）。
- Rework ticket format（返工单格式）。
- Automatic rework limit（自动返工上限），通常 1-2 次后升级给用户。
- User gate（用户确认门），例如删除、覆盖、移动、发布、外部写入、权限、账号操作、付费资源、方向改变或返工达到上限。

检查必须有 evidence（证据），不能只写“已检查”。例如字幕抽查时间点、渲染时长和分辨率、抽帧路径、contact sheet（联系表 / 缩略图总览）、缺失字段数量或具体测试命令。

## Skill 化边界

重复流程先进入项目 `RUNBOOK.md` 或知识库。只有真实使用 2-3 次后，输入输出稳定、边界清楚、验证证据明确，才考虑升级为 skill、脚本、MCP 或 automation。

如果一个 skill 只是在包装通用检查清单，优先降级回 `RUNBOOK.md` 或知识库方法论，避免 skill 变成新的大杂烩。

## 继续项目

用户要求从项目状态继续时：

1. 先读取 `AGENTS.md` 和 `PROJECT_STATE.md`。
2. 如果 `PROJECT_STATE.md` 指向活跃的 `task-states/*.md`，只读取相关任务状态文件。
3. 只有在和当前任务相关时，才读取 `DECISIONS.md`、`DISCUSSION_QUEUE.md`、`RUNBOOK.md`、`REFERENCES.md` 或 `LESSONS_LEARNED.md`。
4. 在做高风险改动前，用简短中文说明当前目标、近期进展、最合理下一步、阻塞项和需要用户决策的问题。

## 收工检查

完成有意义的工作前，判断是否需要更新：

- `PROJECT_STATE.md` 或当前 `task-states/*.md`：目标、进度、下一步、阻塞项、活跃文件变化。
- `DECISIONS.md`：形成后续应继续遵守的明确决策。
- `DISCUSSION_QUEUE.md`：出现 Codex 不能擅自决定的问题。
- `REFERENCES.md`：新增重要资料、文档、API、工具链接。
- `RUNBOOK.md`：新增可重复流程、阶段契约、审查关卡或返工闭环。
- `LESSONS_LEARNED.md`：出现重复摩擦、失败模式或更好的协作规则。

如果不需要更新 Harness 文件，在最终回复里明确说明。
