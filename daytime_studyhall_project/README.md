# Daytime Study Hall Scheduler — Requirements

This project is to create an application that schedules **Daytime Study Halls** (per the initial client meeting with Mrs. DiSciacca).

## Goals

- Generate study hall assignments for students across the cycle while respecting scheduling rules.
- Produce required export(s) for downstream systems, plus at least one human-readable report for staff review.

## Scheduling requirements (rules/constraints)

### Per-student requirements

- **Target assignments by grade**
  - **Grade 9**: **2** study halls per cycle
  - **Grade 10**: **1** study hall per cycle
- **Maintain at least one free period**: every student should keep **≥ 1 free block** (do not schedule away all free blocks).
- **Spacing rules**
  - No student should be scheduled on **consecutive days**.
  - Ideally, avoid study halls that are only **2 days apart** as well.

### Section/session requirements

- **Balance group sizes** across sections/sessions as much as possible.
- **Group size bounds**
  - **Max**: **35** students (client note: may be **28** — treat as a configurable cap)
  - **Min**: **4–5** students (treat as a configurable floor)

### Prioritization / preferences

- Prefer scheduling study halls in **2nd block** and **4th block** first.
- If needed, use **1st block** and **3rd block** next.

### Reporting requirements

- Provide some kind of information about **who received fewer than the desired number** of study halls (and ideally why, e.g., constraints prevented placement).

## Inputs

You will be given two CSV files:

- **Student free blocks CSV**: lists students and their free periods.
- **Available study hall blocks/sections CSV**: lists which blocks are available for daytime study.

Notes:

- Lunch blocks are **not included** in the provided block list. If you choose to support lunch as a study-hall option, you will need to insert **dummy lunch values** into the relevant spreadsheet(s) for now.
- Read/parse the files as **plain text** (do not rely on CSV-parsing packages that “do it for you”).
- See the class “Modules” materials for sample input files and the **database export specification**.

## Outputs

Your `schedule()` run should generate:

- **One required database export file** (per the provided spec).
- **At least one human-readable file** (e.g., a summary report of section sizes, students short of target, constraint violations prevented, etc.).

## Required public API (for the UI)

Because the UI will be provided separately, your scheduling code must expose **exactly these three functions** (use these names):

- `read_students(filename) -> str`
  - Reads/imports student data.
  - Returns a **user-facing status message** suitable for an alert dialog (success or error with actionable details).
- `read_sections(filename) -> str`
  - Reads/imports available sections/blocks data.
  - Returns a **user-facing status message** (success or error).
- `schedule() -> str`
  - Performs the scheduling “heavy lifting” using the rules above.
  - Generates the output files described above.
  - Returns a **user-facing status message** (e.g., summary counts + where outputs were written, or an error message).

## Design expectations

- Your implementation should be **fundamentally object-oriented**.
- Keep the required public functions **clean and thin** by pushing most logic into methods on your own classes.

### Suggested modeling (recommended)

- `**Student` class**: student identity, grade, free blocks, assigned study halls, and helper logic.
- `**Block` / `Session` class** (recommended): representing a specific block (and/or a study hall session) as an object can simplify:
  - prioritization (2nd/4th block first),
  - capacity checks (min/max),
  - “no consecutive days” validation,
  - balancing section sizes.

## Information on Block Schedule

There are 7 days in the schedule from D1-D7, and each day begins with the block of the same number (meaning D1 begins with B1, D2 with B2, D3 with B3, etc.). Each day only has 4 blocks, and the blocks go from one to the next. Example with D1 is as follows: begins with B1, and goes to B2, B3, B4. Example with D2 is: B2, B3, B4, B5, and so on. The caveat is that the blocks wrapps around 7 and starts back at 1 and should never exceed 7. An example is D7: B7, B1, B2, B3. There is a FIXED sequence of the day schedule in this particular order: D1, D5, D2, D6, D3, D7, D4.

## Engineering Decision for `schedule()`

- keeps people in the same grade in each study hall session if possible
- keep the separation of 2 days as soft ideal preference and not strict exclusion
- we will not implement and schedule study hall sections in third blocks because no third block offerings exist in current data of course offerings

