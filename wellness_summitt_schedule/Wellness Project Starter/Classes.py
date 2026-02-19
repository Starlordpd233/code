class Talk:
    def __init__(self, datalist, header_index):
        self.talk_id = datalist[header_index["Short Title"]].strip()
        self.title = datalist[header_index["Title"]].strip()
        self.presenter = datalist[header_index["Speaker"]].strip()
        self.max_runs = int(datalist[header_index["Available"]])
        self.which_block_available = int(datalist[header_index["Restrictions"]]) #this is the block in which this talk can be run (ie, 0, 1, or 2 where 0 means it can be run in both blocks)

        self.demand_score = 0
        self.occurrences = []

    def __lt__(self, other):
        return self.demand_score < other.demand_score

class Room:
    def __init__(self, datalist, header_index):
        self.name = datalist[header_index["Room"]].strip()
        self.capacity = int(datalist[header_index["Capacity"]])

    def __lt__(self, other):
        return self.capacity < other.capacity
    
class Participant:
    def __init__(self, datalist, header_index):
        self.name = datalist[header_index["Name"]].strip()
        self.school = datalist[header_index['School Name']].strip()
        self.email = datalist[header_index["Email"]].strip() if "Email" in header_index else ""

        raw = datalist[header_index["Workshop Ranking"]].strip()

        if raw == "":
            self.ranked_talk_ids = []
        else:
            self.ranked_talk_ids = [
                s.strip() for s in raw.split(";") if s.strip() != ""
            ]

        # One assignment per block
        self.assignment = {1: None, 2: None}

    def session_rank(self, talk_id):
        """
        Return rank index (0 is best).
        Return None if not ranked.
        """
        if talk_id in self.ranked_talk_ids:
            return self.ranked_talk_ids.index(talk_id)
        return None
    
class Occurrence:
    def __init__(self, occ_id, talk):
        self.occ_id = occ_id
        self.talk = talk          # Talk object

        self.block = None         # 1 or 2
        self.room = None          # Room object

        self.participants = []    # list of Participant objects

    def capacity(self):
        return self.room.capacity

    def is_full(self):
        return len(self.participants) >= self.capacity()

    def add_participant(self, participant: Participant):
        """
        Add participant to this occurrence AND update participant.assignment.
        Return True if successful, False if not allowed.
        """

        if participant not in self.participants:
            self.participants.append(participant)
            participant.assignment[self.block] = self

            return True

        return False


    def remove_participant(self, participant):
        """
        Remove participant from this occurrence AND clear participant.assignment for this block.
        """

        if participant in self.participants:
            self.participants.remove(participant)

            participant.assignment[self.block] = None
        
        #later we can add return True/False depending on if we need that feature later
        