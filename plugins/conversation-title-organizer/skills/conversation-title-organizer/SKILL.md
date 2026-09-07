---
name: conversation-title-organizer
description: Diagnose, explain, or customize the installed Conversation Title Organizer Codex plugin. Use when the user asks whether automatic conversation naming is active, why a title was skipped, how Token usage is recorded, or how to change fixed title types. Do not use for ordinary requests that merely need a good title.
---

# Conversation Title Organizer

帮助用户检查和调整同一插件中的自动会话标题能力。

## 诊断

先解析当前 `SKILL.md` 的安装位置。插件根目录是当前 Skill 目录的上两级，诊断脚本位于：

```text
<plugin-root>/scripts/normalize_conversation_title.py
```

运行：

```bash
python3 <plugin-root>/scripts/normalize_conversation_title.py --doctor
```

向用户解释诊断结果时，不读取或展示 Cookie、API Key、会话正文、原始标题或 Codex 登录信息。

## 自定义

只有用户明确要求修改分类时，才创建或更新：

```text
~/.codex/conversation-title-organizer/config.json
```

以插件的 `config/default-config.json` 为字段参考，只保存类型、规则、项目路径和非敏感模型参数。禁止在 JSON 中保存 API Key、token、Cookie、密码或 secret；AI 凭证只能由用户通过插件专用环境变量 `CONVERSATION_TITLE_API_KEY` 提供。

类型列表是固定候选。可以根据用户的工作调整候选与项目映射，但不要让模型在运行中创建新类型。

## 排障边界

- `local_fast_path: true` 且标题意图明确：应记录 `classifier_mode: local`，Token 为 0。
- 没有 AI 环境变量且本机无法可靠判断：保留原名是正常安全降级。
- 已归档、子 Agent 或已符合格式的会话：不会改名。
- 找不到兼容的 Codex 会话数据库：停止，不猜测修改其他 SQLite 文件。
- Codex 大版本升级后出现失败：先运行 doctor，再检查插件更新与 GitHub issue，不直接放宽数据库识别条件。
