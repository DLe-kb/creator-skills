# 规格来源与核验记录

最近核验：2026-08-04。

## 抖音

- 上传视频：https://open.douyin.com/platform/resource/docs/openapi/video-management/douyin/create/upload/
- 创建视频：https://open.douyin.com/platform/resource/docs/openapi/video-management/douyin/create/create-video
- 用户类型及权限：https://open.douyin.com/platform/resource/docs/accession-guide/type-and-permission
- 付费常见问题：https://open.douyin.com/platform/resource/docs/common-question/payment-common-question
- 标题、描述、封面、共创、可见范围和定时字段来自创作者中心当前发布界面观察。

## 小红书

- 创作服务平台：https://creator.xiaohongshu.com/
- 标题、正文、封面、章节、合集、原创声明、可见范围和定时字段来自发布界面观察。
- 没有把未找到的普通创作者公开视频发布 API 描述为绝对不存在；接入前应再次检查开放平台。

## 视频号

- 视频号助手：https://channels.weixin.qq.com/
- 时长、大小、分辨率、码率、格式和发布字段来自视频号助手发布界面观察。
- 没有把未找到的普通视频号公开视频发布 API 描述为绝对不存在；接入前应再次检查官方能力。

## YouTube

- 上传视频帮助：https://support.google.com/youtube/answer/57407
- 缩略图帮助：https://support.google.com/youtube/answer/72431
- `videos.insert`：https://developers.google.com/youtube/v3/docs/videos/insert
- 配额计算：https://developers.google.com/youtube/v3/determine_quota_cost
- 配额与合规审查：https://developers.google.com/youtube/v3/guides/quota_and_compliance_audits

## X

- X API 文档：https://docs.x.com/x-api/
- X API 费用应以 Developer Console 和当前官方定价页为准。
- 2026 年公开资料交叉验证显示新开发者采用按量计费，免费模式因此固定使用本机浏览器，不把 API 费用数字写死在执行器中。

## TikTok

- Content Posting API：https://developers.tiktok.com/doc/content-posting-api-get-started
- Query Creator Info：https://developers.tiktok.com/doc/content-posting-api-reference-query-creator-info
- Media Transfer Guide：https://developers.tiktok.com/doc/content-posting-api-media-transfer-guide
- Content Sharing Guidelines：https://developers.tiktok.com/doc/content-sharing-guidelines
- 网页 30GB、60 分钟、描述 4000 字符等字段来自 TikTok Studio 当前上传界面观察。

## 截图处理

用户提供的原始界面截图仅用于本地识别字段，不进入公共 Skill。公开资料只保留脱敏后的字段、限制、来源类型和核验日期。
