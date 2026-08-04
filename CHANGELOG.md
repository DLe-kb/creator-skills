# Changelog

本仓库中的 Skill 独立版本化。发布标签使用 `<skill-name>-v<version>`。

## social-publisher 0.1.0 - 2026-08-04

- 发布免费、本机优先的多平台视频发布 Skill。
- 支持 B站 `biliup` 路由、五个平台可见浏览器路线和 YouTube Data API 免费配额路线。
- 提供统一发布包、平台字段与素材规格校验、任务指纹和重复发布保护。
- 正式发布必须同时使用 `--execute --authorized`，不确定结果不自动重试。
- 登录态、OAuth token、报告和截图全部保存在公共仓库之外。

## mental-model-info-cards 0.1.0 - 2026-08-02

- 发布六张式思维模型与概念知识信息卡 Skill。
- 提供通用卡组协议、内容质量规则和发布配文标准。
- 提供不依赖第三方前端框架的 HTML/CSS/JS 渲染模板。
- 提供项目初始化、结构校验、Chrome PNG 导出和六张示例输出。
- 提供可配置品牌、配色和模型数据的独立项目模板。

## project-harness 0.1.0 - 2026-08-02

- 发布首个 `project-harness` Skill。
- 提供最小、持续和长期项目的渐进式协作结构。
- 提供项目状态拆分、阶段契约、返工闭环和 Skill 化边界。
- 增加 Codex plugin manifest（插件清单）、公开文档、最小示例和 CI 验证。
- 作为 Open Creator 多 Skill 仓库中的首个能力发布。
