import csv
from typing import Any
from Classes import *
import heapq 

MIN_PEOPLE_PER_SESSION = 10
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


    eligible_talks = [talk for talk in talks.values() if talk.max_runs == 2 and talk.demand_score >= 130]
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
            break #only one occurrence per talk
        if participant.assignment[1] and participant.assignment[2]: #if participant's both are assigned
          break


def calculate_move_cost(participant, curr_occ, new_occ):
  cost = 0

  if len(new_occ.participants) >= new_occ.room.effective_capacity:
    return float('inf')
  if new_occ == curr_occ:
    return float('inf')
  
  other_block = 1 if new_occ.block == 2 else 2
  other_assignment = participant.assignment[other_block]
  if other_assignment and other_assignment.talk.talk_id == new_occ.talk.talk_id:
    return float('inf')

  current_rank = participant.session_rank(curr_occ.talk.talk_id)
  new_rank = participant.session_rank(new_occ.talk.talk_id)

  if new_rank is None:
    cost += float(1000)
  
  if len(new_occ.participants) <= MIN_PEOPLE_PER_SESSION:
    cost -= float(100)
  
  #is there any other factors we should consider?
  if new_rank is not None and current_rank is not None:
    cost += new_rank - current_rank

  return cost


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
    for talk in talks.values():
      for occ in talk.occurrences:
        occ.room = None
    
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
            block_rooms = [r for r in available_rooms if r not in room_used[block]]
            break

def optimize_assignments(talks):
  moves_heap = []
  counter = 0

  occurrences = [occ for talk in talks.values() for occ in talk.occurrences]

  overfilled_occ = [occ for occ in occurrences if occ.is_full()]

  for occ in overfilled_occ:
    for participant in occ.participants:
      same_block_occs = [o for o in occurrences if o.block == occ.block and o != occ]
      
      for new_occ in same_block_occs:
        cost = calculate_move_cost(participant, occ, new_occ)
        if cost != float('inf'):
          heapq.heappush(moves_heap, (cost, counter, participant, occ, new_occ))
          counter += 1
  
  move = 0

  while moves_heap:
    cost, _, participant, curr_occ, new_occ = heapq.heappop(moves_heap)

    if len(curr_occ.participants) <= curr_occ.room.effective_capacity:
      continue
    if len(new_occ.participants) >= new_occ.room.effective_capacity:
      continue
    if participant.assignment[curr_occ.block] != curr_occ:
      continue

    curr_occ.remove_participant(participant)
    new_occ.add_participant(participant)
    move += 1
  

  #now for underfilled occs
  underfilled_occs = [occ for occ in occurrences if len(occ.participants) <= MIN_PEOPLE_PER_SESSION]

  for occ in underfilled_occs:
    while len(occ.participants) < MIN_PEOPLE_PER_SESSION:
      
      donor_occs = [o for o in occurrences if o.block == occ.block and o != occ and len(o.participants) > MIN_PEOPLE_PER_SESSION + 2]

      if not donor_occs:
        break
      
      best_candidate = None
      best_rank = float('inf')
      best_donor = None

      for donor_occ in donor_occs:
        for participant in donor_occ.participants:
          rank = participant.session_rank(occ.talk.talk_id)

          other_block = 1 if occ.block == 2 else 2
          other_assignment = participant.assignment[other_block]
          if other_assignment and other_assignment.talk.talk_id == occ.talk.talk_id:
            continue

          if rank is not None and rank < best_rank:
            best_rank = rank
            best_candidate = participant
            best_donor = donor_occ
      if best_candidate is None:
        break

      best_donor.remove_participant(best_candidate)
      occ.add_participant(best_candidate)
      move += 1
  
  return move


# ---------------------------
# Debug / verification helpers
# ---------------------------

def print_stage1_summary_original(talks, occurrences):
    print("---- STAGE 1 SUMMARY ----")
    print("Talks:", len(talks))
    print("Occurrences:", len(occurrences))
    print()

    sample = list(talks.values())
    for t in sample:
        occ_info = [(o.occ_id, o.block, o.room.name if o.room else None) for o in t.occurrences]
        print(f"{t.talk_id:>20} | demand={t.demand_score:>6} | occs={occ_info}")

def print_stage1_summary(talks, occurrences):
    print("---- STAGE 1 SUMMARY ----")
    print("Talks:", len(talks))
    print("Occurrences:", len(occurrences))
    print()

    sample = list(talks.values())
    for t in sample:
        occ_info = []
        for o in t.occurrences:
            room_name = o.room.name if o.room else "No room"
            num_assigned = len(o.participants)
            capacity = o.capacity() if o.room else "N/A"
            occ_info.append((o.occ_id, o.block, room_name, num_assigned, capacity))
        print(f"{t.talk_id:>20} | demand={t.demand_score:>6} | occs={occ_info}")

def export_session_summary(talks, filename="/Users/MatthewLi/Desktop/Senior Year/Winter/Comp_Sci/code/wellness_summitt_schedule/Wellness Project Starter/session_summary.csv"):
  with open(filename, 'w', newline='', encoding='utf-8') as f:
    writer = csv.writer(f)

    writer.writerow([
      "Title", 
      "Block", 
      "Room",
      "Participant Count"
    ])
    for talk in talks.values():
      for occ in talk.occurrences:
        title = talk.title
        room_name = occ.room.name if occ.room else "No room"
        block = occ.block
        participant_count = len(occ.participants)
        writer.writerow([
          title, 
          block, 
          room_name,
          participant_count
        ])


def export_assignments(participants, filename="/Users/MatthewLi/Desktop/Senior Year/Winter/Comp_Sci/code/wellness_summitt_schedule/Wellness Project Starter/assignments_output.csv"):
    with open(filename, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(["Name", "Email Address", "Block 1 Assignment", "Block 2 Assignment"])
        for participant in participants.values():
            occ1 = participant.assignment[1]
            occ2 = participant.assignment[2]
            session1 = occ1.talk.title if occ1 else "Unassigned"
            session2 = occ2.talk.title if occ2 else "Unassigned"
            writer.writerow([participant.name, participant.email, session1, session2])
    print(f"Assignments exported to {filename}")





def main():
    #read data
    talks = load_objects("/Users/MatthewLi/Desktop/Senior Year/Winter/Comp_Sci/code/wellness_summitt_schedule/Wellness Project Starter/data/Sessions.csv", Talk, 'talk_id')
    rooms = load_objects("/Users/MatthewLi/Desktop/Senior Year/Winter/Comp_Sci/code/wellness_summitt_schedule/Wellness Project Starter/data/Rooms.csv", Room, 'name')
    participants = load_objects("/Users/MatthewLi/Desktop/Senior Year/Winter/Comp_Sci/code/wellness_summitt_schedule/Wellness Project Starter/data/Participants.csv", Participant, "name")

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
    MAX_ITERATIONS = 10

    for i in range(MAX_ITERATIONS):
      assign_rooms(talks, rooms)
      moved = optimize_assignments(talks)
      print(f"  Optimization pass {i+1}: {moved} moves")
      if moved == 0:
        break


    # 7) verify
    print_stage1_summary(talks, occurrences)
    export_assignments(participants)
    export_session_summary(talks)

if __name__ == '__main__':
    main()