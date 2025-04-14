import random
import copy
import math

from penalty import calculate_total_penalty
from constants import DAYS_WEEK_ABB


def swap(assignments, nurses, shift_types):
    """
    Generate a neighbor solution by swapping shifts between two nurses.
    """
    new_assignments = copy.deepcopy(assignments)

    # Randomly select two assignments to swap
    if len(new_assignments) < 2:
        return new_assignments

    idx1, idx2 = random.sample(range(len(new_assignments)), 2)

    # Get the nurse objects for both assignments
    nurse1 = next(n for n in nurses if n["id"] == new_assignments[idx1]["nurse"])
    nurse2 = next(n for n in nurses if n["id"] == new_assignments[idx2]["nurse"])

    # Check if both nurses have the required skills for the swap
    skill1 = new_assignments[idx1]["skill"]
    skill2 = new_assignments[idx2]["skill"]

    if skill2 in nurse1["skills"] and skill1 in nurse2["skills"]:
        # Swap the nurses
        new_assignments[idx1]["nurse"], new_assignments[idx2]["nurse"] = (
            new_assignments[idx2]["nurse"],
            new_assignments[idx1]["nurse"],
        )

    return new_assignments


def change(assignments, nurses, shift_types):
    """
    Generate a neighbor solution by changing a nurse's shift/skill pair,
    including the possibility to assign or remove a day-off.
    The selected skill must always belong to the skill-set of the nurse.
    """
    new_assignments = copy.deepcopy(assignments)

    # Decide whether to add a day-off
    # 20% chance to remove assignment (add day-off)
    if random.random() < 0.2 and new_assignments:
        # Remove a random assignment (giving day off)
        index = random.randint(0, len(new_assignments) - 1)
        new_assignments.pop(index)
        return new_assignments

    # Decide whether to add a new assignment
    # 20% chance to add new assignment
    if random.random() < 0.2:

        # Find nurses that could be assigned more shifts
        all_nurse_ids = [n["id"] for n in nurses]
        available_nurses = []
        nurse_id_dayoff_shifts = {}
        for nurse_id in all_nurse_ids:
            scheduled_days = set(
                a["day"] for a in assignments if a["nurse"] == nurse_id
            )
            day_off = [day for day in DAYS_WEEK_ABB if day not in scheduled_days]

            # Count current day-off for this nurse
            if len(day_off) > 0:
                nurse_id_dayoff_shifts[nurse_id] = day_off
                available_nurses.append(nurse_id)

        if len(available_nurses) > 0:
            # Select random available nurse
            nurse_id = random.choice(available_nurses)
            nurse = next(n for n in nurses if n["id"] == nurse_id)

            # Create new assignment
            new_assignment = {
                "nurse": nurse_id,
                "skill": random.choice(nurse["id"]),
                "shiftType": random.choice(shift_types),
                "day": random.choice(nurse_id_dayoff_shifts[nurse_id]),
            }
            new_assignments.append(new_assignment)
            return new_assignments

    # Return existing assignment (if is empty)
    if not new_assignments:
        return new_assignments

    # Modify a randomed assignment
    index = random.randint(0, len(new_assignments) - 1)
    assignment = new_assignments[index]

    # Get the nurse object
    nurse = next(n for n in nurses if n["id"] == assignment["nurse"])

    if random.random() < 0.5:
        # Randomly assign a new skill from the nurse's skill set
        assignment["skill"] = random.choice(nurse["skills"])
    else:
        # Randomly assign a new shift type
        assignment["shiftType"] = random.choice(shift_types)

    return new_assignments


def simulated_annealing(
    assignments, forbidden_successions, nurses, shift_types, weekdata_filepath, scenario
):
    """
    Simulated Annealing (SA) algorithm to optimize the schedule.
    Input: initial assignments, nurses, scenario, shift_types, week_filepath
    Output: optimized schedule
    """

    # ==== Simulated Annealing (SA) ====
    temperature = 100
    cooling_rate = 0.9
    min_temp = 0.1
    max_iter = 300

    current_assignments = assignments
    current_penalty = calculate_total_penalty(
        nurses, forbidden_successions, current_assignments, weekdata_filepath, scenario
    )
    best_assignments = current_assignments
    best_penalty = current_penalty

    for iteration in range(max_iter):
        if temperature < min_temp or best_penalty == 0:
            print(f"Final penalty: {best_penalty}")
            break

        # Get neighborhood to swap or change for each happened 50%
        if random.random() < 0.5:
            neighbor_assignment = swap(current_assignments, nurses, shift_types)
        else:
            neighbor_assignment = change(current_assignments, nurses, shift_types)

        neighbor_penalty = calculate_total_penalty(
            nurses, forbidden_successions, neighbor_assignment, weekdata_filepath
        )

        delta = neighbor_penalty - current_penalty
        if delta < 0 or random.random() < math.exp(-delta / temperature):
            current_assignments = neighbor_assignment
            current_penalty = neighbor_penalty

            if current_penalty < best_penalty:
                best_assignments = current_assignments
                best_penalty = current_penalty

        temperature *= cooling_rate

    print(f"Final penalty: {best_penalty}")

    return best_assignments
