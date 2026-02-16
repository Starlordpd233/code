# Wellness Summit Session Assignment System

## 1. Project Overview

**Core Objective:** Develop an algorithmic system to optimally assign participants to workshop sessions for a one-day peer school wellness summit.

**Event Scale:**
- **Participants:** 100–180 attendees from multiple peer schools
- **Format:** One-day event with two workshop blocks
- **Content:** 8 distinct speakers/topics total
- **Venue:** 6 available workshop spaces (interchangeable)

## 2. Speaker & Session Constraints

### Speaker Availability Matrix
- **8 Total Speakers** (each covering 1 unique topic)
- **5 Speakers:** Limited to **1 block only** (either Block 1 or Block 2)
- **3 Speakers:** Available to run **2 sessions** (can be scheduled in both blocks, or twice in one block if demand requires)

### Session Requirements
- **Total Topics:** 8 distinct talk topics
- **Mandatory Coverage:** Every topic must run at least once
- **Minimum Capacity:** 10 participants (absolute minimum)
- **Ideal Capacity:** 15+ participants per session
- **Maximum Capacity:** Physical room capacity minus configurable buffer percentage (do not fill to absolute maximum)

## 3. Participant Assignment Logic

### Input Data Structure
- **Survey Data:** Participants rank topics by preference
- **Timestamp Priority:** Survey submission time preserved; used as tiebreaker when participants from different schools have identical priority rankings
- **School Affiliation:** Multiple participants may come from the same school

### Assignment Priorities
1. **Strategic Separation:** If two topics show high correlated demand (e.g., many participants rank "Mental Wellness" #1 and "Self-Care" #2), schedule these in **separate blocks** to maximize attendance satisfaction
2. **Geographic Optimization:** Place high-demand talks in strategically located spaces to manage foot traffic
3. **Capacity Management:** Prioritize filling minimum requirements (10–15 people) before optimizing for preferences

## 4. Algorithm Workflow

### Phase 1: Demand Analysis & Speaker Placement
- Analyze survey demand data to determine session popularity
- Decide which speakers are assigned to Block 1 vs. Block 2
- Determine which of the 3 flexible speakers run twice (based on demand volume)
- **Constraint:** Ensure minimum capacity requirements can be met for all scheduled sessions

### Phase 2: Initial Assignment
- Assign participants to first-choice sessions where possible
- Assign to second-choice when first-choice is over capacity or conflicting
- **Target:** Maximize first and second-choice assignments

### Phase 3: Optimization & Conflict Resolution
Implement a **cost-function-based heap** to resolve overfills:

**Cost Function Criteria:**
- Identify participants in overfilled sessions who have underfilled alternate choices
- **Good Move:** Moving a participant from an overfilled first-choice session to their underfilled second-choice session
- **Priority Queue:** Use min-heap or similar structure to efficiently identify optimal candidates for reassignment

### Phase 4: First-Come-First-Serve Arbitration
- For remaining conflicts where participants have identical priority rankings from different schools, use **survey submission timestamp** to determine priority

## 5. Output & Quality Assurance

### Satisfaction Monitoring
- **Low-Satisfaction Report:** Generate list of participants assigned to any of their **bottom 3 choices** (ranks 6–8 if 8 topics exist)
- **Threshold Logic:** 
  - If few participants receive low-tier assignments → Flag for manual review by Hathorn (suggests algorithmic adjustment needed)
  - If many participants receive low-tier assignments → Acceptable outcome (indicates demand distribution issues rather than assignment failure)

### Emergency Protocols
System must handle runtime changes:
- **Speaker Cancellation:** Remove speaker and reassign affected participants
- **Space Unavailability:** Reassign sessions to alternative spaces
- **Dynamic Rebalancing:** Capability to rerun optimization with updated constraints

## 6. Implementation Specifications

### Configurable Parameters (Global Variables)
```python
MIN_PARTICIPANTS_ABSOLUTE = 10      # Hard minimum per session
MIN_PARTICIPANTS_IDEAL = 15         # Soft target per session
CAPACITY_BUFFER_PERCENT = 0.10      # 10% buffer below physical max
NUM_WORKSHOP_BLOCKS = 2
NUM_SPACES = 6
NUM_SPEAKERS = 8
SPEAKERS_SINGLE_BLOCK = 5
SPEAKERS_DOUBLE_BLOCK = 3
LOW_SATISFACTION_THRESHOLD = 3      # Bottom N choices considered "low satisfaction"