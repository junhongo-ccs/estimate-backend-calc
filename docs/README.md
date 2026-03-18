# Documentation Map

This folder is the canonical handoff area for the OutSystems migration work.

## Read Order

When resuming work in a new conversation or with a different AI session, read these files in this order:

1. `master_status.md`
2. `api_contract.md`
3. `odc_notes.md`
4. `daily/2026-03-13.md` and any newer files in `daily/`

## File Roles

### `master_status.md`
- Single source of truth for current state
- Active milestone
- What already works
- What is blocked or deferred
- Exact next step

### `api_contract.md`
- Backend endpoints used for ODC
- Request/response shapes
- Current Railway URLs
- Which endpoint is for shortcut PoC vs production direction

### `odc_notes.md`
- ODC-specific constraints and recurring pitfalls
- UI behavior notes
- Known safe workflows

### `daily/`
- Day-by-day factual work log
- What changed that day
- What was achieved
- What remains

## Current Preferred Resume Prompt

When resuming in a new session, use:

`Please continue from docs/master_status.md in /Users/hongoujun/Documents/GitHub/estimate-backend-calc`

That should be enough context to restart efficiently.
