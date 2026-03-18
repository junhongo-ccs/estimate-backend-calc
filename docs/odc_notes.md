# ODC Notes

## Why The Current Flow Uses GET

ODC repeatedly caused friction when binding POST request structures.

Observed issues:
- request structure type not visible where expected
- local variable type picker inconsistent across contexts
- request parameters appearing but not bindable cleanly
- repeated `Request` validation loops

To keep momentum, the current PoC uses:

- `GET /calculate_test`
- then `GET /calculate_simple_get`

This is intentional, not accidental.

## Safe Working Pattern

When working in ODC:

1. Give instructions using exact tabs
   - `Logic`
   - `Interface`
   - `Data`

2. Give one action at a time
   - user gets lost if multiple jumps are packed together

3. Prefer GET query params over POST request binding for now

4. Use ODC flow nodes in this order:
   - backend call
   - `JSON Serialize` if raw JSON text is needed
   - `Assign` into screen variables

## Current Screen Variables

On `EstimateForm`, these variables are already in use:

- `RawCalcJson`
- `EstimatedAmount`
- `TotalManDays`
- `EstimatedRange`
- `Client.Department`
- `Client.ScreenCount`
- `Client.TableCount`

## Current UI State

The screen already shows:

- temporary `Department` selector
- `Screen Count` input
- `Table Count` input
- `Run Estimate` button
- `Estimated Amount`
- `Total Man Days`
- `Estimated Range`
- those values are coming from `GetCalculateSimpleGet`, not from the old fixed test route

This is enough as a baseline.

## Recommended Next UI Change

Do not redo the current two-input work.

The current next change should be:

- keep the existing dynamic inputs intact
- keep the current `department` flow intact
- replace the temporary department radio group with a proper dropdown
- use only formal department names as choices

## Known ODC Pitfalls

### 1. Wrong Tab Context

The same item can be hard to find depending on whether the user is in:
- `Interface`
- `Logic`
- `Data`

Always specify the tab first.

### 2. Double Click Matters

Opening a Client Action often requires double click.
Single click may only select it, not open the flow canvas.

### 3. Widget Placement Is Sensitive

Inside `MainContent`, controls may align unexpectedly.

Preferred workaround:
- use one `Container` per row
- put simple widgets inside each row container
- when the page starts looking wrong, first stabilize layout before adding more bindings
- when a richer widget starts blocking progress, use the simplest temporary selector that preserves correct values

### 4. Raw JSON vs Structured Display

Raw JSON was useful to prove the backend call works.
Now that structured values are visible, raw JSON should be considered secondary.

### 5. Reliable Current Flow

The currently working action flow is:

1. `GetCalculateSimpleGet`
2. `JSON Serialize`
3. `Assign` into display variables
4. `Assign` raw JSON string

Do not replace this flow structure during the next session.
The hardcoded query values have already been replaced by:

- `Client.Department`
- `Client.ScreenCount`
- `Client.TableCount`

Do not disrupt this working binding while adding the next parameter.

## Concrete Current Working State

`EstimateForm` currently works with:

- a temporary `Department` selector
- two numeric inputs
- labels above the inputs
- `DoTestCalculate` as the button action
- `GetCalculateSimpleGet` as the backend call

One confirmed browser case:

- `department = ＣＳ第１システム開発部`
- `screen_count = 4`
- `table_count = 7`
- the result changes from the previous default-department case

## Department UI Direction

Current state:

- free-text department input was only a temporary step
- a temporary `Radio Group` now works
- this is not the target UI because the real department count is 10+

Preferred next state:

- `Department` should become a `Dropdown`
- the dropdown should expose formal department names only
- do not go back to free text

## Department Dropdown Reproduction Guide

Use this section if you need to recreate the dropdown on Mac from the current server-side app state without trusting the Windows-local OML.

### Goal

Replace the temporary `Department` radio selector with a proper dropdown while preserving the already-working backend call path.

### Do Not Change

- Do not change `DoTestCalculate`
- Do not change the `GetCalculateSimpleGet` action flow structure
- Do not revert to free-text department input
- Do not switch the backend route away from `GetCalculateSimpleGet`
- Do not change the existing bindings for:
  - `Client.Department`
  - `Client.ScreenCount`
  - `Client.TableCount`

### Final Intended Dropdown Wiring

The final widget wiring should be:

- `Dropdown1.Variable = Client.Department`
- `Dropdown1.List = GetDepartmentMasters.List`
- `Dropdown1.Options Text = DepartmentMaster.DisplayName`
- `Dropdown1.Options Value = DepartmentMaster.DisplayName`

### Final Intended Aggregate Wiring

Create a screen aggregate named:

- `GetDepartmentMasters`

Configure it as:

- Source:
  - `DepartmentMaster`
- Filter:
  - `DepartmentMaster.Is_Active = True`
- Sorting:
  - `DepartmentMaster.Order (ASC)`

### Why DisplayName Must Be Used As The Value

The backend currently expects the formal department name string in the query parameter:

- `department`

Therefore, the dropdown must send:

- `DepartmentMaster.DisplayName`

Do not send:

- `DepartmentMaster.Id`

If you send the ID, the backend request will no longer match the current contract.

### Actual Working Reconstruction Sequence

Follow this sequence exactly.

1. Open `EstimateForm` in the `Interface` tab.
2. Find the current temporary `Radio Group` used for `Department`.
3. Confirm it is bound to:
   - `Client.Department`
4. Add a new `Dropdown` near the current department selector.
5. Set the dropdown `Variable` to:
   - `Client.Department`
6. Do not delete the old radio group yet.
7. Create a new screen aggregate under `EstimateForm`:
   - `GetDepartmentMasters`
8. Add `DepartmentMaster` as the source.
9. Add the filter:
   - `DepartmentMaster.Is_Active = True`
10. Add sorting:
   - `DepartmentMaster.Order (ASC)`
11. Return to the new dropdown.
12. Set:
   - `List = GetDepartmentMasters.List`
13. For `Options Text`, choose:
   - `DepartmentMaster.DisplayName`
14. For `Options Value`, choose:
   - `DepartmentMaster.DisplayName`
15. Only after the dropdown is fully wired, remove or hide the temporary radio group if the environment allows it.

### Failed Approach That Looked Promising But Should Be Avoided

This was tried and should not be the primary route:

- creating a local variable like `DepartmentOptions`
- making it a text list
- trying to bind the dropdown directly to that text list

Why this was abandoned:

- the dropdown did not reliably expose the expected text-field suggestions
- ODC behaved as if it wanted record attributes, not a simple text list

If you start seeing empty or missing suggestions for `Options Text` / `Options Value`, switch to the aggregate approach above.

### What You Should Expect To See In ODC

When the aggregate is wired correctly, the dropdown suggestion list should include:

- `DepartmentMaster.Id`
- `DepartmentMaster.Label`
- `DepartmentMaster.Order`
- `DepartmentMaster.Is_Active`
- `DepartmentMaster.DisplayName`

At that point:

- choose `DepartmentMaster.DisplayName` for both display and value

### Preview / Permission Noise That Is Not The Main Problem

During the Windows attempt, the aggregate preview showed:

- `403 - Forbidden`

That preview failure did not mean the aggregate definition itself was wrong.
Treat preview failure separately from actual screen wiring.

### Publish / Environment Notes

Windows ODC Studio reached save/upload but failed on publish with:

- `Your current role doesn't allow you to perform this action in this app. (Forbidden)`

Do not spend more time trying to recover the Windows publish path.
Current operating assumption:

- Windows ODC Studio is not trusted for future ODC work on this task
- all future ODC work should be done on Mac

### If Rebuilding From Scratch On Mac

The success checklist is:

1. `EstimateForm` still shows:
   - `Screen Count`
   - `Table Count`
   - `Run Estimate`
2. `DoTestCalculate` still calls:
   - `GetCalculateSimpleGet`
3. `Department` is a dropdown, not radio or free text
4. Dropdown value is the formal department name
5. Browser verification still works for:
   - department change
   - screen count change
   - table count change

## Communication Preference

When resuming work, use:

- exact tab names
- exact tree locations
- one-step instructions

This is not cosmetic; it materially reduces ODC confusion.
