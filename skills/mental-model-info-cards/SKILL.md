---
name: mental-model-info-cards
description: Create, extend, review, export, caption, or archive six-card mental-model and concept knowledge information cards. Use for requests involving 思维模型知识信息卡、概念卡片、六张式知识卡、card-set data, HTML/CSS card rendering, PNG export, publishing captions, visual QA, or initializing a reusable info-card project.
---

# Mental Model Info Cards

创建和维护“一项概念，六张卡讲清楚”的知识信息卡项目。优先产出可理解、可保存、可应用的知识单元，而不是把百科定义拆成六页。

Skill 自带可复制的轻量 HTML/CSS/JS 工具模板，不依赖特定品牌、现有项目或第三方前端框架。

## 选择工作模式

- **初始化项目**：运行 `scripts/init_project.py`，复制 `assets/template/` 并建立最小项目结构。
- **新增概念**：编辑现有项目的 `tool-v1/data/models.js` 和 `tool-v1/data/captions.md`。
- **审查卡组**：检查内容分工、结构字段、视觉风险、导出完整性和发布配文。
- **导出 PNG**：先运行校验，再从 `tool-v1/` 执行 `node export.mjs`。
- **调整协议或工具**：先确认属于通用能力还是项目专属品牌与内容，避免污染可复用模板。

处理现有项目时，先读取该项目自己的 `README.md`、状态文件和 `tool-v1/README.md`。不要假设固定绝对路径。

## 初始化

从 Skill 目录运行：

```bash
python3 scripts/init_project.py /path/to/new-project
```

初始化会创建：

```text
new-project/
├── README.md
├── tool-v1/
│   ├── data/models.js
│   ├── data/theme.js
│   ├── data/captions.md
│   ├── src/cards.js
│   ├── index.html
│   ├── styles.css
│   └── export.mjs
├── output/
└── archive/
```

默认拒绝覆盖非空目录。只有用户明确授权覆盖时才使用 `--force`。

## 六张卡协议

固定顺序：

1. `cover`：概念名称和记忆钩子。
2. `definition`：定义、适用场景、判断信号和输出。
3. `mechanism`：解释运作结构，支持 `flow`、`cycle`、`balance`、`matrix`。
4. `scenarios`：四个具有决策价值的问题。
5. `case`：一个具体场景和三步应用过程。
6. `boundary`：误用边界、延展阅读和行动建议。

新增内容前读取 [card-protocol.md](references/card-protocol.md)。撰写定义、案例、引用和配文时读取 [content-quality.md](references/content-quality.md)。操作模板、校验和导出时读取 [tool-guide.md](references/tool-guide.md)。

## 新增概念

1. 检查 `models.js` 中的现有 schema（结构）和编号。
2. 创建小写连字符 `slug`，并使用下一个未占用编号。
3. 从 `theme.js` 的色池选择一种强调色；同一组六张卡只用一种。
4. 严格创建六张卡，并保持协议顺序。
5. 在 `captions.md` 添加对应发布配文。
6. 运行结构校验：

```bash
node /path/to/skill/scripts/validate_project.mjs /path/to/project
```

7. 导出并检查六张 PNG 的尺寸、文字溢出、页脚和机制图。

## 内容标准

- 先说明读者何时会需要这个概念，再解释它是什么。
- 每页承担不同功能，不重复上一页。
- 提问卡提供真正能改变判断的问题，不写成口号。
- 案例使用具体人物、选择、约束和结果，不用抽象占位叙事。
- 边界页主动说明不适用情形，引用不确定时不得伪装成已核实事实。
- 配文从真实困境切入，补充使用动机，不逐句复述卡片。
- 品牌名称由 `theme.js` 的 `brand` 字段配置，不硬编码个人或组织品牌。

## 验收

至少完成以下检查：

- 校验脚本通过。
- 每个模型恰好六张卡，类型和顺序正确。
- `output/<id>-<name>/` 中存在六个非空 PNG。
- PNG 尺寸为 `1080 x 1440`。
- 封面可快速识别主题，定义页可独立理解，机制页表达关系而非装饰。
- 长文本没有被裁切，页脚、页码和标签没有拥挤或重叠。
- 配文包含读者入口、使用价值和必要标签，但不重复图片正文。

能查看图片时必须做视觉检查；无法查看时，明确说明只完成了结构与文件验证。

## 边界

- 不把现有业务品牌、账号数据、完整内容库或已发布成品默认放入公共 Skill。
- 不自动扩展到大批量生产；先用 1–3 组卡验证协议和视觉稳定性。
- 不把 Notion、飞书或 Figma 设为必需依赖，除非用户明确选择对应工作流。
- 删除、覆盖、移动、发布或修改外部账号前，取得用户明确确认。
