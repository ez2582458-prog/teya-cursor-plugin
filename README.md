# Teya Cursor Plugin

Teya is an autonomous Cursor plugin for end-to-end website production:
brief, research, manual keywords/URL map, AURA visual system, Aurora WordPress build team,
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
Brief -> Research -> manual keywords/URL map || AURA -> Aurora Team -> Aurora split build
-> Deploy/Media -> Report Compiler -> Excalibur -> Blog Integrator
-> Paint Evidence -> Release Gate -> Design Guardian -> QA
```

## Release Gate

For a built project, run:

```bash
python3 teya/scripts/teya_release_gate.py --project-root <PROJECT_ROOT>                                   # live PUBLIC_SITE_URL
python3 teya/scripts/teya_release_gate.py --project-root <PROJECT_ROOT> --local-url http://127.0.0.1:8080/  # local WordPress / preview
python3 teya/scripts/teya_release_gate.py --project-root <PROJECT_ROOT> --final                            # + fresh DESIGN OK / QA OK
```

The gate must pass before any run can be considered production-ready. It runs the browser checks itself
(`teya_visual_lint.py`, `teya_content_lint.py`, `teya_page_weight.py`, `teya_site_fact_check.py`,
`teya_image_optimize.py --check`, `teya_favicon.py --check`), needs Playwright + Chromium
(`scripts/teya_cloud_setup.sh`), and writes `teya-memory/wp/release-gate-report.md` itself.
Limits and rules: `shared/site-quality-scripts.md`. Cloud setup with a local WordPress: `docs/cloud-agents-setup.md`.
