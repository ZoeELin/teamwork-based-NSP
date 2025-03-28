import random
import copy
import math

from penalty import calculate_total_penalty


def get_neighbor(assignments, nurses, shift_types):
    """
    Generate a neighbor solution by randomly modifying an assignment.
    """
    new_assignments = copy.deepcopy(assignments)

    # Randomly pick one assignment to modify
    index = random.randint(0, len(new_assignments) - 1)
    assignment = new_assignments[index]

    # Get the nurse object
    nurse = next(n for n in nurses if n["id"] == assignment["nurse"])

    # Randomly pick a new skill (nurse must have this skill)
    new_skill = random.choice(nurse["skills"])

    # Randomly pick a new shift
    new_shift = random.choice(shift_types)

    # Apply the changes
    assignment["skill"] = new_skill
    assignment["shiftType"] = new_shift

    return new_assignments


def simulated_annealing(
    assignments, forbidden_successions, nurses, shift_types, week_filepath
):
    """
    Simulated Annealing (SA) algorithm to optimize the schedule.
    Input: initial assignments, nurses, scenario, shift_types, week_filepath
    Output: optimized schedule
    """

    # ==== Simulated Annealing (SA) ====
    temperature = 100.0
    cooling_rate = 0.99
    min_temp = 0.1
    max_iter = 3000

    current_assignments = assignments
    current_penalty = calculate_total_penalty(
        nurses, current_assignments, week_filepath
    )
    best_assignments = current_assignments
    best_penalty = current_penalty

    for iteration in range(max_iter):
        if temperature < min_temp or best_penalty == 0:
            break

        neighbor_assignment = get_neighbor(current_assignments, nurses, shift_types)
        neighbor_penalty = calculate_total_penalty(
            nurses, forbidden_successions, neighbor_assignment, week_filepath
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
