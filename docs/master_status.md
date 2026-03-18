# Master Status

## Objective

Recreate the Dify-based AI estimation PoC in OutSystems ODC, starting with a minimal but real end-to-end path:

- ODC UI
- Railway-hosted backend
- estimation result returned and displayed

The immediate goal is not full parity yet. The immediate goal is stable ODC-to-backend integration with visible business output.

## Current State

As of 2026-03-18:

- Railway backend is live and reachable.
- ODC can call the backend successfully.
- UTF-8 response handling is fixed, and yen/range text renders correctly in ODC.
- The active ODC action flow uses `GetCalculateSimpleGet`.
- `EstimateForm` has working user-editable inputs for:
  - `screen_count`
  - `table_count`
  - `department`
- Those values are bound in ODC through:
  - `Client.ScreenCount`
  - `Client.TableCount`
  - `Client.Department`
- `DoTestCalculate` now passes all three into:
  - `GetCalculateSimpleGet.screen_count`
  - `GetCalculateSimpleGet.table_count`
  - `GetCalculateSimpleGet.department`
- The backend route `GET /calculate_simple_get` has also been extended to accept `department`.
- Dynamic input has been verified in the browser for both counts and department changes.
- One confirmed department-sensitive case is:
  - `department = ＣＳ第１システム開発部`
  - `screen_count = 4`
  - `table_count = 7`
  - result changes from the previous default-department case
- On Windows ODC Studio, `EstimateForm` was updated locally so `Department` now uses a proper `Dropdown`.
- That dropdown is wired as:
  - `Dropdown1.Variable = Client.Department`
  - `Dropdown1.List = GetDepartmentMasters.List`
  - `Options Text = DepartmentMaster.DisplayName`
  - `Options Value = DepartmentMaster.DisplayName`
- `GetDepartmentMasters` was added on the screen side with:
  - source: `DepartmentMaster`
  - filter: `DepartmentMaster.Is_Active = True`
  - sorting: `DepartmentMaster.Order (ASC)`
- The old temporary radio-based department selector is no longer the target direction.
- However, the updated ODC screen has not yet been published successfully from Windows.
- `1-Click Publish` on Windows ODC Studio reaches save/upload but ends with:
  - `Your current role doesn't allow you to perform this action in this app. (Forbidden)`
- Browser access to the personal ODC environment still works, and Mac ODC Studio does not show the same behavior.
- The latest working local artifact was exported/saved as:
  - `C:\Users\hongouj\OneDrive - NTT DATA\ドキュメント\OSML\AI Estimation System.oml`
- That `.oml` was then copied into this repository for handoff on branch:
  - `codex/odc-dropdown-transfer`
- Repository handoff path:
  - `OML/AI Estimation System.oml`
- Later verification showed that Mac cannot reliably open/use that `.oml` handoff path for this task.
- Therefore, the practical resume strategy is now:
  - do all future ODC work on Mac only
  - treat the Windows OML as historical evidence of the attempted configuration
  - reproduce the dropdown changes directly in the Mac-hosted ODC app by following the documented steps

## What Works

### Backend

- `GET /calculate_test`
  - fixed test endpoint
  - no request payload needed
  - used to prove first E2E flow

- `GET /calculate_simple_get?screen_count={screen_count}&table_count={table_count}`
  - now also supports `department`
  - minimal dynamic endpoint
  - lets ODC pass the currently stabilized PoC variables
  - avoids complex POST request-structure binding in ODC
  - already consumed successfully in ODC
  - already wired into the current ODC action flow

### ODC

- `EstimateForm` screen exists
- button triggers an action flow
- action can call Railway backend
- ODC variables are updated from backend response
- visible output is already on screen
- user can type `screen_count`
- user can type `table_count`
- user can now change `department`
- current screen includes:
  - the last confirmed server-side screen still needs the `Department` dropdown re-applied on Mac
  - `Screen Count` input
  - `Table Count` input
  - `Run Estimate` button
  - three displayed values for amount, man-days, and range
- current action flow is:
  - `GetCalculateSimpleGet`
  - `JSON Serialize`
  - `Assign`
  - `Assign`

## What Is Intentionally Deferred

- Full Dify-equivalent POST request binding in ODC
- Rich natural-language report generation in ODC
- Password gate refinement
- Advanced UI polish
- RAG integration
- Full production data model

## Active Milestone

### Milestone A: Stable Dynamic Input PoC

Definition:

- User changes `screen_count`
- User changes `table_count`
- ODC calls backend with those values
- amount/days/range update accordingly

This milestone is now achieved.

### Milestone B: Expand Business Inputs

Definition:

- add more business-relevant inputs beyond counts
- start with `department`
- extend backend contract and ODC bindings in small increments
- keep the current GET-based working loop stable while expanding inputs

This milestone is now started and partially achieved.

## Main Technical Strategy

Use a staged backend interface:

1. `calculate_test`
   - fixed GET
   - proved ODC integration

2. `calculate_simple_get`
   - dynamic GET with screen/query params
   - current recommended route for ODC
   - already integrated into the action flow
   - now using screen-bound ODC variables inside the action
   - currently proven for:
     - `screen_count`
     - `table_count`
     - `department`

3. Only after the ODC flow is stable:
   - revisit richer POST contracts

This is a deliberate workaround for ODC request-typing friction.

## Main Blocker History

The dominant blocker was ODC request structure binding for POST methods.

Symptoms included:
- request shape not recognized
- local variable type not appearing where expected
- `Request` parameter validation loops
- hard-to-predict UI behavior in ODC

This is why the current preferred route uses GET query params for the PoC phase.

## Exact Next Step

In ODC:

1. Keep `DoTestCalculate` wired to `GetCalculateSimpleGet`
2. Preserve the already-working dynamic inputs for:
   - `department`
   - `screen_count`
   - `table_count`
3. On Mac ODC Studio, open the current app/server version of `EstimateForm`
4. Re-apply the `Department` dropdown using the exact reproduction steps in `docs/odc_notes.md`
5. Publish from Mac ODC Studio
6. Verify in the browser that:
   - `Department` renders as a dropdown
   - formal department names are shown
   - selecting a department still updates the backend result correctly
7. Only after publish is verified, continue expanding additional business inputs

## Success Condition For The Next Session

The next milestone is complete when:

- the user can choose from formal department names in a dropdown
- the backend receives the exact formal value
- the displayed result still updates correctly

## Current Resume Point

If work resumes in a new session, start from:

1. Read `docs/odc_notes.md` first for the exact dropdown reproduction steps
2. On Mac ODC Studio, open the current app version of `EstimateForm`
3. Recreate the `Department` dropdown directly in the app
4. Keep the existing `DoTestCalculate` / `GetCalculateSimpleGet` flow intact
5. Publish from Mac
6. Verify browser behavior for:
   - `Department`
   - `Screen Count`
   - `Table Count`
7. Do not revert to free-text department input

## Source Files

- Backend:
  - `/Users/hongoujun/Documents/GitHub/estimate-backend-calc/outsystems_api_wrapper.py`

- Docs:
  - `/Users/hongoujun/Documents/GitHub/estimate-backend-calc/docs/api_contract.md`
  - `/Users/hongoujun/Documents/GitHub/estimate-backend-calc/docs/odc_notes.md`
  - `/Users/hongoujun/Documents/GitHub/estimate-backend-calc/docs/daily/2026-03-13.md`
  - `/Users/hongoujun/Documents/GitHub/estimate-backend-calc/docs/daily/2026-03-14.md`
  - `/Users/hongoujun/Documents/GitHub/estimate-backend-calc/docs/daily/2026-03-17.md`
