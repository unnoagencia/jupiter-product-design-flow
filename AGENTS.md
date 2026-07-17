# AGENTS.md

## Purpose

This repository contains a reusable design-process skill. Changes must improve process predictability, brand fidelity, execution discipline, or evidence quality.

## Rules

- Keep `SKILL.md` below 100,000 characters.
- Preserve valid YAML frontmatter at byte zero.
- Do not add generic design advice that does not change agent behavior.
- Put branch-specific detail in `references/`.
- Every workflow phase must end with a checkable completion criterion.
- Do not make dark mode, named aesthetics, or user confirmation mandatory by default.
- Visual review requires evidence, not code inspection alone.
- Run the reproducible validator test suite before committing.

## Verification

```bash
python3 -m pip install --requirement requirements.txt
npm ci
npx playwright install chromium
python3 -m py_compile scripts/validate_design_flow.py scripts/export_carousel.py tests/playwright_smoke.py
npm run check:node
npm run test:unit
npm run test:e2e
```

CI runs this verification on macOS and Ubuntu with Python 3.11 and 3.12. Keep `pyproject.toml`, `requirements.txt`, `package.json`, and `package-lock.json` aligned when dependencies or the release version change.
