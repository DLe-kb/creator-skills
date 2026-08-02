# Open Creator Repository Guidance

## 仓库定位

本仓库是 Open Creator 的公开发布仓库，只保存 GitHub 用户真实需要的正式 Skills、脚本、模板、示例、公开文档和验证配置。

Skill 的研究、讨论、候选判断和真实项目验证应留在来源项目或 AI Native Lab，不迁入本仓库。

## 发布 Skill

当用户要求把其他项目中的 Skill 发布到 Open Creator 时：

1. 先读取来源项目的规则、Skill 文件和验证证据。
2. 判断 Skill 是否已经真实使用、边界清楚并具备公开价值；不成熟时停止发布并说明缺口。
3. 只把公开运行所需的正式文件迁入 `skills/<skill-name>/`。
4. 删除本机绝对路径、私人数据、凭证、业务专属内容、临时约束和无必要的历史过程。
5. 更新根目录 `README.md`、`CHANGELOG.md`、相关 `docs/`、`examples/` 和仓库验证规则。
6. 运行 Skill、plugin（插件）、仓库和必要的实际功能验证。
7. 检查准确的 Git diff，通过分支、Pull Request（拉取请求）和独立 Skill 版本标签发布。
8. 发布完成后，只在来源项目或 AI Native Lab 更新内部状态。

## 仓库边界

不要在本仓库创建或提交：

- `PROJECT_STATE.md`、`DISCUSSION_QUEUE.md`、内部候选池或任务状态。
- 调研过程、聊天记录、迁移日志或私人复盘。
- 未成熟的 Skill 草稿和只适用于单个业务项目的工作流。
- API Key、token（令牌）、cookie、密码、App Secret 或完整凭证文件。
- 本机绝对路径、Finder 缓存、构建缓存和无关生成文件。
- 未确认许可证或版权来源的第三方内容。

## Skill 结构

- 每个 Skill 使用独立目录 `skills/<skill-name>/`。
- 运行时目录保持精简，只保留必要的 `SKILL.md`、`agents/`、`scripts/`、`references/` 和 `assets/`。
- 面向人的安装、示例和维护说明放在仓库根目录、`docs/` 或 `examples/`。
- 每个 Skill 独立验证和版本化，标签使用 `<skill-name>-v<version>`。

## 默认验证

提交前至少运行：

```bash
python3 scripts/validate_repo.py
```

同时检查：

- Skill frontmatter（元数据）与目录名一致。
- `agents/openai.yaml` 和 plugin manifest（插件清单）有效。
- 公开链接、必要文件和示例完整。
- 没有敏感信息、本机路径、临时占位符或 `.DS_Store`。
- `README.md`、`CHANGELOG.md` 和版本标签与发布内容一致。
