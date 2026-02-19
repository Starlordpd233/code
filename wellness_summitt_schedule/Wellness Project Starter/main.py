import csv
from typing import Any
from Classes import *

CAPACITY_BUFFER_PERCENT = 0.1
# ---------------------------
# Load Data
# ---------------------------

def load_objects(filename, cls, key_attr):
    """
    Generic CSV loader.

    filename:  path to CSV
    cls:       class to construct (init must accept (datalist, header_index))
    key_attr:  attribute name to key the returned dictionary on

    Returns: dictionary mapping obj.<key_attr>:obj
    """
    objects = {}

    with open(filename, 'r', newline='', encoding='utf-8') as file:
        data = list(csv.reader(file))

    headers = data[0]
    headers[0] = headers[0].lstrip("\ufeff") #remove BOM Character
    header_index = {headers[i]: i for i in range(len(headers))}

    for row in data[1:]:
        #skip empty rows
        if not row or all(cell.strip() == "" for cell in row):
            continue

        obj = cls(row, header_index)
        key = getattr(obj, key_attr)
        objects[key] = obj

    return objects

# ---------------------------
# Demand (interest)
# ---------------------------

def compute_demand_scores(talks:dict, participants:dict, top_k=5):
    """
    Compute a demand_score for each talk based on participant rankings.

    Baseline scoring rule:
    - Only consider each participant's top_k choices
    - Give points:
        rank 0 (top choice) -> top_k points
        rank 1 -> top_k-1 points
        ...
        rank top_k-1 -> 1 point
    - Talks outside top_k get 0 points from that participant

    Parameters:
      talks: dictionary talk_id:Talk
      participants: dictionary participant_name:Participant
      top_k: int

    Output:
      Mutates each Talk object's .demand_score
    """

    if top_k <= 0:
      for talk in talks.values():
        talk.demand_score = 0

    #reset step
    for talk in talks.values():
      talk.demand_score = 0 
    
    for participant in participants.values():
      ranked = participant.ranked_talk_ids

      k = min(top_k, len(ranked))

      for i in range(k):
        talk_id = ranked[i]
        points = top_k - i
        talks[talk_id].demand_score += points



# ---------------------------
# Conflicts (overlap)
# ---------------------------

def build_conflict_matrix(talks:dict, participants:dict, top_k=5):
    """
    Build a conflict matrix:
      conflict[(a,b)] = number of participants who have BOTH a and b in their top_k.

    IMPORTANT (for later integration):
    - Store BOTH directions:
        conflict[(a,b)] and conflict[(b,a)]
      so other code can do: conflict[(talk_id, other_id)] without worrying about order.

    Parameters:
      talks: dictionary talk_id:Talk
      participants: dictionary participant_name:Participant
      top_k: int

    Returns:
      conflict: dictionary (talk_id, talk_id):int conflict score
    """
    conflict = {}

    talk_ids = list(talks.keys())
    talk_ids.sort()

    for a in talk_ids:
      for b in talk_ids:
        conflict[(a,b)] = 0
    
    for participant in participants.values():
      ranked = participant.ranked_talk_ids

      k = min(top_k, len(ranked))
      top = ranked[:k]

      for i in range(len(top)):
        for j in range(i+1, len(top)):
          a = top[i]
          b = top[j]

          conflict[(a,b)] += 1
          conflict[(b,a)] += 1


    return conflict

# ---------------------------
# Occurrence creation
# ---------------------------

def create_occurrences(talks, max_total_occurrences):
    """
    Create Occurrence objects for each Talk.

    Rules:
    1. Every talk must have at least one occurrence.
    2. Some talks may have a second occurrence if:
        - talk.max_runs == 2
        - AND there is remaining capacity in the schedule.
    3. Total number of occurrences created may NOT exceed max_total_occurrences.

    """
    occurrences = []

    # Step 1: create one occurrence per talk
    for talk in talks.values():
        occ1 = Occurrence(talk.talk_id + "_1", talk)
        talk.occurrences.append(occ1)
        occurrences.append(occ1)


    eligible_talks = [talk for talk in talks.values() if talk.max_runs == 2]
    eligible_talks.sort(reverse=True)

    for talk in eligible_talks:
        if len(occurrences) < max_total_occurrences:
            occ2 = Occurrence(talk.talk_id + "_2", talk)
            talk.occurrences.append(occ2)
            occurrences.append(occ2)

    return occurrences

# ---------------------------
# Block assignment (conflict-aware)
# ---------------------------

def block_cost(talk_id, target_block, block_talk_ids, conflict):

    """
    Cost of putting talk_id into target_block:
    sum of conflict(talk_id, other) for all talks already in that block.
    """
    total = 0
    for other_id in block_talk_ids[target_block]:
        total += conflict.get((talk_id, other_id), 0)
    return total


def assign_blocks_conflict_aware(occurrences, conflict):
    """
    Assign each occurrence.block to 1 or 2 using a greedy overlap-minimizing strategy.

    Key idea:
    - Place Talks with two occurrences one into each block
    - Sort remaining talks and process from most demand to least
        - For each occurrence, choose block with lower conflict cost.
    """

    # Track which talk IDs are already placed in each block
    block_talk_ids = {1: [], 2: []}


    # TODO: if talk has 2 occurrences:
    #   place one in each block
    talk_w_2_occurrences = set()

    for occ in occurrences:
      if len(occ.talk.occurrences) == 2:
        talk_w_2_occurrences.add(occ.talk)
    
    for talk in talk_w_2_occurrences:
      talk.occurrences[0].block = 1
      talk.occurrences[1].block = 2

      block_talk_ids[1].append(talk.talk_id)
      block_talk_ids[2].append(talk.talk_id)



    # TODO: if talk has only 1 occurrence:
    #   choose block 1 or 2 based on lower cost
    
    talk_with_1_occurences = []
    for occ in occurrences:
      if len(occ.talk.occurrences) == 1 and occ.talk not in talk_with_1_occurences:
        talk_with_1_occurences.append(occ.talk)

    talk_with_1_occurences.sort(reverse=True)
    
    for talk in talk_with_1_occurences:

      occ = talk.occurrences[0]

      if talk.which_block_available != 0:
        occ.block = talk.which_block_available
        block_talk_ids[talk.which_block_available].append(talk.talk_id)
      else:

        cost1 = block_cost(talk.talk_id, 1, block_talk_ids, conflict)
        cost2 = block_cost(talk.talk_id, 2, block_talk_ids, conflict)

        if cost1 <= cost2:
          occ.block = 1
          block_talk_ids[1].append(talk.talk_id)
        else:
          occ.block = 2
          block_talk_ids[2].append(talk.talk_id)



# ---------------------------
# Participant assignment
# ---------------------------

def assign_participants_initial(talks: dict, participants: dict):
    """
    Assign participants to occurrences based on already-assigned blocks and preferences.

    Goal:
    - Each participant should get one occurrence in Block 1 and one in Block 2
    - The pair of assignments should be as high-ranked as possible for that participant

    Assumptions:
    - Occurrences exist (talk.occurrences)
    - Each occurrence has occ.block set to 1 or 2
    - Occurrence.add_participant(participant) returns True/False and updates both sides
    - Participant.session_rank(talk_id) returns rank index (0 is best) or None if not ranked
    """

    for participant in participants.values():
      for talk_id in participant.ranked_talk_ids:
        for occ in talks[talk_id].occurrences:
          if not participant.assignment[occ.block]:
            occ.add_participant(participant)
        if participant.assignment[1] and participant.assignment[2]: #if participant's both are assigned
          break
    


# ---------------------------
# Room assignment (capacity-aware)
# ---------------------------

def assign_rooms(talks, rooms):
    """
    Assign rooms based on numbers *within blocks*, while enforcing:
    - Each room can host at most one occurrence per block
    - Rooms can be reused across blocks
    - If a talk has TWO occurrences, BOTH occurrences must use the SAME room
    """
    room_used = {1: set[Any](), 2: set()} # to check which rooms have already been used

    #first secure rooms for talks with 2 occurrences
    double_run_talks = []
    for talk in talks.values():
      if len(talk.occurrences) == 2:
        occ1, occ2 = talk.occurrences
        max_participants = max(len(occ1.participants), len(occ2.participants)) # but if we simply choose the max here, wouldn't we be ignoring the situation where the occ1 has a lot more people and occ2? Because I am thinking that in that case, we should actually move some people from occ1 to occ2 (if this is a valid move and there's no big loss here in terms of conflict and the participant's priorities) 
        double_run_talks.append((talk, max_participants))
    
    double_run_talks.sort(key=lambda x: x[1], reverse=True) #biggest talks first

    available_rooms = sorted(rooms.values(), key=lambda r:r.capacity, reverse=True) #biggest rooms first

    for talk, max_needed in double_run_talks:
      for room in available_rooms:
        effective_max_ppl = room.capacity * (1 - CAPACITY_BUFFER_PERCENT)

        if max_needed <= effective_max_ppl and room not in room_used[1] and room not in room_used[2]:
          for occ in talk.occurrences:
            occ.room = room
          room_used[1].add(room)
          room_used[2].add(room)
          break

    #then handle single-run talks
    single_occurrences = {1: [], 2: []}

    for talk in talks.values():
      if len(talk.occurrences) == 1:
        occ = talk.occurrences[0]
        single_occurrences[occ.block].append(occ)
    
    for block in [1, 2]:
      single_occurrences[block].sort(key=lambda occ:len(occ.participants), reverse = True)

      block_rooms = [r for r in available_rooms if r not in room_used[block]]
      block_rooms.sort(key=lambda r: r.capacity, reverse=True)

      for occ in single_occurrences[block]:
        for room in block_rooms:
          effective_max_ppl = room.capacity * (1 - CAPACITY_BUFFER_PERCENT)
          if len(occ.participants) <= effective_max_ppl:
            occ.room = room
            room_used[block].add(room)
            break



# ---------------------------
# Debug / verification helpers
# ---------------------------

def print_stage1_summary(talks, occurrences):
    print("---- STAGE 1 SUMMARY ----")
    print("Talks:", len(talks))
    print("Occurrences:", len(occurrences))
    print()

    sample = list(talks.values())
    for t in sample:
        occ_info = [(o.occ_id, o.block, o.room.name if o.room else None) for o in t.occurrences]
        print(f"{t.talk_id:>20} | demand={t.demand_score:>6} | occs={occ_info}")



# --- Added by Claude ---

def print_occurrence_summary(talks):
    print("---- OCCURRENCE SUMMARY ----")
    for talk in talks.values():
        for occ in talk.occurrences:
            room_name = occ.room.name if occ.room else "No room"
            capacity = occ.room.capacity if occ.room else "N/A"
            effective_max = f"{occ.room.capacity * (1 - CAPACITY_BUFFER_PERCENT):.0f}" if occ.room else "N/A"
            print(
                f"{occ.occ_id:>25} | block={occ.block} | room={room_name:>20} "
                f"| capacity={capacity} | effective_max={effective_max} | participants={len(occ.participants)}"
            )
    print()


def print_satisfaction_summary(participants):
    print("---- SATISFACTION SUMMARY ----")
    rank_counts = {}
    unranked = 0

    for participant in participants.values():
        for block in [1, 2]:
            occ = participant.assignment[block]
            if occ is None:
                continue
            rank = participant.session_rank(occ.talk.talk_id)
            if rank is None:
                unranked += 1
            else:
                rank_counts[rank] = rank_counts.get(rank, 0) + 1

    total = sum(rank_counts.values()) + unranked
    for rank in sorted(rank_counts):
        label = f"Rank {rank + 1}"
        count = rank_counts[rank]
        low_flag = " *** LOW SATISFACTION ***" if rank >= (8 - LOW_SATISFACTION_THRESHOLD) else ""
        print(f"  {label}: {count} assignments{low_flag}")
    if unranked:
        print(f"  Unranked talk assigned: {unranked}")
    print(f"  Total assignments counted: {total}")
    print()


def print_unassigned(participants):
    print("---- UNASSIGNED PARTICIPANTS ----")
    count = 0
    for participant in participants.values():
        missing = [b for b in [1, 2] if participant.assignment[b] is None]
        if missing:
            print(f"  {participant.name} — missing block(s): {missing}")
            count += 1
    if count == 0:
        print("  All participants fully assigned.")
    else:
        print(f"  Total unassigned: {count}")
    print()

LOW_SATISFACTION_THRESHOLD = 3

def export_assignments(participants, filename="/Users/MatthewLi/Desktop/Senior Year/Winter/Comp_Sci/code/wellness_summitt_schedule/Wellness Project Starter/assignments_output.csv"):
    with open(filename, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(["Name", "Email", "Session 1", "Session 2"])
        for participant in participants.values():
            occ1 = participant.assignment[1]
            occ2 = participant.assignment[2]
            session1 = occ1.talk.title if occ1 else "Unassigned"
            session2 = occ2.talk.title if occ2 else "Unassigned"
            writer.writerow([participant.name, participant.email, session1, session2])
    print(f"Assignments exported to {filename}")


def main():
    #read data
    talks = load_objects('data/Sessions.csv', Talk, 'talk_id')
    rooms = load_objects('data/Rooms.csv', Room, 'name')
    participants = load_objects("data/Participants.csv", Participant, "name")

    # 1) demand
    compute_demand_scores(talks, participants)

    # 2) conflicts
    conflict = build_conflict_matrix(talks, participants)

    # 3) create occurrences
    max_total_occurrences = len(rooms) * 2
    occurrences = create_occurrences(talks, max_total_occurrences)

    # 4) assign blocks
    assign_blocks_conflict_aware(occurrences, conflict)

    # 5) assign initial participants list
    assign_participants_initial(talks, participants)

    # 6) assign rooms
    assign_rooms(talks, rooms)

    # 7) verify
    print_stage1_summary(talks, occurrences)
    print_occurrence_summary(talks)
    print_satisfaction_summary(participants)
    print_unassigned(participants)
    export_assignments(participants)

if __name__ == '__main__':
    main()