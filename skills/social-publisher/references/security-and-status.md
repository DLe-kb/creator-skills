# 安全、确认与结果状态

## 本地数据

默认运行目录：

```text
~/.config/open-creator/social-publisher/
├── profiles/<platform>/<account-alias>/
├── reports/
└── screenshots/
```

可以使用 `SOCIAL_PUBLISHER_HOME` 覆盖。不要把该目录放入内容项目或 Git 仓库。

## 发布确认

- `prepare` 只负责上传和填写。
- `publish` 必须同时出现 `--execute` 与 `--authorized`。
- 浏览器页面填写完成后，仍需人工输入 `PUBLISH` 才能点击最终发布按钮。
- 正式点击前再次打印平台、账号别名、content ID、视频 SHA-256、标题和可见范围。
- 验证码、二次确认、版权提示或平台警告出现时停止，让用户处理。

## 状态

| 状态 | 含义 |
| --- | --- |
| `validated` | 文件和字段通过本地校验 |
| `prepared` | 页面已填写，尚未点击发布 |
| `awaiting_confirmation` | 等待用户授权最终写入 |
| `published` | 已获得作品 ID、URL 或平台明确成功反馈 |
| `uncertain` | 已点击但无法确认平台是否创建作品 |
| `failed` | 已确认失败，保留错误和页面截图 |
| `skipped` | 用户或规则跳过该平台 |

## 重试

- 素材上传失败可以在确认没有创建作品后重试。
- 最终发布请求、页面点击超时或网络中断后不要自动重试。
- 先在创作者后台查询 content ID、标题和发布时间；仍不能确认时保持 `uncertain`。
