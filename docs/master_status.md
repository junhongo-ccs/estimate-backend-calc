# Master Status

## Objective

Recreate the Dify-based AI estimation PoC in OutSystems ODC, starting with a minimal but real end-to-end path:

- ODC UI
- Railway-hosted backend
- estimation result returned and displayed

The immediate goal is not full parity yet. The immediate goal is stable ODC-to-backend integration with visible business output.

## Current State

As of 2026-03-19:

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
- `DoTestCalculate` passes all three into:
  - `GetCalculateSimpleGet.screen_count`
  - `GetCalculateSimpleGet.table_count`
  - `GetCalculateSimpleGet.department`
- The backend route `GET /calculate_simple_get` accepts `department` as the formal department name string.
- `EstimateForm` now uses a working `Dropdown` for `Department`.
- The dropdown is wired as:
  - `Dropdown1.Variable = Client.Department`
  - `Dropdown1.List = GetDepartmentMasters.List`
  - `Dropdown1.Options Text = DepartmentMaster.DisplayName`
  - `Dropdown1.Options Value = DepartmentMaster.DisplayName`
- `Client.Department` is `Text`.
- `GetDepartmentMasters` is configured with:
  - source: `DepartmentMaster`
  - filter: `DepartmentMaster.Is_Active = True`
  - sorting: `DepartmentMaster.Order (ASC)`
- `DepartmentMaster` now contains the BS department master data required by the dropdown.
- Browser verification is complete for:
  - changing `screen_count`
  - changing `table_count`
  - changing `department`
- Department change is confirmed to affect the estimate result when switching across departments with different coefficients.
- There are currently no blocking ODC validation errors or warnings related to the old unused parsing action; the unused `ParseEstimateResponse` action has been removed.
- Windows ODC Studio publish remains historical troubleshooting context only. The current trusted working path is Mac ODC Studio plus the live server-side app state.

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
  - `Department` dropdown backed by `DepartmentMaster`
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

This milestone is now achieved for `department`.

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
3. Use the current `DepartmentMaster` data and dropdown wiring as the baseline
4. Continue expanding additional business inputs without regressing the current end-to-end flow
5. Verify in the browser after each change that:
   - `Department` still renders as a dropdown
   - formal department names are shown
   - selecting a department still updates the backend result correctly

## Success Condition For The Next Session

The next milestone is complete when:

- the existing department dropdown still works after further changes
- the backend still receives the exact formal department value
- the displayed result still updates correctly while new business inputs are added

## Current Resume Point

If work resumes in a new session, start from:

1. Treat the current Dify workflow as the primary implementation track
2. Use the full Dify workflow-compatible logic file:
   - `/Users/hongoujun/Documents/GitHub/estimate-backend-calc/dify_estimate_logic_full_for_workflow.py`
3. Align the Dify input UI with the calculation logic so visible inputs are truly reflected in the result
4. Keep the current OutSystems work as supporting validation context, not the main delivery path
5. Continue with Dify-centered demo hardening and presentation preparation

## Source Files

- Backend:
  - `/Users/hongoujun/Documents/GitHub/estimate-backend-calc/outsystems_api_wrapper.py`

- Docs:
  - `/Users/hongoujun/Documents/GitHub/estimate-backend-calc/docs/api_contract.md`
  - `/Users/hongoujun/Documents/GitHub/estimate-backend-calc/docs/odc_notes.md`
  - `/Users/hongoujun/Documents/GitHub/estimate-backend-calc/docs/daily/2026-03-13.md`
  - `/Users/hongoujun/Documents/GitHub/estimate-backend-calc/docs/daily/2026-03-14.md`
  - `/Users/hongoujun/Documents/GitHub/estimate-backend-calc/docs/daily/2026-03-17.md`
