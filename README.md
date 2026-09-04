# Open Creator

Open Creator 是一个面向内容创作者的开源 AI Skills 工具库，提供可安装、可组合的创作工具。

仓库计划覆盖灵感与选题、资料研究、内容策划、文案写作、图文制作、视频生产、发布管理和内容复盘等创作环节。当前能力会持续按独立 Skill 的形式扩展。

这个仓库采用“一个仓库，多个 Skill”的结构。每个 Skill 都是独立、可安装、可验证的能力单元；仓库根目录负责统一导航、贡献规范、版本记录和自动验证。

## Skills

| Skill | 用途 |
| --- | --- |
| [`mental-model-info-cards`](skills/mental-model-info-cards/) | 创建、导出和审查六张式思维模型与概念知识信息卡 |
| [`xhs-viral-content-analysis`](skills/xhs-viral-content-analysis/) | 解析小红书图文或视频内容，或综合多份既有分析报告，交付证据化 HTML 与结构化 JSON |

后续 Skill 会继续放在 `skills/<skill-name>/` 下，而不是创建新的独立仓库。

## 安装

### 使用 Skill Installer

在 Codex 中调用 `$skill-installer`，要求从以下仓库安装目标 Skill：

```text
https://github.com/DLe-kb/open-creator
```

并指定 Skill 名称，例如 `mental-model-info-cards` 或 `xhs-viral-content-analysis`。

### 用户级手动安装

```bash
git clone https://github.com/DLe-kb/open-creator.git ~/open-creator
mkdir -p ~/.agents/skills
ln -s ~/open-creator/skills/mental-model-info-cards ~/.agents/skills/mental-model-info-cards
ln -s ~/open-creator/skills/xhs-viral-content-analysis ~/.agents/skills/xhs-viral-content-analysis
```

更新仓库：

```bash
git -C ~/open-creator pull
```

### 仓库级安装

只希望某个项目使用时，把目标 Skill 放入该项目的 `.agents/skills/`：

```bash
mkdir -p /path/to/your-repo/.agents/skills
cp -R skills/mental-model-info-cards /path/to/your-repo/.agents/skills/mental-model-info-cards
```

如果新安装的 Skill 没有立即出现，请重启 Codex。

## 仓库结构

```text
open-creator/
├── .codex-plugin/plugin.json
├── .github/workflows/validate.yml
├── docs/
│   ├── mental-model-info-cards/
│   └── xhs-viral-content-analysis/
├── examples/
│   └── mental-model-info-cards/
├── scripts/validate_repo.py
├── skills/
│   ├── mental-model-info-cards/
│   └── xhs-viral-content-analysis/
├── CONTRIBUTING.md
├── SECURITY.md
├── CHANGELOG.md
└── LICENSE
```

每个 Skill 运行时目录只保留 Agent 真正需要的 `SKILL.md`、`agents/`、`references/`、`scripts/` 或 `assets/`。面向人的说明、示例和维护文档放在仓库级目录，避免增加 Skill 加载时的上下文负担。

## Mental Model Info Cards

Mental Model Info Cards 用六张卡解释一个思维模型或概念。它包含卡组协议、内容质量规则、初始化与校验脚本，以及可独立运行的 HTML/CSS/JS 渲染模板。

- [使用说明](docs/mental-model-info-cards/README-使用说明.md)
- [Skill 本体](skills/mental-model-info-cards/)
- [第一性原理示例输出](examples/mental-model-info-cards/first-principles/)

显式调用示例：

```text
$mental-model-info-cards 创建一个新的六张式概念知识信息卡项目。
```

```text
$mental-model-info-cards 为“机会成本”制作、校验并导出一组六张知识卡。
```

## XHS Viral Content Analysis

XHS Viral Content Analysis 包含两种独立工作流：解析一批小红书图文或视频笔记；综合多份已经完成的分析报告。前者识别信息任务、主要载体、内容路线、说服结构、价值转译和风险边界，后者提炼跨报告共性机制、路线、媒体与研究对象差异及适用边界。两种工作流都输出可独立审阅的单文件 HTML 与结构化 JSON，不直接生成或发布新内容。

- [使用说明](docs/xhs-viral-content-analysis/README-使用说明.md)
- [Skill 本体](skills/xhs-viral-content-analysis/)

显式调用示例：

```text
$xhs-viral-content-analysis 分析这批小红书图文内容，输出带原帖证据的 HTML 报告和结构化 JSON。
```

```text
$xhs-viral-content-analysis 分析这批小红书视频，重点拆解前 5 秒、画面文字、口播、声画关系和观众决策链。
```

```text
$xhs-viral-content-analysis 综合这几份已经完成的小红书内容分析报告，提炼反复出现的内容机制、内容路线、媒体与产品差异，并生成综合 HTML 报告和结构化 JSON。
```

## 验证

```bash
python3 -m pip install -r requirements-dev.txt
python3 scripts/validate_repo.py
```

验证会扫描所有 `skills/*/SKILL.md`，检查 Skill 元数据、目录命名、插件清单、仓库链接、本机绝对路径、TODO 占位符和 Finder 缓存。GitHub Actions 还会运行 `xhs-viral-content-analysis` 的单批解析与跨报告综合 HTML/JSON 校验器测试。

## 发布

不同 Skill 独立演进。公开能力、使用方式和重要变更以 Skill 本体、使用说明与 `CHANGELOG.md` 为准。

## License

[MIT](LICENSE)

## English summary

Open Creator is an open-source AI Skills toolkit for content creators, covering ideation, research, writing, visual content, video production, publishing, analytics, and creator workflows. Each Skill lives under `skills/<skill-name>/` and is versioned independently.
