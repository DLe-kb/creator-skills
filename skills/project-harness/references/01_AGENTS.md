# Project Harness 项目说明

## 用途

这个项目使用轻量 Project Harness，帮助 Codex / Agent 在新对话中快速恢复项目目标、当前状态、已定决策、待讨论问题和可重复流程。

Project Harness 是单个项目内部的脚手架 / 约束系统。它不负责跨项目调度和全局优先级；这些职责应交给 Hermes 或单独的 Portfolio Harness。

## 工作方法

- Project Harness 的目标是减少下一轮沟通成本、误操作风险和人工验收负担，不是增加本轮文档维护成本。小任务默认轻量执行，只有当规则或文件能明显减少后续重复解释、上下文重建、误推进、返工或风险操作时才启用。
- 继续推进项目时，先读取 `00_project-harness-项目协作/PROJECT_STATE.md`。只有当前任务需要时，再读取 `DECISIONS.md`、`DISCUSSION_QUEUE.md`、`REFERENCES.md`、`RUNBOOK.md` 或 `LESSONS_LEARNED.md`。
- 如果 `00_project-harness-项目协作/PROJECT_STATE.md` 指向 `task-states/` 中的活跃任务，只读取当前相关的任务状态文件，不默认读取全部历史任务。
- 优先小步可验证地推进：先只读检查，再局部修改，再验证。
- 长期项目知识要写入文件，不只留在聊天里。
- 成熟重复流程写入 `00_project-harness-项目协作/RUNBOOK.md`。如果流程仍需要用户逐步盯梢，先定义阶段输入、输出、自检证据、下游验收、返工规则和用户确认门。
- 不记录密钥、访问令牌、刷新令牌、cookie、App Secret 或完整凭证文件。
- 删除、覆盖、移动、修改权限、转移所有权或对外部账号做有风险操作前，必须先询问。
- 同一类流程重复出现 2-3 次后，先沉淀为 runbook 或知识库方法论；是否升级为 skill、脚本、MCP 或 automation，必须由人确认。

## 协作文件

- `00_project-harness-项目协作/PROJECT_STATE.md`：当前目标、进展、下一步、活跃文件、阻塞项。
- `task-states/`：可选目录。只有当项目长期多任务推进、`00_project-harness-项目协作/PROJECT_STATE.md` 开始膨胀时才创建；每个活跃任务一份状态文件。
- `00_project-harness-项目协作/DECISIONS.md`：已经接受的决策和原因。
- `00_project-harness-项目协作/DISCUSSION_QUEUE.md`：需要人参与判断的问题。
- `00_project-harness-项目协作/REFERENCES.md`：官方文档、工具链接和研究记录。
- `00_project-harness-项目协作/RUNBOOK.md`：配置、检查、可重复执行的操作流程、阶段契约和返工闭环。
- `00_project-harness-项目协作/LESSONS_LEARNED.md`：复盘出的摩擦点和改进点，稳定后再迁入规则。

不要求项目一开始就创建全部文件。最小必备是 `AGENTS.md` 和 `00_project-harness-项目协作/PROJECT_STATE.md`。其他文件在出现对应需求时再补：

- 有稳定决策：创建 `00_project-harness-项目协作/DECISIONS.md`。
- 有需要用户判断的问题：创建 `00_project-harness-项目协作/DISCUSSION_QUEUE.md`。
- 有可重复操作流程，或需要定义阶段契约 / 自检 / 下游验收 / 返工闭环：创建 `00_project-harness-项目协作/RUNBOOK.md`。
- 有重要资料或外部工具链接：创建 `00_project-harness-项目协作/REFERENCES.md`。
- 有重复错误、协作摩擦或复盘经验：创建 `00_project-harness-项目协作/LESSONS_LEARNED.md`。

## 默认完成标准

- 说明改了什么。
- 说明验证了什么、没有验证什么。
- 如果项目方向、下一步、决策或待讨论问题发生变化，更新对应状态文件。

## 协作骨架文件更新机制

每轮任务收尾前，检查是否需要更新这些文件：

- 目标、进度、下一步、阻塞项变化：更新 `00_project-harness-项目协作/PROJECT_STATE.md`。
- 如果已启用 `task-states/`，任务内进度优先更新当前任务状态文件，`00_project-harness-项目协作/PROJECT_STATE.md` 只更新活跃任务索引和项目总览。
- 出现已经确定、后续应继续遵守的判断：更新 `00_project-harness-项目协作/DECISIONS.md`。
- 出现需要用户判断、不能由 Codex 擅自决定的问题：更新 `00_project-harness-项目协作/DISCUSSION_QUEUE.md`。
- 新增重要链接、资料、API 文档、工具说明：更新 `00_project-harness-项目协作/REFERENCES.md`。
- 新增可重复执行的安装、配置、发布、检查流程，或成熟流程的阶段契约：更新 `00_project-harness-项目协作/RUNBOOK.md`。
- 出现重复错误、协作摩擦或可改进流程：更新 `00_project-harness-项目协作/LESSONS_LEARNED.md`。

如果对应文件尚不存在，但本轮出现了明确触发条件，就创建它。很小的改动如果没有改变项目状态、决策、资料或流程，可以不更新骨架文件，但需要在最终回复中说明“本轮无需更新状态文件”。

默认轻量执行，按需升档：

- Level 0 直接执行：小任务无需更新协作文件。
- Level 1 轻量状态：普通推进只更新当前状态、下一步或必要的阶段状态。
- Level 2 完整协作：跨多轮、跨工具、复杂项目或高风险操作时，再启用完整配套文件。

## 上下文压缩前检查点

长任务、连续多轮探索、文件改动较多或讨论分支变多时，不等到最后再更新。应主动创建检查点：

- 当前目标和下一步写入 `00_project-harness-项目协作/PROJECT_STATE.md`。
- 已确定判断写入 `00_project-harness-项目协作/DECISIONS.md`。
- 需要用户确认的问题写入 `00_project-harness-项目协作/DISCUSSION_QUEUE.md`。
- 新找到的重要资料写入 `00_project-harness-项目协作/REFERENCES.md`。
- 新形成的重复流程写入 `00_project-harness-项目协作/RUNBOOK.md`。
- 协作风险或经验写入 `00_project-harness-项目协作/LESSONS_LEARNED.md`。

如果发现上下文已经很长，或用户提醒“上下文快满了”，先暂停新增工作，完成状态落盘，再继续。
