# Tool v1

本工具使用原生 HTML、CSS 和 JavaScript 渲染 `1080 x 1440` 的六张式知识信息卡。

## 数据

- `data/models.js`：概念和六张卡的生产数据。
- `data/theme.js`：品牌名、纸张色和强调色池。
- `data/captions.md`：发布配文。

## 预览

直接打开 `index.html` 查看全部卡片。查看单张卡：

```text
index.html?model=first-principles&card=1
```

## 导出

```bash
node export.mjs
```

可选环境变量：

```bash
CARDS_MODELS=first-principles node export.mjs
CARDS_FORCE=1 node export.mjs
CARDS_BROWSER=/path/to/chrome node export.mjs
```

导出文件进入项目根目录的 `output/<id>-<name>/`。
