# Mental Model Info Cards Project

这是由 `$mental-model-info-cards` 初始化的六张式概念知识信息卡项目。

## 结构

```text
tool-v1/   HTML/CSS/JS 渲染工具和内容数据
output/    最终 PNG 验收区
archive/   被替代的实验和历史版本
```

## 开始使用

1. 编辑 `tool-v1/data/theme.js` 设置品牌名、纸张色和强调色池。
2. 编辑 `tool-v1/data/models.js` 增加或修改概念。
3. 编辑 `tool-v1/data/captions.md` 维护发布配文。
4. 用浏览器打开 `tool-v1/index.html` 预览。
5. 在 `tool-v1/` 中运行 `node export.mjs` 导出 PNG。

导出前建议运行 Skill 自带的 `scripts/validate_project.mjs`。
