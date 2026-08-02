# Open Creator

Open Creator 是一个面向 Codex 和 AI Agent 的开放 Skill 集合，用来沉淀从真实内容、增长、业务和 Agent 实践中提炼出的可复用能力。

这个仓库采用“一个仓库，多个 Skill”的结构。每个 Skill 都是独立、可安装、可验证的能力单元；仓库根目录负责统一导航、贡献规范、版本记录和自动验证。

## Skills

| Skill | 用途 | 当前版本 |
| --- | --- | --- |
| [`project-harness`](skills/project-harness/) | 为单个项目初始化、审查和维护轻量 Project Harness（项目脚手架 / 约束系统） | `0.1.0` |
| [`mental-model-info-cards`](skills/mental-model-info-cards/) | 创建、导出和审查六张式思维模型与概念知识信息卡 | `0.1.0` |

后续 Skill 会继续放在 `skills/<skill-name>/` 下，而不是创建新的独立仓库。

## 安装

### 使用 Skill Installer

在 Codex 中调用 `$skill-installer`，要求从以下仓库安装目标 Skill：

```text
https://github.com/DLe-kb/open-creator
```

并指定 Skill 名称，例如 `project-harness` 或 `mental-model-info-cards`。

### 用户级手动安装

```bash
git clone https://github.com/DLe-kb/open-creator.git ~/open-creator
mkdir -p ~/.agents/skills
ln -s ~/open-creator/skills/project-harness ~/.agents/skills/project-harness
ln -s ~/open-creator/skills/mental-model-info-cards ~/.agents/skills/mental-model-info-cards
```

更新仓库：

```bash
git -C ~/open-creator pull
```

### 仓库级安装

只希望某个项目使用时，把目标 Skill 放入该项目的 `.agents/skills/`：

```bash
mkdir -p /path/to/your-repo/.agents/skills
cp -R skills/project-harness /path/to/your-repo/.agents/skills/project-harness
```

如果新安装的 Skill 没有立即出现，请重启 Codex。

## 仓库结构

```text
open-creator/
├── .codex-plugin/plugin.json
├── .github/workflows/validate.yml
├── docs/
│   ├── mental-model-info-cards/
│   └── project-harness/
├── examples/
│   ├── mental-model-info-cards/
│   └── project-harness/
├── scripts/validate_repo.py
├── skills/
│   ├── mental-model-info-cards/
│   └── project-harness/
├── AGENTS.md
├── CONTRIBUTING.md
├── SECURITY.md
├── CHANGELOG.md
└── LICENSE
```

每个 Skill 运行时目录只保留 Agent 真正需要的 `SKILL.md`、`agents/`、`references/`、`scripts/` 或 `assets/`。面向人的说明、示例和维护文档放在仓库级目录，避免增加 Skill 加载时的上下文负担。

## Project Harness

Project Harness 是本仓库发布的第一个 Skill。它帮助新的 Agent 或新对话快速理解：项目是什么、当前做到哪里、哪些不能动、下一步是什么，以及什么时候必须让人确认。

- [设计原则](docs/project-harness/design-principles-设计原则.md)
- [文件职责](docs/project-harness/file-guide-文件职责.md)
- [可视化结构图](docs/project-harness/project-harness-visual-map.html)
- [最小项目示例](examples/project-harness/minimal-project/)

显式调用示例：

```text
$project-harness 为这个项目初始化最小协作骨架。
```

```text
$project-harness 审查当前 AGENTS.md 和 PROJECT_STATE.md，删除不再有用的管理负担。
```

## Mental Model Info Cards

Mental Model Info Cards 把“一项概念，六张卡讲清楚”的真实生产经验整理为可安装 Skill。它包含通用卡组协议、内容质量规则、初始化与校验脚本，以及可独立运行的 HTML/CSS/JS 渲染模板。

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

## 验证

```bash
python3 -m pip install -r requirements-dev.txt
python3 scripts/validate_repo.py
```

验证会扫描所有 `skills/*/SKILL.md`，检查 Skill 元数据、目录命名、插件清单、仓库链接、本机绝对路径、TODO 占位符和 Finder 缓存。GitHub Actions 会在每次 push 和 pull request 时运行相同检查。

## 版本

不同 Skill 独立发布，标签格式为：

```text
<skill-name>-v<version>
```

例如：`project-harness-v0.1.0`、`mental-model-info-cards-v0.1.0`。

## License

[MIT](LICENSE)

## English summary

Open Creator is an open collection of reusable Codex and AI Agent skills distilled from real content, growth, business, and agent workflows. Each skill lives under `skills/<skill-name>/` and is versioned independently.
