# Repository Guidance

## Purpose

This repository publishes multiple reusable Codex and AI Agent skills under `skills/`.

## Working rules

- Keep each runtime skill folder concise and directly useful to an agent.
- Keep human-facing installation, examples, contribution, and release documentation at repository root or under `docs/` and `examples/`.
- Give each skill an independent folder, validation path, changelog entry, and release tag.
- Do not add secrets, private data, machine-specific absolute paths, generated artifacts, or business-project files.
- Run `python3 scripts/validate_repo.py` before committing.
- Update `README.md` and `CHANGELOG.md` when a public skill is added or changed.

## Release checks

- Validate every Skill frontmatter and the repository plugin manifest.
- Check links, required files, and the exact Git diff.
- Use tags in the form `<skill-name>-v<version>`.
