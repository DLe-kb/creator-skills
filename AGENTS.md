# Open Creator Repository Guidance

## Purpose

Open Creator is an open-source AI Skills toolkit for content creators. The repository may include tools for ideation, research, writing, image creation, video production, publishing, analytics, and creator workflows.

## Repository Rules

- Keep every published Skill independently installable, documented, and testable.
- Store Skill runtime files under `skills/<skill-name>/`.
- Keep human-facing documentation and examples under `docs/` and `examples/`.
- Do not commit secrets, personal data, private materials, machine-specific absolute paths, caches, or unrelated generated files.
- Do not add internal project-management files such as `PROJECT_STATE.md`, discussion queues, private notes, or task logs.
- Include only files that are useful to repository users, contributors, or maintainers.

## Adding Or Updating A Skill

1. Keep the Skill focused on one clear capability.
2. Ensure the directory name matches the `name` in `SKILL.md` frontmatter.
3. Keep `SKILL.md` concise and move detailed material into `references/`, deterministic operations into `scripts/`, and reusable output resources into `assets/`.
4. Add or update `agents/openai.yaml` when the Skill should appear in Codex interfaces.
5. Update the root `README.md`, `CHANGELOG.md`, related documentation, examples, and repository validation rules.
6. Run the Skill-specific checks and the repository validation.
7. Review the exact Git diff before committing.
8. Version Skill releases with tags in the form `<skill-name>-v<version>`.

## Validation

Run before committing:

```bash
python3 scripts/validate_repo.py
```

Also verify:

- Skill frontmatter and directory names match.
- `agents/openai.yaml` and the plugin manifest are valid.
- Required files, public links, examples, and documentation are complete.
- The repository contains no secrets, absolute local paths, placeholders, or `.DS_Store` files.
- `README.md`, `CHANGELOG.md`, and release tags match the published contents.
