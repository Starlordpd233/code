# Wellness Summit Session Assignment System

## Purpose
Algorithmic scheduling system for a one-day peer school wellness event. Assigns 100-180 participants to workshop sessions across 2 time blocks, maximizing preference satisfaction under speaker/room constraints.

## Project Structure
```
wellness_summitt_schedule/
├── HW3-2.py                        # Stage 1: demand scoring + conflict matrix (COMPLETE)
├── README.md                       # Full project specification and algorithm details
├── Wellness Summit.docx            # Project documentation (Word)
└── Wellness Project Starter/
    ├── Classes.py                  # Data model: Talk, Participant, Occurrence, Room
    ├── main.py                     # Main pipeline (partially stubbed)
    ├── Sessions.csv                # 8 workshops with speaker info
    └── Rooms.csv                   # 6 rooms with capacities (250 total)
```

## Key Files

- **HW3-2.py** — Implements `compute_demand_scores()` and `build_conflict_matrix()`. Has mini test data with 4 talks and 3 participants. Run with `python HW3-2.py`.
- **Classes.py** — Core data model. `Talk`, `Room`, `Participant`, `Occurrence` classes. `Occurrence.add_participant()` and `remove_participant()` are incomplete.
- **main.py** — Orchestrates the full pipeline. Most function bodies are stubbed (`pass`/TODO). Loads CSVs via `load_objects()`.

## Algorithm Pipeline (5 phases)
1. **Demand Analysis** — Score talks by participant preference rankings (top-k weighted)
2. **Conflict Matrix** — Count how many participants rank both talks in top-k
3. **Create Occurrences** — Generate occurrence objects; popular flexible talks get 2 runs (max 12 total)
4. **Block Assignment** — Greedy conflict-aware placement into Block 1 vs Block 2
5. **Participant Assignment** — Assign each participant one session per block by preference
6. **Room Assignment** — Map occurrences to physical rooms (same room for double-run talks)

## Key Constraints
- **Speakers:** 5 single-block only (Athletes, International, Parents, Vulnerability, Grief); 3 flexible (Eating Disorders, Boys, Health Center)
- **Athletes** session is FIRST SESSION ONLY
- **Rooms:** 6 rooms, capacities 30-50. Max 1 occurrence per room per block. Double-run talks use same room both blocks.
- **Participants:** Exactly 1 session per block. Ranked preferences for all 8 talks.

## Configuration Constants
```
MIN_PARTICIPANTS_ABSOLUTE = 10
MIN_PARTICIPANTS_IDEAL = 15
CAPACITY_BUFFER_PERCENT = 0.10
NUM_WORKSHOP_BLOCKS = 2
NUM_SPACES = 6
NUM_SPEAKERS = 8
LOW_SATISFACTION_THRESHOLD = 3
```

## Current Status
- Stage 1 (HW3-2.py): **Complete** with tests
- Main project (main.py): **In progress** — framework set up, most functions stubbed
- Participants.csv: **Not yet available** (needed to run full system)

## Tech Stack
- Python 3, standard library only (csv module for data loading)
- No external dependencies

## Academic Integrity
This is graded coursework. Do not provide complete implementations. Guide the student with concepts, pseudocode, partial scaffolds, and debugging help per the parent CLAUDE.md policy.
