# Master Status

## Objective

Recreate the Dify-based AI estimation PoC in OutSystems ODC, starting with a minimal but real end-to-end path:

- ODC UI
- Railway-hosted backend
- estimation result returned and displayed

The immediate goal is not full parity yet. The immediate goal is stable ODC-to-backend integration with visible business output.

## Current State

As of 2026-03-17:

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
- The current UI state uses a temporary `Radio Group` for `Department` with a few fixed choices.
- That radio-based solution works as a PoC, but it is not the desired final UI because the real number of departments is 10+.
- The agreed next UI direction is:
  - replace the temporary radio group
  - move `Department` to a proper `Dropdown`
  - keep formal department names as the selectable values

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
  - temporary `Department` selector
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
3. Replace the temporary `Department` radio group with a proper `Dropdown`
4. Populate that dropdown with the formal department names used by the backend
5. Expand additional business inputs only after the department selector is stabilized

## Success Condition For The Next Session

The next milestone is complete when:

- `Department` is no longer free text
- `Department` is no longer represented by a temporary radio group
- the user can choose from formal department names in a dropdown
- the backend receives the exact formal value
- the displayed result still updates correctly

## Current Resume Point

If work resumes in a new session, start from:

1. Open `EstimateForm` in ODC
2. Confirm the current browser still updates when changing:
   - `Department`
   - `Screen Count`
   - `Table Count`
3. Keep the current `DoTestCalculate` flow intact
4. Replace the temporary `Department` radio selector with a dropdown
5. Use formal department names only; do not go back to free-text department input

## Source Files

- Backend:
  - `/Users/hongoujun/Documents/GitHub/estimate-backend-calc/outsystems_api_wrapper.py`

- Docs:
  - `/Users/hongoujun/Documents/GitHub/estimate-backend-calc/docs/api_contract.md`
  - `/Users/hongoujun/Documents/GitHub/estimate-backend-calc/docs/odc_notes.md`
  - `/Users/hongoujun/Documents/GitHub/estimate-backend-calc/docs/daily/2026-03-13.md`
  - `/Users/hongoujun/Documents/GitHub/estimate-backend-calc/docs/daily/2026-03-14.md`
  - `/Users/hongoujun/Documents/GitHub/estimate-backend-calc/docs/daily/2026-03-17.md`
