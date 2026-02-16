"""
HW: Stage 1 — Demand + Conflict

You will write two functions used by our conference scheduler:

1) compute_demand_scores(talks, participants, top_k=4)
2) build_conflict_matrix(talks, participants, top_k=4)

These functions MUST work later with our real classes loaded from CSV.
So: do NOT rely on anything except these attributes:

Talk:
- talk_id (string)
- demand_score (number you will compute)

Participant:
- ranked_talk_ids (list of talk_id strings, best -> worst)

This homework file includes a tiny data generator and tests.
When you're done, run this file to see if your tests pass.
"""

# --------------------------
# Tiny stand-in classes
# (These mirror the attributes of our real classes.)
# Later, your two functions will be used with the real Talk/Participant.
# --------------------------

class Talk:
    def __init__(self, talk_id):
        self.talk_id = talk_id
        self.demand_score = 0

class Participant:
    def __init__(self, name, ranked_talk_ids):
        self.name = name
        self.ranked_talk_ids = ranked_talk_ids


# --------------------------
# TODO 1: Demand
# --------------------------

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

    pass


# --------------------------
# TODO 2: Conflict Matrix
# --------------------------

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

    #TODO: populate conflict dictionary

    return conflict


# --------------------------
# Mini test data (deterministic)
# --------------------------

def build_small_test_data():
    """
    Talks: A, B, C, D
    Participants:
      P1: A > B > C > D
      P2: A > C > B > D
      P3: B > A > D > C
    """
    talks = {tid: Talk(tid) for tid in ["A", "B", "C", "D"]}

    participants = {
        "P1": Participant("P1", ["A", "B", "C", "D"]),
        "P2": Participant("P2", ["A", "C", "B", "D"]),
        "P3": Participant("P3", ["B", "A", "D", "C"]),
    }
    return talks, participants


def run_tests():
    talks, participants = build_small_test_data()

    # ---- Demand test ----
    # Using top_k=3:
    # P1 gives A=3, B=2, C=1
    # P2 gives A=3, C=2, B=1
    # P3 gives B=3, A=2, D=1
    # Totals: A=8, B=6, C=3, D=1
    compute_demand_scores(talks, participants, top_k=3)
    expected = {"A": 8, "B": 6, "C": 3, "D": 1}
    for tid in expected:
        assert talks[tid].demand_score == expected[tid], f"demand {tid} expected {expected[tid]}, got {talks[tid].demand_score}"

    # ---- Conflict test ----
    # Using top_k=2 (top two choices per participant):
    # P1: {A,B}
    # P2: {A,C}
    # P3: {B,A}
    # conflict(A,B)=2 (P1 and P3)
    # conflict(A,C)=1 (P2)
    # conflict(B,C)=0
    conflict = build_conflict_matrix(talks, participants, top_k=2)

    assert conflict[("A", "B")] == 2, f'conflict(A,B) expected 2, got {conflict[("A","B")]}'
    assert conflict[("B", "A")] == 2, f'conflict(B,A) expected 2, got {conflict[("B","A")]}'
    assert conflict[("A", "C")] == 1, f'conflict(A,C) expected 1, got {conflict[("A","C")]}'
    assert conflict[("C", "A")] == 1, f'conflict(C,A) expected 1, got {conflict[("C","A")]}'
    assert conflict[("B", "C")] == 0, f'conflict(B,C) expected 0, got {conflict[("B","C")]}'

    print("All tests passed ✅")

if __name__ == "__main__":
    run_tests()