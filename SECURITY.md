# Security Policy

Open Creator 中的 Skills 默认不应要求用户提交真实账号凭证。

请勿在 issue（问题）、示例、测试材料、Skill references 或脚本中提交 API Key、token、cookie、密码、App Secret、私人路径或完整凭证文件。

如果发现仓库中包含敏感信息：

1. 不要在公开 issue 中复制敏感值。
2. 优先使用 GitHub 的 private vulnerability reporting（私密漏洞报告）功能。
3. 如果该功能不可用，只创建不含敏感细节的 issue，说明需要维护者私下处理。

误提交的真实凭证必须先在来源系统轮换，删除 Git 历史中的文本不能替代凭证轮换。

`conversation-title-organizer` 默认只使用本机规则。可选 AI 兜底仅从插件专用的 `CONVERSATION_TITLE_API_KEY` 环境变量读取用户主动提供的凭证；插件不会读取浏览器 Cookie、Codex 登录态、通用 `OPENAI_API_KEY` 或 `~/.codex/config.toml` 中的 provider 凭证。用户 JSON 配置禁止保存密钥类字段。
