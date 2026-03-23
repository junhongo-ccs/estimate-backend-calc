# Documentation Map

This folder is the canonical handoff area for the OutSystems migration work.

## Read Order

When resuming work in a new conversation or with a different AI session, read these files in this order:

1. `status/master_status.md`
2. `api/api_contract.md`
3. `odc/odc_notes.md`
4. `daily/2026-03-13.md` and any newer files in `daily/`

## File Roles

### `status/`
- Current-state documents
- Resume points
- Antigravity-facing summaries

### `api/`
- API contracts and endpoint behavior

### `odc/`
- OutSystems / ODC-specific notes and migration docs

### `dify/`
- Dify workflow plans and next-step notes

### `presentation/`
- Demo and presentation story docs

### `guides/`
- End-user manuals and operator guides

### `daily/`
- Day-by-day factual work log

### `dify/dify_document_output_version_plan_2026-03-23.md`
- Plan for duplicating the current Dify estimate app
- Minimal sequence for estimate-document output
- Workflow node wiring for the document version
- New code needed to convert `calc_json` into PDF input

### `status/master_status.md`
- Single source of truth for current state
- Active milestone
- What already works
- What is blocked or deferred
- Exact next step

### `status/antigravity_dify_pricing_handoff_2026-03-23.md`
- Detailed write-up of the estimate-app -> price-simulator handoff
- Why the two-app Dify structure is intentional
- What was changed in runtime and repo
- What is demo-ready now

### `api/api_contract.md`
- Backend endpoints used for ODC
- Request/response shapes
- Current Railway URLs
- Which endpoint is for shortcut PoC vs production direction

### `guides/USER_MANUAL.md`
- Current end-user guide for the Dify two-app operation
- Estimate app -> pricing simulator handoff procedure
- Copy/paste JSON usage
- Non-technical operating instructions

### `presentation/presentation_dify_story_2026-03.md`
- Presentation storyline for the Dify demo
- Talking points for the two-app handoff story
- Reference links for slide prep and recorded demo context

### `odc/odc_notes.md`
- ODC-specific constraints and recurring pitfalls
- UI behavior notes
- Known safe workflows

## Current Preferred Resume Prompt

When resuming in a new session, use:

`Please continue from docs/status/master_status.md in /Users/hongoujun/Documents/GitHub/estimate-backend-calc`

That should be enough context to restart efficiently.
