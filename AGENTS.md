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
python3 -m py_compile scripts/validate_design_flow.py
python3 -m unittest discover -s tests -v
```
