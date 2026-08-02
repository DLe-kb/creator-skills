# 工具操作指南

## 初始化

```bash
python3 scripts/init_project.py /path/to/project
```

初始化器把 `assets/template/` 复制为独立项目，并创建 `output/`、`archive/`。

## 预览

直接用浏览器打开：

```text
tool-v1/index.html
```

查看单张卡：

```text
tool-v1/index.html?model=first-principles&card=1
```

## 校验

```bash
node scripts/validate_project.mjs /path/to/project
```

校验内容包括模型字段、编号和 slug 唯一性、六页类型顺序、机制图类型、配文条目和导出文件完整性。

## 导出

进入项目的 `tool-v1/` 后运行：

```bash
node export.mjs
```

环境变量：

```bash
CARDS_MODELS=first-principles node export.mjs
CARDS_FORCE=1 node export.mjs
CARDS_BROWSER=/path/to/chrome node export.mjs
```

- `CARDS_MODELS`：逗号分隔的 slug、id 或 `<id>-<name>`。
- `CARDS_FORCE=1`：覆盖已经完整导出的卡组。
- `CARDS_BROWSER`：指定 Chrome 或 Chromium 可执行文件。

## 视觉检查

导出后至少抽查：

- 第一页标题和英文名。
- 第二页长文本与四个事实框。
- 第三页节点、连线和标签。
- 第四页四个问题的高度。
- 第五页三步案例和结论。
- 第六页阅读列表、边界提示和行动建议。

自动校验不能替代视觉检查。
