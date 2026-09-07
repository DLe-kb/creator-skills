# Conversation Title Organizer 使用说明

Conversation Title Organizer 是一个独立安装的 Codex Plugin（插件）。它在主会话回答结束后，将标题规范为：

```text
MMDD｜类型｜主题
```

例如：

```text
0907｜排障｜修复自动命名
0907｜调研｜选择视频工具
```

## 安装

要求：

- Codex CLI 支持 `codex plugin` 命令。
- 使用 Codex Desktop，并存在兼容的本机会话数据库。
- 本机可执行 `python3`，版本为 Python 3.9 或更高。

添加 Open Creator marketplace（插件市场）：

```bash
codex plugin marketplace add DLe-kb/creator-skills --ref main
```

安装插件：

```bash
codex plugin add conversation-title-organizer@creator-skills
```

安装后，在 Codex 中使用 `/hooks` 打开 Hook 管理，检查并信任 `Conversation Title Organizer` 的 Hook。Codex 不会自动信任新安装插件携带的 Hook；未完成这一步时，插件能显示为已安装，但自动命名不会运行。

然后新建一个 Codex 主会话。第一次回答结束后，插件会在后台尝试规范标题。子 Agent、归档会话和已经符合格式的标题不会处理。

## 默认运行方式

- 意图明确时，本机完成分类，模型 Token 为 0。
- 意图含糊且没有配置 AI 时，保留原名，不冒险误改。
- 类型只能从固定列表中选择，插件不会自行增加分类。
- 每个会话最多尝试一次，不会在每轮回答后重复运行模型。

默认类型：

```text
概念、调研、评估、规划、实践、开发、验证、排障、复盘、治理、沉淀
```

## 可选 AI 兜底

本机无法可靠判断时，可以使用 OpenAI-compatible Responses API（兼容 OpenAI Responses 的接口）进行语义分类。

默认不启用真实 AI 调用，因为插件不会读取 Codex 登录 Cookie、浏览器 Cookie、`~/.codex/config.toml`、通用 `OPENAI_API_KEY` 或其他应用凭证。需要 AI 兜底时，由用户自行设置插件专用环境变量：

```bash
export CONVERSATION_TITLE_API_KEY="your-api-key"
```

默认使用 `https://api.openai.com/v1` 和 `gpt-5-mini`。兼容接口可以额外设置：

```bash
export CONVERSATION_TITLE_BASE_URL="https://your-provider.example/v1"
export CONVERSATION_TITLE_MODEL="your-model"
```

不要把 API Key 写入仓库、插件目录或 JSON 配置文件。插件会拒绝包含 `api_key`、`token`、`cookie`、`password` 或 `secret` 字段的用户配置。

## 隐私与安全

- 不读取浏览器 Cookie 或 Codex 登录 Cookie。
- 不读取 `~/.codex/config.toml` 中的 provider 或 token，也不借用通用 `OPENAI_API_KEY`。
- 不包含作者电脑的路径、账号、日志、数据库或会话内容。
- AI 兜底只发送当前标题和首条请求的短文本，最长 240 个字符。
- 发送前会清除链接、邮箱、手机号、证件号和常见本机路径。
- 历史记录只保存分类方式与 Token 数，不保存原始标题或新标题。
- 只修改 Codex 本机的会话标题索引，不发布内容，不操作外部账号。

## 自定义类型

如需自定义，在以下位置创建用户配置：

```text
~/.codex/conversation-title-organizer/config.json
```

用户配置会与默认配置合并。示例：

```json
{
  "profiles": {
    "software": {
      "types": ["需求", "设计", "开发", "测试", "修复", "发布"],
      "rules": [
        {
          "type": "修复",
          "prefixes": ["修复", "排查"],
          "keywords": ["报错", "失败", "bug"]
        }
      ]
    }
  },
  "projects": [
    {
      "key": "my-software-project",
      "root": "~/projects/my-app",
      "profile": "software"
    }
  ]
}
```

项目路径最长的规则优先；没有登记的项目继续使用通用类型。类型仍然来自用户配置中的固定候选，不会无限膨胀。

## 诊断

在插件目录运行：

```bash
python3 scripts/normalize_conversation_title.py --doctor
```

诊断只显示数据库是否找到、AI 是否由环境变量启用等布尔状态，不显示凭证、标题或会话正文。

运行记录位于 `~/.codex/conversation-title-organizer/`。其中 `history.jsonl` 不保存标题正文，`errors.log` 只保存错误类型。

## 更新与卸载

```bash
codex plugin marketplace upgrade creator-skills
codex plugin add conversation-title-organizer@creator-skills
```

卸载：

```bash
codex plugin remove conversation-title-organizer
```

插件依赖 Codex Desktop 当前本机会话数据库结构。Codex 大版本升级后，如果标题不再更新，先运行 `--doctor` 并查看仓库最新版本；脚本找不到兼容数据库时会停止，不会猜测写入未知数据库。
