# Contributing

感谢你改进 Open Creator。

## 贡献原则

- 从真实项目反复出现的问题出发，不为了“完整”增加 Skill。
- 一个 Skill 只承担边界清晰、可验证的能力；不要把多个不相关流程塞进同一个 Skill。
- 保持 `SKILL.md` 简洁，详细资料按需放入 `references/`，确定性操作优先放入 `scripts/`。
- 面向人的安装、案例和发布说明放在仓库级 `docs/`、`examples/` 或根目录。
- 不提交密钥、个人信息、本机绝对路径、业务项目产物或未确认版权的内容。

## 新增或修改 Skill

1. 将 Skill 放在 `skills/<skill-name>/`，目录名与 frontmatter 中的 `name` 保持一致。
2. 确保 `SKILL.md` 只包含 `name` 和 `description` 两个 frontmatter 字段。
3. 为需要展示在 Codex 中的 Skill 提供 `agents/openai.yaml`。
4. 在根 `README.md` 的 Skills 表格中登记。
5. 在 `CHANGELOG.md` 中记录变化。
6. 运行本地验证。

## 本地验证

```bash
python3 -m pip install -r requirements-dev.txt
python3 scripts/validate_repo.py
```

提交 Pull Request（拉取请求）时，请说明真实问题、能力边界、影响场景和验证证据。
