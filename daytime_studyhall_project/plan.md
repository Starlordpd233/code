Approach B — Enforce minimum size for non-empty sections (deactivate-first)
Implement a post-pass at the end of schedule() that fixes section sizes after the main assignment rounds.

Step 1: Identify “illegal active sections”
Define `active_underfilled = [sec for sec in _sh_sections if 0 < size(sec) < min]`.
Step 2: Deactivate-first pass (preferred)
For each sec in active_underfilled, attempt to move all its students elsewhere so sec becomes 0.

For each student currently in sec, find a destination block in the student’s availability that:
is not already in student.scheduled_sh
has capacity
first pass: respects spacing (get_distance > 1)
second pass: allows spacing violation (and add a note to that student)
preference (2/4 vs 1) is allowed to be overridden here (soft)
If you succeed for every student in sec, then sec is now 0 and the min rule is satisfied.
Step 3: If deactivation fails, try filling to min
If sec still has students (because some cannot move out), attempt to pull students in from other sections.

Donor selection ideas:
prefer donors that will remain comfortably non-empty (don’t create new 1..(min−1) donors)
prefer moving students for whom sec is in availability
Again stage constraints:
first preserve spacing
then relax spacing with notes
Step 4: Final report
If some sections remain non-empty and < min even after Step 3:

mark them as unavoidable_underfilled
include in the returned status/report:
which sections
current size
why common candidates couldn’t move (capacity, no availability, spacing only, etc.)
