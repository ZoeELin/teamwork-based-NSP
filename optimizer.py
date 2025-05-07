import random
import copy
import math


from penalty import calculate_total_penalty
from constants import DAYS_WEEK_ABB
import utils


def has_conflict(assignments, nurse_id, day):
    """
    Check if the nurse already has an assignment on the given day.
    """
    return any(a["nurse"] == nurse_id and a["day"] == day for a in assignments)


def get_consecutive_days(k, days):
    start_idx = random.randint(0, len(days) - k)
    return days[start_idx : start_idx + k]


def base_swap(assignments, nurses, shift_types):
    """
    Generate a neighbor solution by swapping shifts between two nurses.
    Ensures H1: Only one assignment per day per nurse.
    """
    new_assignments = copy.deepcopy(assignments)

    if len(new_assignments) < 2:
        return new_assignments

    idx1, idx2 = random.sample(range(len(new_assignments)), 2)

    a1 = new_assignments[idx1]
    a2 = new_assignments[idx2]

    nurse1 = next(n for n in nurses if n["id"] == a1["nurse"])
    nurse2 = next(n for n in nurses if n["id"] == a2["nurse"])

    skill1 = a1["skill"]
    skill2 = a2["skill"]

    # Check skill compatibility and H1 constraint
    if (
        skill2 in nurse1["skills"]
        and skill1 in nurse2["skills"]
        and not has_conflict(new_assignments, nurse1["id"], a2["day"])
        and not has_conflict(new_assignments, nurse2["id"], a1["day"])
    ):

        # Perform swap
        new_assignments[idx1]["nurse"], new_assignments[idx2]["nurse"] = (
            a2["nurse"],
            a1["nurse"],
        )
        new_assignments[idx1]["skill"] = skill2
        new_assignments[idx2]["skill"] = skill1

    return new_assignments


def base_change(assignments, nurses, shift_types):
    """
    Generate a neighbor solution by changing a nurse's shift/skill pair,
    ensuring H1: Only one assignment per day per nurse.
    """
    new_assignments = copy.deepcopy(assignments)

    # 33% chance to remove a random assignment
    if random.random() < 0.33 and new_assignments:
        index = random.randint(0, len(new_assignments) - 1)
        new_assignments.pop(index)
        return new_assignments

    # 33% chance to add a new assignment
    if random.random() < 0.33:
        all_nurse_ids = [n["id"] for n in nurses]
        available_nurses = []
        nurse_id_dayoff_shifts = {}

        for nurse_id in all_nurse_ids:
            scheduled_days = set(
                a["day"] for a in assignments if a["nurse"] == nurse_id
            )
            day_off = [day for day in DAYS_WEEK_ABB if day not in scheduled_days]

            if day_off:
                nurse_id_dayoff_shifts[nurse_id] = day_off
                available_nurses.append(nurse_id)

        if available_nurses:
            nurse_id = random.choice(available_nurses)
            nurse = next(n for n in nurses if n["id"] == nurse_id)

            chosen_day = random.choice(nurse_id_dayoff_shifts[nurse_id])
            if has_conflict(new_assignments, nurse_id, chosen_day):
                return new_assignments  # skip if H1 is violated

            new_assignment = {
                "nurse": nurse_id,
                "skill": random.choice(nurse["skills"]),
                "shiftType": random.choice(shift_types),
                "day": chosen_day,
            }
            new_assignments.append(new_assignment)
            return new_assignments

    # Modify an existing assignment
    if not new_assignments:
        return new_assignments

    index = random.randint(0, len(new_assignments) - 1)
    assignment = new_assignments[index]

    nurse = next(n for n in nurses if n["id"] == assignment["nurse"])

    if random.random() < 0.5:
        assignment["skill"] = random.choice(nurse["skills"])
    else:
        new_shift = random.choice(shift_types)
        assignment["shiftType"] = new_shift

    return new_assignments


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
    assignments,
    forbidden_successions,
    nurses,
    shift_types,
    weekdata_filepath,
    scenario,
    lastday_of_lastweek,
    nurseHistory,
):
    """
    Simulated Annealing (SA) algorithm to optimize the schedule.
    Input: initial assignments, nurses, scenario, shift_types, week_filepath
    Output: optimized schedule
    """

    temperature = 110
    cooling_rate = 0.95
    min_temp = 2.13
    max_iter = 2 * 10

    current_assignments = assignments
    current_penalty = calculate_total_penalty(
        nurses,
        forbidden_successions,
        current_assignments,
        weekdata_filepath,
        scenario,
        lastday_of_lastweek,
        nurseHistory,
    )
    best_assignments = current_assignments
    best_penalty = current_penalty

    for iteration in range(max_iter):
        if temperature < min_temp or best_penalty == 0:
            print(f"Final penalty: {best_penalty:.4f}")
            break

        # Get neighborhood to swap or change for each happened 50%
        if random.random() < 0.5:
            neighbor_assignment = swap(current_assignments, nurses, shift_types)
        else:
            neighbor_assignment = change(current_assignments, nurses, shift_types)

        neighbor_penalty = calculate_total_penalty(
            nurses,
            forbidden_successions,
            neighbor_assignment,
            weekdata_filepath,
            scenario,
            lastday_of_lastweek,
            nurseHistory,
        )

        delta = neighbor_penalty - current_penalty
        if delta < 0 or random.random() < math.exp(-delta / temperature):
            current_assignments = neighbor_assignment
            current_penalty = neighbor_penalty

            if current_penalty < best_penalty:
                best_assignments = current_assignments
                best_penalty = current_penalty

        temperature *= cooling_rate

    print(f"Final penalty: {best_penalty: .4f}")

    return best_assignments


def simulated_annealing_author_style(
    assignments,
    forbidden_successions,
    nurses,
    shift_types,
    weekdata_filepath,
    scenario,
    lastday_of_lastweek,
    nurseHistory,
    initial_temp=110.0,
    min_temp=2.13,
    cooling_rate=0.95,
    max_iter=2 * 10**4,
    kmaxMS=20,
    kmaxMC=2,
    pMS=0.45,
    pC=0.5,
    pDC=0.05,
    poff=0.33,
    pchange=0.33,
    pstay=0.34,
):
    """
    Simulated Annealing algorithm as described by Ceschia et al.
    Includes MultiSwap, Change, DoubleChange moves and probabilistic control.
    """
    temperature = initial_temp
    current_assignments = assignments

    def penalty(assigns):
        return calculate_total_penalty(
            nurses,
            forbidden_successions,
            assigns,
            weekdata_filepath,
            scenario,
            lastday_of_lastweek,
            nurseHistory,
        )

    def multi_swap(assignments, nurses, shift_types, k):
        new_assignments = copy.deepcopy(assignments)
        days = sorted(list(set(a["day"] for a in new_assignments)))
        if len(days) < k:
            return new_assignments
        day_idx = random.randint(0, len(days) - k)
        selected_days = days[day_idx : day_idx + k]

        n1, n2 = random.sample(nurses, 2)
        for day in selected_days:
            for a1 in new_assignments:
                if a1["nurse"] == n1["id"] and a1["day"] == day:
                    for a2 in new_assignments:
                        if a2["nurse"] == n2["id"] and a2["day"] == day:
                            if (
                                a1["skill"] in n2["skills"]
                                and a2["skill"] in n1["skills"]
                            ):
                                a1["nurse"], a2["nurse"] = a2["nurse"], a1["nurse"]
        return new_assignments

    def multi_change(assignments, nurses, shift_types, k, poff, pchange, pstay):
        new_assignments = copy.deepcopy(assignments)
        days = sorted(list(set(a["day"] for a in new_assignments)))
        if len(days) < k:
            return new_assignments
        day_idx = random.randint(0, len(days) - k)
        selected_days = days[day_idx : day_idx + k]

        nurse = random.choice(nurses)
        for day in selected_days:
            # Remove existing assignment for the nurse on that day
            new_assignments = [
                a
                for a in new_assignments
                if not (a["nurse"] == nurse["id"] and a["day"] == day)
            ]

            r = random.random()
            if r < poff:
                continue  # day-off
            elif r < poff + pchange:
                shift = random.choice(shift_types)
            else:
                # Try to stay in the same shift as previous day (if any)
                prev_day = days[day_idx - 1] if day_idx > 0 else None
                prev_shift = None
                for a in assignments:
                    if a["nurse"] == nurse["id"] and a["day"] == prev_day:
                        prev_shift = a["shiftType"]
                        break
                shift = prev_shift if prev_shift else random.choice(shift_types)

            skill = random.choice(nurse["skills"])
            new_assignments.append(
                {
                    "nurse": nurse["id"],
                    "day": day,
                    "shiftType": shift,
                    "skill": skill,
                }
            )
        return new_assignments

    def double_change(assignments, nurses, shift_types, k, poff, pchange, pstay):
        return multi_change(assignments, nurses, shift_types, 2, poff, pchange, pstay)

    current_penalty = penalty(current_assignments)
    best_assignments = current_assignments
    best_penalty = current_penalty

    total_temp_levels = int(math.log(min_temp / initial_temp) / math.log(cooling_rate))
    ns_per_temp = max_iter // total_temp_levels

    for temp_idx in range(total_temp_levels):
        print(f"\n--- Temperature Level {temp_idx + 1} ---")
        print(f"Current temperature: {temperature:.4f}")
        accepted = 0
        for inner_idx in range(ns_per_temp):
            if random.random() < pMS:
                k = random.randint(1, kmaxMS)
                neighbor = multi_swap(current_assignments, nurses, shift_types, k)
            else:
                k = random.randint(1, kmaxMC)
                if random.random() < pC / (pC + pDC):
                    neighbor = multi_change(
                        current_assignments,
                        nurses,
                        shift_types,
                        k,
                        poff,
                        pchange,
                        pstay,
                    )
                else:
                    neighbor = double_change(
                        current_assignments,
                        nurses,
                        shift_types,
                        k,
                        poff,
                        pchange,
                        pstay,
                    )

            neighbor_penalty = penalty(neighbor)
            delta = neighbor_penalty - current_penalty

            if delta < 0 or random.random() < math.exp(-delta / temperature):
                current_assignments = neighbor
                current_penalty = neighbor_penalty
                accepted += 1

                if current_penalty < best_penalty:
                    best_assignments = current_assignments
                    best_penalty = current_penalty

            if (inner_idx + 1) % 10000 == 0:  # 每 10000 次印一次
                print(f"  Step {inner_idx+1}: Best penalty = {best_penalty:.2f}")

            # Early cutoff: reduce temperature sooner if enough solutions accepted
            if accepted >= ns_per_temp:
                break

        temperature *= cooling_rate
        if temperature < min_temp or best_penalty == 0:
            break

    print(f"Final penalty: {best_penalty:.4f}")
    return best_assignments


def simulated_annealing_with_ComC(
    run_id,
    output_dir,
    assignments,
    forbidden_successions,
    nurses,
    shift_types,
    weekdata_filepath,
    scenario,
    lastday_of_lastweek,
    nurseHistory,
    comc_w=0,
    initial_temp=110.0,
    min_temp=2.13,
    cooling_rate=0.95,
    max_iter=2 * 10 ** 4,
    kmaxMS=20,
    kmaxMC=2,
    pMS=0.45,
    pC=0.5,
    pDC=0.05,
    poff=0.33,
    pchange=0.33,
    pstay=0.34,
):
    """
    Simulated Annealing algorithm as described by Ceschia et al.
    Includes MultiSwap, Change, DoubleChange moves and probabilistic control.
    """
    temperature = initial_temp
    current_assignments = assignments

    def penalty(assigns, print_penalty=True, run_id=0):
        return calculate_total_penalty(
            nurses,
            forbidden_successions,
            assigns,
            weekdata_filepath,
            scenario,
            lastday_of_lastweek,
            nurseHistory,
            output_dir,
            comc_w,
            print_each_penalty=print_penalty,
            run_id=run_id,
        )

    def multi_swap(assignments, nurses, shift_types, k):
        print("multi_swaping...")
        new_assignments = utils.fast_copy(assignments)
        days = sorted(list(set(a["day"] for a in new_assignments)))
        if len(days) < k:
            return new_assignments
        day_idx = random.randint(0, len(days) - k)
        selected_days = days[day_idx : day_idx + k]

        n1, n2 = random.sample(nurses, 2)
        for day in selected_days:
            for a1 in new_assignments:
                if a1["nurse"] == n1["id"] and a1["day"] == day:
                    for a2 in new_assignments:
                        if a2["nurse"] == n2["id"] and a2["day"] == day:
                            if (
                                a1["skill"] in n2["skills"]
                                and a2["skill"] in n1["skills"]
                            ):
                                a1["nurse"], a2["nurse"] = a2["nurse"], a1["nurse"]
        return new_assignments

    def multi_change(assignments, nurses, shift_types, k, poff, pchange, pstay):
        print("multi_changing...")
        new_assignments = utils.fast_copy(assignments)
        days = sorted(list(set(a["day"] for a in new_assignments)))
        if len(days) < k:
            return new_assignments
        day_idx = random.randint(0, len(days) - k)
        selected_days = days[day_idx : day_idx + k]

        nurse = random.choice(nurses)
        for day in selected_days:
            # Remove existing assignment for the nurse on that day
            new_assignments = [
                a
                for a in new_assignments
                if not (a["nurse"] == nurse["id"] and a["day"] == day)
            ]

            r = random.random()
            if r < poff:
                continue  # day-off
            elif r < poff + pchange:
                shift = random.choice(shift_types)
            else:
                # Try to stay in the same shift as previous day (if any)
                prev_day = days[day_idx - 1] if day_idx > 0 else None
                prev_shift = None
                for a in assignments:
                    if a["nurse"] == nurse["id"] and a["day"] == prev_day:
                        prev_shift = a["shiftType"]
                        break
                shift = prev_shift if prev_shift else random.choice(shift_types)

            skill = random.choice(nurse["skills"])
            new_assignments.append(
                {
                    "nurse": nurse["id"],
                    "day": day,
                    "shiftType": shift,
                    "skill": skill,
                }
            )
        return new_assignments

    def double_change(assignments, nurses, shift_types, k, poff, pchange, pstay):
        print("double_changing...")
        return multi_change(assignments, nurses, shift_types, 2, poff, pchange, pstay)

    print("\nStart simulated annealing...🧊")
    current_penalty = penalty(current_assignments, run_id)
    best_assignments = current_assignments
    best_penalty = current_penalty

    total_temp_levels = int(math.log(min_temp / initial_temp) / math.log(cooling_rate))
    ns_per_temp = max_iter // total_temp_levels

    for temp_idx in range(total_temp_levels):
        print(f"\n--- Temperature Level ({temp_idx + 1}/{total_temp_levels}) ---")
        print(f"> Current temperature: {temperature:.4f}, current penalties: {current_penalty:.4f}")
        accepted = 0
        for inner_idx in range(ns_per_temp):
            if random.random() < pMS:
                k = random.randint(1, kmaxMS)
                neighbor = multi_swap(current_assignments, nurses, shift_types, k)
            else:
                k = random.randint(1, kmaxMC)
                if random.random() < pC / (pC + pDC):
                    neighbor = multi_change(
                        current_assignments,
                        nurses,
                        shift_types,
                        k,
                        poff,
                        pchange,
                        pstay,
                    )
                else:
                    neighbor = double_change(
                        current_assignments,
                        nurses,
                        shift_types,
                        k,
                        poff,
                        pchange,
                        pstay,
                    )
            neighbor_penalty = penalty(neighbor, run_id=run_id, print_penalty=True)
            
            delta = neighbor_penalty - current_penalty

            if delta < 0 or random.random() < math.exp(-delta / temperature):
                current_assignments = neighbor
                current_penalty = neighbor_penalty
                accepted += 1

                if current_penalty < best_penalty:
                    best_assignments = current_assignments
                    best_penalty = current_penalty

            # Early cutoff: reduce temperature sooner if enough solutions accepted
            if accepted >= ns_per_temp:
                break

        temperature *= cooling_rate
        if temperature < min_temp or best_penalty == 0:
            break

    return best_assignments
