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

## Communication Preference

When resuming work, use:

- exact tab names
- exact tree locations
- one-step instructions

This is not cosmetic; it materially reduces ODC confusion.
