# Mental Model Info Cards 使用说明

`mental-model-info-cards` 用于创建、扩展、审查、导出和归档六张式思维模型与概念知识信息卡。

## 来源

该 Skill 来自一个真实的本地信息卡项目：先经历 3 轮 MVP，再用轻量 HTML/CSS/JS 工具完成 20 组、共 120 张卡片的试生产。公开版只提炼稳定流程和通用工具，不包含个人品牌、完整内容库、历史成品或本机路径。

## 六张卡

1. 封面：名称和记忆钩子。
2. 定义：核心动作、适用场景、判断信号和输出。
3. 机制：流程、循环、平衡或四象限。
4. 提问：四个可以直接使用的问题。
5. 案例：具体场景和三步应用。
6. 边界：误用提醒、延展阅读和行动建议。

## 初始化项目

安装 Skill 后，在 Skill 目录运行：

```bash
python3 scripts/init_project.py /path/to/new-project
```

模板使用原生 HTML、CSS 和 JavaScript，不需要安装 npm 包。预览时直接打开 `tool-v1/index.html`。

## 校验与导出

```bash
node scripts/validate_project.mjs /path/to/new-project
```

进入新项目的 `tool-v1/`：

```bash
node export.mjs
```

导出需要本机安装 Chrome、Chromium 或兼容浏览器。可通过 `CARDS_BROWSER` 指定浏览器路径。

## 示例

[第一性原理六张示例](../../examples/mental-model-info-cards/first-principles/) 展示了默认模板的实际导出结果。品牌名称和强调色可在 `tool-v1/data/theme.js` 中修改。
