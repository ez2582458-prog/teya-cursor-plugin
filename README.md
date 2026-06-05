# Teya Cursor Plugin

Teya is an autonomous Cursor plugin for end-to-end website production:
research, semantic core, AURA visual system, Aurora WordPress build team,
Excalibur blog articles, release gates, paint QA, and WordPress deploy support.

## Contents

- `agents/` — Cursor subagent prompts.
- `skills/` — role-specific skill contracts.
- `commands/` — user-facing workflow commands.
- `rules/` — workspace rules for orchestration.
- `scripts/` — validation, deploy, release-gate, WordPress and Excalibur utilities.
- `shared/` — data-flow contracts, templates, QA gates and examples.
- `vendor/` — bundled AURA/Yadryshko references.

## Install

Place this folder at:

```text
%USERPROFILE%\.cursor\plugins\local\teya
```

Then restart or reload Cursor.

## Runtime Data

Project outputs and secrets must live outside this plugin, usually in the
working project under:

```text
teya-memory/
```

Do not commit real credentials. Use `shared/teya.env.example` and
`shared/site.inv.example` as templates.

## Main Workflow

Start with:

```text
/teya-phase1
```

The current pipeline is split across focused agents:

```text
Research -> Core || AURA -> Aurora Team -> Aurora split build
-> Deploy/Media -> Report Compiler -> Excalibur -> Blog Integrator
-> Paint Evidence -> Release Gate -> Design Guardian -> QA
```

## Release Gate

For a built project, run:

```powershell
python teya/scripts/teya_release_gate.py --project-root <PROJECT_ROOT>
```

The gate must pass before any run can be considered production-ready.
