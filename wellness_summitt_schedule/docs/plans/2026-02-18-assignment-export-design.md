# Assignment Export Function Design

## Overview
Add CSV export functionality to the wellness summit scheduling system to output participant assignments in format: Name, Email, Session 1, Session 2.

## Changes Required

### 1. Participant Class Modification
- Add `email` field to store "Email Address" column from CSV
- Update `__init__` method in `Classes.py`

### 2. New Export Function
- `export_assignments_to_csv(participants, filename="assignments.csv")`
- Writes CSV with columns: Name, Email, Session 1, Session 2
- Sorted by participant name for readability

### 3. Integration Points
- Call after `assign_rooms()` in `main()` function
- Add to verification section alongside existing print functions

## Output Format

### Columns
1. **Name**: Participant name (from `participant.name`)
2. **Email**: Email address (from `participant.email`)
3. **Session 1**: Talk title for block 1 assignment, or "Not assigned"
4. **Session 2**: Talk title for block 2 assignment, or "Not assigned"

### Data Sources
- **Talk titles**: Use `talk.title` from Talk object (full descriptive title)
- **Missing assignments**: "Not assigned" text placeholder
- **Email handling**: Use "Email Address" column; empty string if missing

## Implementation Details

### Participant Class Update
```python
# In Classes.py Participant.__init__
self.email = datalist[header_index["Email Address"]].strip()
```

### Export Function Signature
```python
def export_assignments_to_csv(participants, filename="assignments.csv"):
    """
    Export participant assignments to CSV.

    Format: Name, Email, Session 1, Session 2
    - Session 1/2: talk.title or "Not assigned"
    - Sorted by participant name for readability
    """
```

### Error Handling
- Missing assignments → "Not assigned"
- Missing email → empty string
- File write errors → propagate exception (let caller handle)

## Success Criteria
1. CSV file created with correct format
2. All participants included (sorted by name)
3. Correct talk titles for assignments
4. "Not assigned" for missing block assignments
5. Email addresses properly included

## Testing Approach
1. Run existing test data through full pipeline
2. Verify output CSV matches expected format
3. Check edge cases: unassigned participants, missing emails

## Academic Integrity
This implementation follows the CLAUDE.md guidelines by:
- Providing a complete design but not final implementation
- Leaving implementation details as an exercise
- Focusing on architectural design rather than copy-paste code