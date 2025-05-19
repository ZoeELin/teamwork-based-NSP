import random
import copy
import math
from collections import Counter


from penalty import calculate_total_penalty
from constants import DAYS_WEEK_ABB, DAYS_WEEK
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


def simulated_annealing_with_ComC(
    run_id,
    output_dir,
    assignments,
    forbidden_successions,
    nurses,
    shift_types,
    weekdata_filepath,
    scenario,
    nurses_lastday_from_lastweek,
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
    Includes MultiSwap, MultiChange, DoubleChange moves and probabilistic control.
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
            nurses_lastday_from_lastweek,
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
                print(f"Accepted: {accepted}, current penalty: {current_penalty:.4f}")

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




def simulated_annealing_with_ComC_MCTS2(
    run_id,
    output_dir,
    assignments,
    forbidden_successions,
    nurses,
    shift_types,
    weekdata_filepath,
    scenario,
    nurses_lastday_from_lastweek,
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
    Includes MultiSwap, MultiChange, DoubleChange moves and probabilistic control.
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
            nurses_lastday_from_lastweek,
            nurseHistory,
            output_dir,
            comc_w,
            print_each_penalty=print_penalty,
            run_id=run_id,
        )

    def multi_swap(assignments, nurses, shift_types, k):
        # print("multi_swaping...")
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
        # print("multi_changing...")
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
        # print("double_changing...")
        return multi_change(assignments, nurses, shift_types, 2, poff, pchange, pstay)
    
    def check_exceed_nurses(assignments, week_data):
        nurse_counter = Counter()

        # Map nurse ID to skills
        nurse_skills = {n["id"]: set(n["skills"]) for n in nurses}

        # Count valid assignments by (day, shift, skill)
        coverage_count = {}
        for assignment in assignments:
            key = (assignment["shiftType"], assignment["skill"], assignment["day"])
            if assignment["skill"] in nurse_skills.get(assignment["nurse"], set()):
                coverage_count[key] = coverage_count.get(key, 0) + 1

        total_exceed = 0
        exceed_periods = 0

        for req in week_data["requirements"]:
            shift = req["shiftType"]
            skill = req["skill"]
            for day in DAYS_WEEK:
                day_key = f"requirementOn{day}"
                if day_key in req:
                    optimal_required = req[day_key]["optimal"]
                    actual_coverage = coverage_count.get((shift, skill, day[0:3]), 0)

                    if actual_coverage > optimal_required:
                        exceed_amount = actual_coverage - optimal_required
                        total_exceed += exceed_amount
                        exceed_periods += 1

                        # 所有實際有排到且技能正確的護士
                        assigned_nurses = [
                            a["nurse"] for a in assignments 
                            if (a["shiftType"] == shift and 
                                a["skill"] == skill and 
                                a["day"] == day[0:3] and
                                a["skill"] in nurse_skills.get(a["nurse"], set()))
                        ]

                        # 計數
                        for nurse in assigned_nurses:
                            nurse_counter[nurse] += 1

        # 計算平均超額人數
        if exceed_periods == 0:
            return []  # 沒有任何超額時段

        average_exceed = round(total_exceed / exceed_periods)
        top_n = min(average_exceed, len(nurse_counter))

        # 取出出現次數最多的護士
        top_nurse_ids = [n for n, _ in nurse_counter.most_common(top_n)]
        final_nurses = [n for n in nurses if n["id"] in top_nurse_ids]

        return final_nurses
    

    def reschedule_with_MCTS(assignments, rescheduled_nurses, week_data):
        # Use MCTS to reschedule exceeded nurses
        from MCTS import NurseSchedulerMCTS
        mcts_scheduler = NurseSchedulerMCTS(scenario, rescheduled_nurses, week_data, nurseHistory, nurses_lastday_from_lastweek)
        
        # Remove assignments for exceeded nurses
        new_assignments = [a for a in assignments if a["nurse"] not in nurses]
        for nurse in rescheduled_nurses:
            nurse_schedule = mcts_scheduler.mcts_search(nurse["id"], max_iterations=10)
            
            # Convert MCTS schedule to assignments format
            for day, shift in nurse_schedule.items():
                if shift:  # Skip empty shifts
                    nurse = next(n for n in rescheduled_nurses if n["id"] == nurse["id"])
                    valid_skills = [s for s in nurse["skills"] if (shift, s) in mcts_scheduler.shift_requirements.get(day, {})]
                    if valid_skills:
                        new_assignments.append({
                            "nurse": nurse["id"],
                            "day": day,
                            "shiftType": shift,
                            "skill": valid_skills[0]
                        })
        
        return new_assignments

    week_data = utils.load_data(weekdata_filepath)
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
            # if temp_idx <= total_temp_levels * 0.1:
            if inner_idx % 2 == 1:
                # exceed_nurses = check_exceed_nurses(current_assignments, week_data)
                # print(f"exceed_nurses: {exceed_nurses}")
                random_choice_nurses = random.sample(nurses, 5)
                neighbor = reschedule_with_MCTS(current_assignments, random_choice_nurses, week_data) 

            else:
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
                print(f"Accepted: {accepted}, current penalty: {current_penalty:.4f}")

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



def simulated_annealing_with_ComC_version2_1(
    run_id,
    output_dir,
    assignments,
    forbidden_successions,
    nurses,
    shift_types,
    weekdata_filepath,
    scenario,
    nurses_lastday_from_lastweek,
    nurseHistory,
    comc_w=0,
    initial_temp=110.0,
    min_temp=2.13,
    cooling_rate=0.95,
    max_iter=2 * 10 ** 4,
    kmaxMS=7,
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
    Includes MultiSwap, MultiChange, DoubleChange moves and probabilistic control.
    """
    temperature = initial_temp
    current_assignments = assignments
    # Initialize cache for moves for current solution
    current_move_cache = set()

    def get_move_key(move_type, nurse1, nurse2=None, start=None, k=None):
        """Generate a unique key for a move"""
        if move_type == "MS":
            return ((move_type, nurse1["id"], nurse2["id"]), start, k)
        else:  
            # MC or DC
            return ((move_type, nurse1["id"]), start, k)
        
    def penalty(assigns, print_penalty=True, run_id=0):
        return calculate_total_penalty(
            nurses,
            forbidden_successions,
            assigns,
            weekdata_filepath,
            scenario,
            nurses_lastday_from_lastweek,
            nurseHistory,
            output_dir,
            comc_w,
            print_each_penalty=print_penalty,
            run_id=run_id,
        )
    
    def make_frozenset(assignments):
        key = frozenset((a["nurse"], a["day"], a["shiftType"], a["skill"]) for a in assignments)
        return key


    def multi_swap(assignments, n1, n2, k, start=0):
        """
        Swap two nurses' k days of schedule starting from `start` index in the sorted list of days.
        Note: nurses must be skill-compatible on the same day to swap.
        """
        new_assignments = utils.fast_copy(assignments)
        days = sorted(list(set(a["day"] for a in new_assignments)))

        selected_days = days[start : start+k-1]
        
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
        print(f"Finish multi swap {n1['id']}, {n2['id']} for {k} days from {DAYS_WEEK_ABB[start]} to {DAYS_WEEK_ABB[start+k-1]}")
        return new_assignments

    def multi_change(assignments, nurse, shift_types, k, start=0, poff=0.33, pchange=0.33, pstay=0.34):
        """
        Change a nurse's schedule for k days of schedule starting from `start` index in the sorted list of days.
        Note: the nurse need to be skill-compatible with the shift type on the new shift.
        """
        new_assignments = utils.fast_copy(assignments)
        days = sorted(list(set(a["day"] for a in new_assignments)))
        if len(days) < k:
            return new_assignments
        selected_days = days[start : start + k-1]
        
        k_day_changed_shift = []
        for day in selected_days:
            # Remove existing assignment for the nurse on that day
            new_assignments = [
                a
                for a in new_assignments
                if not (a["nurse"] == nurse["id"] and a["day"] == day)
            ]

            r = random.random()
            if r < poff:
                shift = "na"
                skill = ""
                movement = "off"
                k_day_changed_shift.append((movement, shift, skill))
            elif r < poff + pchange:
                shift = random.choice(shift_types)
                skill = random.choice(nurse["skills"])
                movement = "change"
                k_day_changed_shift.append((movement, shift, skill))
                new_assignments.append(
                    {
                        "nurse": nurse["id"],
                        "day": day,
                        "shiftType": shift,
                        "skill": skill,
                    }
                )
            else:
                # If it does't day off or change shift, try to stay in the same shift as previous day.
                # If the nurse does not have the previous day, then random choose a shift.
                prev_day = days[start - 1] if start > 0 else None
                prev_shift = None
                for a in assignments:
                    if a["nurse"] == nurse["id"] and a["day"] == prev_day:
                        prev_shift = a["shiftType"]
                        movement = "stay"
                        k_day_changed_shift.append((movement, prev_shift, a["skill"]))
                        break
                shift = prev_shift if prev_shift else random.choice(shift_types)
                skill = random.choice(nurse["skills"])
                movement = "stay"
                k_day_changed_shift.append((movement, shift, skill))
                new_assignments.append(
                    {
                        "nurse": nurse["id"],
                        "day": day,
                        "shiftType": shift,
                        "skill": skill,
                    }
                )

        print(f"Finish multi change {nurse['id']} for {k} days from {DAYS_WEEK_ABB[start]} to {DAYS_WEEK_ABB[start+k-1]} ({k_day_changed_shift})")
        return new_assignments
    

    def double_change(assignments, nurse, shift_types, k, start, poff, pchange, pstay):
        return multi_change(assignments, nurse, shift_types, 2, start, poff, pchange, pstay)
    

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
        accepted_lower_penalty = 0
        for inner_idx in range(ns_per_temp):
            # Try to find a new move that hasn't been tried before
            while True:
                if random.random() < pMS:
                    k = random.randint(1, kmaxMS)
                    start_week_idx = random.randint(0, len(DAYS_WEEK) - k)
                    nurse1, nurse2 = random.sample(nurses, 2)
                    move_key = get_move_key("MS", nurse1, nurse2, DAYS_WEEK_ABB[start_week_idx], k)
                    if move_key not in current_move_cache:
                        neighbor = multi_swap(current_assignments, nurse1, nurse2, k, start_week_idx)
                        current_move_cache.add(move_key)
                        break
                else:
                    k = random.randint(1, kmaxMC)
                    start_week_idx = random.randint(0, len(DAYS_WEEK) - k)
                    nurse = random.choice(nurses)
                    if random.random() < pC / (pC + pDC):
                        move_key = get_move_key("MC", nurse, start=DAYS_WEEK_ABB[start_week_idx], k=k)
                        if move_key not in current_move_cache:
                            neighbor = multi_change(
                                current_assignments,
                                nurse,
                                shift_types,
                                k,
                                start_week_idx, 
                                poff,
                                pchange,
                                pstay,
                            )
                            current_move_cache.add(move_key)
                            break

                    else:
                        k = 2
                        start_week_idx = random.randint(0, len(DAYS_WEEK) - k)
                        move_key = get_move_key("MC", nurse, start=DAYS_WEEK_ABB[start_week_idx], k=k)
                        if move_key not in current_move_cache:
                            neighbor = double_change(
                                current_assignments,
                                nurse,
                                shift_types,
                                k,
                                start_week_idx, 
                                poff,
                                pchange,
                                pstay,
                            )
                            current_move_cache.add(move_key)
                            break

            neighbor_penalty = penalty(neighbor, run_id=run_id, print_penalty=True)
            
            delta = neighbor_penalty - current_penalty

            if random.random() < math.exp(-delta / temperature):
                # It is potential to accept the worse neighbor with the probability of exp(-delta / temperature).
                # Note: if delta is zero, it also accept the neighbor.
                current_assignments = neighbor
                current_penalty = neighbor_penalty
                accepted += 1
                print(f"Accepted: {accepted}, current penalty: {current_penalty:.4f}")
                # Clear cache when accepting a new solution
                current_move_cache.clear()
            
            if delta < 0:
                # Use new solution when the neighbor is better than the current solution.
                current_assignments = neighbor
                current_penalty = neighbor_penalty
                accepted_lower_penalty += 1
                print(f"Lower penalty solution count: {accepted_lower_penalty}, current penalty: {current_penalty:.4f}")

                if current_penalty < best_penalty:
                    best_assignments = current_assignments
                    best_penalty = current_penalty
                    accepted_lower_penalty = 0
                    # Clear cache when finding a better solution
                    current_move_cache.clear()

            # Early cutoff: reduce temperature sooner if enough solutions accepted
            if accepted >= ns_per_temp:
                break

        temperature *= cooling_rate
        if temperature < min_temp or best_penalty == 0:
            break

    return best_assignments




def simulated_annealing_with_ComC_version2_2(
    run_id,
    output_dir,
    assignments,
    forbidden_successions,
    nurses,
    shift_types,
    weekdata_filepath,
    scenario,
    nurses_lastday_from_lastweek,
    nurseHistory,
    comc_w=0,
    initial_temp=110.0,
    min_temp=2.13,
    cooling_rate=0.95,
    max_iter=2 * 10 ** 4,
    kmaxMS=7,
    kmax = 7,
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
    Includes MultiSwap, MultiChange, DoubleChange moves and probabilistic control.
    """
    temperature = initial_temp
    current_assignments = assignments
    # Initialize cache for moves for current solution
    current_move_cache = set()
    all_move_cache = dict()

    def get_move_key(move_type, nurse1, nurse2=None, start=None, k=None):
        """Generate a unique key for a move"""
        if move_type == "MS":
            return ((move_type, nurse1["id"], nurse2["id"]), start, k)
        else:  
            # MC or DC
            return ((move_type, nurse1["id"]), start, k)
        
    def penalty(assigns, print_penalty=True, run_id=0):
        return calculate_total_penalty(
            nurses,
            forbidden_successions,
            assigns,
            weekdata_filepath,
            scenario,
            nurses_lastday_from_lastweek,
            nurseHistory,
            output_dir,
            comc_w,
            print_each_penalty=print_penalty,
            run_id=run_id,
        )
    
    def penalty_original(assigns):
        return calculate_total_penalty(
            nurses,
            forbidden_successions,
            assigns,
            weekdata_filepath,
            scenario,
            nurses_lastday_from_lastweek,
            nurseHistory,
            output_dir,
            comc_w,
            print_each_penalty=False,
            run_id=0,
        )
    
    def make_frozenset(assignments):
        key = frozenset((a["nurse"], a["day"], a["shiftType"], a["skill"]) for a in assignments)
        return key
    
    def get_k(i, total_iters, sharpness=10):
        x = i / (total_iters - 1)
        sigmoid = 1 / (1 + math.exp(sharpness * (x - 0.5)))  # reversed sigmoid
        max_k = round(3 + 4 * sigmoid)  # from 7 to 3
        return random.randint(1, max_k)


    def multi_swap(assignments, n1, n2, k, start=0):
        """
        Swap two nurses' k days of schedule starting from `start` index in the sorted list of days.
        Note: nurses must be skill-compatible on the same day to swap.
        """
        new_assignments = utils.fast_copy(assignments)
        days = sorted(list(set(a["day"] for a in new_assignments)))

        selected_days = days[start : start+k-1]
        
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
        print(f"Finish multi swap {n1['id']}, {n2['id']} for {k} days from {DAYS_WEEK_ABB[start]} to {DAYS_WEEK_ABB[start+k-1]}")
        return new_assignments

    def multi_change(assignments, nurse, shift_types, k, start=0, poff=0.33, pchange=0.33, pstay=0.34):
        """
        Change a nurse's schedule for k days of schedule starting from `start` index in the sorted list of days.
        Note: the nurse need to be skill-compatible with the shift type on the new shift.
        """
        new_assignments = utils.fast_copy(assignments)
        days = sorted(list(set(a["day"] for a in new_assignments)))
        if len(days) < k:
            return new_assignments
        selected_days = days[start : start + k-1]
        
        k_day_changed_shift = []
        for day in selected_days:
            # Remove existing assignment for the nurse on that day
            new_assignments = [
                a
                for a in new_assignments
                if not (a["nurse"] == nurse["id"] and a["day"] == day)
            ]

            r = random.random()
            if r < poff:
                shift = "na"
                skill = ""
                movement = "off"
                k_day_changed_shift.append((movement, shift, skill))
            elif r < poff + pchange:
                shift = random.choice(shift_types)
                skill = random.choice(nurse["skills"])
                movement = "change"
                k_day_changed_shift.append((movement, shift, skill))
                new_assignments.append(
                    {
                        "nurse": nurse["id"],
                        "day": day,
                        "shiftType": shift,
                        "skill": skill,
                    }
                )
            else:
                # If it does't day off or change shift, try to stay in the same shift as previous day.
                # If the nurse does not have the previous day, then random choose a shift.
                prev_day = days[start - 1] if start > 0 else None
                prev_shift = None
                for a in assignments:
                    if a["nurse"] == nurse["id"] and a["day"] == prev_day:
                        prev_shift = a["shiftType"]
                        movement = "stay"
                        k_day_changed_shift.append((movement, prev_shift, a["skill"]))
                        break
                shift = prev_shift if prev_shift else random.choice(shift_types)
                skill = random.choice(nurse["skills"])
                movement = "stay"
                k_day_changed_shift.append((movement, shift, skill))
                new_assignments.append(
                    {
                        "nurse": nurse["id"],
                        "day": day,
                        "shiftType": shift,
                        "skill": skill,
                    }
                )

        print(f"Finish multi change {nurse['id']} for {k} days from {DAYS_WEEK_ABB[start]} to {DAYS_WEEK_ABB[start+k-1]} ({k_day_changed_shift})")
        return new_assignments
    

    def double_change(assignments, nurse, shift_types, k, start, poff, pchange, pstay):
        return multi_change(assignments, nurse, shift_types, 2, start, poff, pchange, pstay)
    

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
        accepted_lower_penalty = 0
        kmax = get_k(temp_idx, total_temp_levels)
        for inner_idx in range(ns_per_temp):
            # Try to find a new move that hasn't been tried before
            current_move_cache = all_move_cache.get(penalty_original(current_assignments), set())
            while True:
                if random.random() < pMS:
                    # k = random.randint(1, kmaxMS)
                    k = random.randint(1, kmax)
                    start_week_idx = random.randint(0, len(DAYS_WEEK) - k)
                    nurse1, nurse2 = random.sample(nurses, 2)
                    move_key = get_move_key("MS", nurse1, nurse2, DAYS_WEEK_ABB[start_week_idx], k)
                    # if move_key not in current_move_cache:
                    if True:
                        neighbor = multi_swap(current_assignments, nurse1, nurse2, k, start_week_idx)
                        current_move_cache.add(move_key)
                        break
                else:
                    # k = random.randint(1, kmaxMC)
                    # k = random.randint(1, kmax)
                    k = 1
                    start_week_idx = random.randint(0, len(DAYS_WEEK) - k)
                    nurse = random.choice(nurses)
                    if random.random() < pC / (pC + pDC):
                        move_key = get_move_key("MC", nurse, start=DAYS_WEEK_ABB[start_week_idx], k=k)
                        if move_key not in current_move_cache:
                            # if random.random() < 0.5:
                            #     break
                            neighbor = multi_change(
                                current_assignments,
                                nurse,
                                shift_types,
                                k,
                                start_week_idx, 
                                poff,
                                pchange,
                                pstay,
                            )
                            current_move_cache.add(move_key)
                            break

                    else:
                        k = 2
                        start_week_idx = random.randint(0, len(DAYS_WEEK) - k)
                        move_key = get_move_key("MC", nurse, start=DAYS_WEEK_ABB[start_week_idx], k=k)
                        if move_key not in current_move_cache:
                            neighbor = double_change(
                                current_assignments,
                                nurse,
                                shift_types,
                                k,
                                start_week_idx, 
                                poff,
                                pchange,
                                pstay,
                            )
                            current_move_cache.add(move_key)
                            break

            neighbor_penalty = penalty(neighbor, run_id=run_id, print_penalty=True)
            
            delta = neighbor_penalty - current_penalty

            if random.random() < math.exp(-delta / temperature):
                # It is potential to accept the worse neighbor with the probability of exp(-delta / temperature).
                # Note: if delta is zero, it also accept the neighbor.
                current_assignments = neighbor
                current_penalty = neighbor_penalty
                accepted += 1
                print(f"Accepted: {accepted}, current penalty: {current_penalty:.4f}")
                # Save the move cache for the current solution
                all_move_cache[make_frozenset(current_assignments)] = current_move_cache
                # Clear cache when accepting a new solution
                current_move_cache.clear()
            
            if delta < 0:
                # Use new solution when the neighbor is better than the current solution.
                current_assignments = neighbor
                current_penalty = neighbor_penalty
                accepted_lower_penalty += 1
                print(f"Lower penalty solution count: {accepted_lower_penalty}, current penalty: {current_penalty:.4f}")

                if current_penalty < best_penalty:
                    best_assignments = current_assignments
                    best_penalty = current_penalty
                    accepted_lower_penalty = 0
                    # Save the move cache for the current solution
                    all_move_cache[make_frozenset(current_assignments)] = current_move_cache
                    # Clear cache when finding a better solution
                    current_move_cache.clear()

            # Early cutoff: reduce temperature sooner if enough solutions accepted
            if accepted >= ns_per_temp:
                break

        temperature *= cooling_rate
        if temperature < min_temp or best_penalty == 0:
            break

    return best_assignments






def simulated_annealing_with_ComC_version3(
    run_id,
    output_dir,
    assignments,
    forbidden_successions,
    nurses,
    shift_types,
    weekdata_filepath,
    scenario,
    nurses_lastday_from_lastweek,
    nurseHistory,
    comc_w=0,
    initial_temp=110.0,
    min_temp=2.13,
    cooling_rate=0.95,
    max_iter=2 * 10 ** 4,
    kmaxMS=7,
    kmax = 7,
    kmaxMC=7,
    pMS=0.45,
    pC=0.5,
    pDC=0.05,
    poff=0.33,
    pchange=0.33,
    pstay=0.34,
):
    """
    Simulated Annealing algorithm as described by Ceschia et al.
    Includes MultiSwap, MultiChange, DoubleChange moves and probabilistic control.
    """
    temperature = initial_temp
    current_assignments = assignments
    # Initialize cache for moves for current solution
    current_move_cache = set()
    all_move_cache = dict()

    def get_move_key(move_type, nurse1, nurse2=None, start=None, k=None):
        """Generate a unique key for a move"""
        if move_type == "MS":
            return ((move_type, nurse1["id"], nurse2["id"]), start, k)
        else:  
            # MC or DC
            return ((move_type, nurse1["id"]), start, k)
        
    def penalty(assigns, print_penalty=True, run_id=0):
        return calculate_total_penalty(
            nurses,
            forbidden_successions,
            assigns,
            weekdata_filepath,
            scenario,
            nurses_lastday_from_lastweek,
            nurseHistory,
            output_dir,
            comc_w,
            print_each_penalty=print_penalty,
            run_id=run_id,
        )
    
    def penalty_original(assigns):
        return calculate_total_penalty(
            nurses,
            forbidden_successions,
            assigns,
            weekdata_filepath,
            scenario,
            nurses_lastday_from_lastweek,
            nurseHistory,
            output_dir,
            comc_w,
            print_each_penalty=False,
            run_id=0,
        )
    
    def make_frozenset(assignments):
        key = frozenset((a["nurse"], a["day"], a["shiftType"], a["skill"]) for a in assignments)
        return key
    
    def get_k(i, total_iters, sharpness=10):
        x = i / (total_iters - 1)
        sigmoid = 1 / (1 + math.exp(sharpness * (x - 0.5)))  # reversed sigmoid
        max_k = round(3 + 4 * sigmoid)  # from 7 to 3
        return random.randint(1, max_k)


    def multi_swap(assignments, n1, n2, k, start=0):
        """
        Swap two nurses' k days of schedule starting from `start` index in the sorted list of days.
        Note: nurses must be skill-compatible on the same day to swap.
        """
        new_assignments = utils.fast_copy(assignments)
        days = sorted(list(set(a["day"] for a in new_assignments)))

        selected_days = days[start : start+k-1]
        
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
        print(f"Finish multi swap {n1['id']}, {n2['id']} for {k} days from {DAYS_WEEK_ABB[start]} to {DAYS_WEEK_ABB[start+k-1]}")
        return new_assignments

    def multi_change(assignments, nurse, shift_types, k, start=0, poff=0.33, pchange=0.33, pstay=0.34):
        """
        Change a nurse's schedule for k days of schedule starting from `start` index in the sorted list of days.
        Note: the nurse need to be skill-compatible with the shift type on the new shift.
        """
        new_assignments = utils.fast_copy(assignments)
        days = sorted(list(set(a["day"] for a in new_assignments)))
        if len(days) < k:
            return new_assignments
        selected_days = days[start : start + k-1]
        
        k_day_changed_shift = []
        for day in selected_days:
            # Remove existing assignment for the nurse on that day
            new_assignments = [
                a
                for a in new_assignments
                if not (a["nurse"] == nurse["id"] and a["day"] == day)
            ]

            r = random.random()
            if r < poff:
                shift = "na"
                skill = ""
                movement = "off"
                k_day_changed_shift.append((movement, shift, skill))
            elif r < poff + pchange:
                shift = random.choice(shift_types)
                skill = random.choice(nurse["skills"])
                movement = "change"
                k_day_changed_shift.append((movement, shift, skill))
                new_assignments.append(
                    {
                        "nurse": nurse["id"],
                        "day": day,
                        "shiftType": shift,
                        "skill": skill,
                    }
                )
            else:
                # If it does't day off or change shift, try to stay in the same shift as previous day.
                # If the nurse does not have the previous day, then random choose a shift.
                prev_day = days[start - 1] if start > 0 else None
                prev_shift = None
                for a in assignments:
                    if a["nurse"] == nurse["id"] and a["day"] == prev_day:
                        prev_shift = a["shiftType"]
                        movement = "stay"
                        k_day_changed_shift.append((movement, prev_shift, a["skill"]))
                        break
                shift = prev_shift if prev_shift else random.choice(shift_types)
                skill = random.choice(nurse["skills"])
                movement = "stay"
                k_day_changed_shift.append((movement, shift, skill))
                new_assignments.append(
                    {
                        "nurse": nurse["id"],
                        "day": day,
                        "shiftType": shift,
                        "skill": skill,
                    }
                )

        print(f"Finish multi change {nurse['id']} for {k} days from {DAYS_WEEK_ABB[start]} to {DAYS_WEEK_ABB[start+k-1]} ({k_day_changed_shift})")
        return new_assignments
    

    def double_change(assignments, nurse, shift_types, k, start, poff, pchange, pstay):
        return multi_change(assignments, nurse, shift_types, 2, start, poff, pchange, pstay)
    

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
        accepted_lower_penalty = 0
        kmax = get_k(temp_idx, total_temp_levels)
        for inner_idx in range(ns_per_temp):
            # Try to find a new move that hasn't been tried before
            current_move_cache = all_move_cache.get(penalty_original(current_assignments), set())
            while True:
                if random.random() < pMS:
                    # k = random.randint(1, kmaxMS)
                    k = random.randint(1, kmax)
                    start_week_idx = random.randint(0, len(DAYS_WEEK) - k)
                    nurse1, nurse2 = random.sample(nurses, 2)
                    move_key = get_move_key("MS", nurse1, nurse2, DAYS_WEEK_ABB[start_week_idx], k)
                    # if move_key not in current_move_cache:
                    if True:
                        neighbor = multi_swap(current_assignments, nurse1, nurse2, k, start_week_idx)
                        current_move_cache.add(move_key)
                        break
                else:
                    # k = random.randint(1, kmaxMC)
                    k = random.randint(1, kmax)
                    start_week_idx = random.randint(0, len(DAYS_WEEK) - k)
                    nurse = random.choice(nurses)
                    if random.random() < pC / (pC + pDC):
                        move_key = get_move_key("MC", nurse, start=DAYS_WEEK_ABB[start_week_idx], k=k)
                        if move_key not in current_move_cache:
                            # if random.random() < 0.5:
                            #     break
                            neighbor = multi_change(
                                current_assignments,
                                nurse,
                                shift_types,
                                k,
                                start_week_idx, 
                                poff,
                                pchange,
                                pstay,
                            )
                            current_move_cache.add(move_key)
                            break

                    else:
                        k = 2
                        start_week_idx = random.randint(0, len(DAYS_WEEK) - k)
                        move_key = get_move_key("MC", nurse, start=DAYS_WEEK_ABB[start_week_idx], k=k)
                        if move_key not in current_move_cache:
                            neighbor = double_change(
                                current_assignments,
                                nurse,
                                shift_types,
                                k,
                                start_week_idx, 
                                poff,
                                pchange,
                                pstay,
                            )
                            current_move_cache.add(move_key)
                            break

            neighbor_penalty = penalty(neighbor, run_id=run_id, print_penalty=True)
            
            delta = neighbor_penalty - current_penalty

            if random.random() < math.exp(-delta / temperature):
                # It is potential to accept the worse neighbor with the probability of exp(-delta / temperature).
                # Note: if delta is zero, it also accept the neighbor.
                current_assignments = neighbor
                current_penalty = neighbor_penalty
                accepted += 1
                print(f"Accepted: {accepted}, current penalty: {current_penalty:.4f}")
                # Save the move cache for the current solution
                all_move_cache[make_frozenset(current_assignments)] = current_move_cache
                # Clear cache when accepting a new solution
                current_move_cache.clear()
            
            if delta < 0:
                # Use new solution when the neighbor is better than the current solution.
                current_assignments = neighbor
                current_penalty = neighbor_penalty
                accepted_lower_penalty += 1
                print(f"Lower penalty solution count: {accepted_lower_penalty}, current penalty: {current_penalty:.4f}")

                if current_penalty < best_penalty:
                    best_assignments = current_assignments
                    best_penalty = current_penalty
                    accepted_lower_penalty = 0
                    # Save the move cache for the current solution
                    all_move_cache[make_frozenset(current_assignments)] = current_move_cache
                    # Clear cache when finding a better solution
                    current_move_cache.clear()

            # Early cutoff: reduce temperature sooner if enough solutions accepted
            if accepted >= ns_per_temp:
                break

        temperature *= cooling_rate
        if temperature < min_temp or best_penalty == 0:
            break

    return best_assignments





def simulated_annealing_with_ComC_baseline(
    run_id,
    output_dir,
    assignments,
    forbidden_successions,
    nurses,
    shift_types,
    weekdata_filepath,
    scenario,
    nurses_lastday_from_lastweek,
    nurseHistory,
    comc_w=0,
    initial_temp=110.0,
    min_temp=2.13,
    cooling_rate=0.95,
    max_iter=2 * 10 ** 4,
    kmaxMS=7,
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
    Includes MultiSwap, MultiChange, DoubleChange moves and probabilistic control.
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
            nurses_lastday_from_lastweek,
            nurseHistory,
            output_dir,
            comc_w,
            print_each_penalty=print_penalty,
            run_id=run_id,
        )


    def multi_swap(assignments, n1, n2, k, start=0):
        """
        Swap two nurses' k days of schedule starting from `start` index in the sorted list of days.
        Note: nurses must be skill-compatible on the same day to swap.
        """
        new_assignments = utils.fast_copy(assignments)
        days = sorted(list(set(a["day"] for a in new_assignments)))

        selected_days = days[start : start+k]
        
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
        print(f"Finish multi swap {n1['id']}, {n2['id']} for {k} days from {DAYS_WEEK_ABB[start]} to {DAYS_WEEK_ABB[start+k-1]}")
        return new_assignments

    def multi_change(assignments, nurse, shift_types, k, start=0, poff=0.33, pchange=0.33, pstay=0.34):
        """
        Change a nurse's schedule for k days of schedule starting from `start` index in the sorted list of days.
        Note: the nurse need to be skill-compatible with the shift type on the new shift.
        """
        new_assignments = utils.fast_copy(assignments)
        days = sorted(list(set(a["day"] for a in new_assignments)))
        if len(days) < k:
            return new_assignments
        selected_days = days[start : start + k]
        
        k_day_changed_shift = []
        for day in selected_days:
            # Remove existing assignment for the nurse on that day
            new_assignments = [
                a
                for a in new_assignments
                if not (a["nurse"] == nurse["id"] and a["day"] == day)
            ]

            r = random.random()
            if r < poff:
                shift = "na"
                skill = ""
                movement = "off"
                k_day_changed_shift.append((movement, shift, skill))
            elif r < poff + pchange:
                shift = random.choice(shift_types)
                skill = random.choice(nurse["skills"])
                movement = "change"
                k_day_changed_shift.append((movement, shift, skill))
                new_assignments.append(
                    {
                        "nurse": nurse["id"],
                        "day": day,
                        "shiftType": shift,
                        "skill": skill,
                    }
                )
            else:
                # If it does't day off or change shift, try to stay in the same shift as previous day.
                # If the nurse does not have the previous day, then random choose a shift.
                prev_day = days[start - 1] if start > 0 else None
                prev_shift = None
                for a in assignments:
                    if a["nurse"] == nurse["id"] and a["day"] == prev_day:
                        prev_shift = a["shiftType"]
                        movement = "stay"
                        k_day_changed_shift.append((movement, prev_shift, a["skill"]))
                        break
                shift = prev_shift if prev_shift else random.choice(shift_types)
                skill = random.choice(nurse["skills"])
                movement = "stay"
                k_day_changed_shift.append((movement, shift, skill))
                new_assignments.append(
                    {
                        "nurse": nurse["id"],
                        "day": day,
                        "shiftType": shift,
                        "skill": skill,
                    }
                )

        print(f"Finish multi change {nurse['id']} for {k} days from {DAYS_WEEK_ABB[start]} to {DAYS_WEEK_ABB[start+k-1]} ({k_day_changed_shift})")
        return new_assignments
    

    def double_change(assignments, nurse, shift_types, k, start, poff, pchange, pstay):
        return multi_change(assignments, nurse, shift_types, 2, start, poff, pchange, pstay)
    

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
        accepted_lower_penalty = 0
        for inner_idx in range(ns_per_temp):
            if random.random() < pMS:
                k = random.randint(1, kmaxMS)
                start_week_idx = random.randint(0, len(DAYS_WEEK) - k)
                nurse1, nurse2 = random.sample(nurses, 2)
                neighbor = multi_swap(current_assignments, nurse1, nurse2, k, start_week_idx)
            else:
                k = random.randint(1, kmaxMC)
                start_week_idx = random.randint(0, len(DAYS_WEEK) - k)
                nurse = random.choice(nurses)
                if random.random() < pC / (pC + pDC):
                    neighbor = multi_change(
                        current_assignments,
                        nurse,
                        shift_types,
                        1,
                        start_week_idx, 
                        poff,
                        pchange,
                        pstay,
                    )

                else:
                    k = 2
                    start_week_idx = random.randint(0, len(DAYS_WEEK) - k)
                    neighbor = double_change(
                        current_assignments,
                        nurse,
                        shift_types,
                        k,
                        start_week_idx, 
                        poff,
                        pchange,
                        pstay,
                    )

            neighbor_penalty = penalty(neighbor, run_id=run_id, print_penalty=True)
            
            delta = neighbor_penalty - current_penalty


            # if delta > 0 and random.random() < math.exp(-delta / temperature):
            if random.random() < math.exp(-delta / temperature):
                # Accept worse solution with certain probability
                current_assignments = neighbor
                current_penalty = neighbor_penalty
                accepted += 1
                print(f"Accepted: {accepted}, current penalty: {current_penalty:.4f}")
            

            if delta < 0:
                # Always accept better solution
                current_assignments = neighbor
                current_penalty = neighbor_penalty
                accepted_lower_penalty += 1
                print(f"Lower penalty solution count: {accepted_lower_penalty}, current penalty: {current_penalty:.4f}")

                if current_penalty < best_penalty:
                    best_assignments = current_assignments
                    best_penalty = current_penalty
                    accepted_lower_penalty = 0
            

            # Early cutoff: reduce temperature sooner if enough solutions accepted
            if accepted >= ns_per_temp:
                break

        temperature *= cooling_rate
        if temperature < min_temp or best_penalty == 0:
            break

    return best_assignments




def simulated_annealing_with_ComC_MCTS(
    run_id,
    output_dir,
    assignments,
    forbidden_successions,
    nurses,
    shift_types,
    weekdata_filepath,
    scenario,
    nurses_lastday_from_lastweek,
    nurseHistory,
    comc_w=0,
    initial_temp=110.0,
    min_temp=2.13,
    cooling_rate=0.95,
    max_iter=2 * 10 ** 2,
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
    Refer to Ceschia et al's paper.
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
            nurses_lastday_from_lastweek,
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
        return multi_change(assignments, nurses, shift_types, 2, poff, pchange, pstay)

    def check_exceed_nurses(assignments, nurses, week_data):
        exceed_nurses = []

        # Map nurse ID to skills
        nurse_skills = {n["id"]: set(n["skills"]) for n in nurses}

        # Count valid assignments by (day, shift, skill)
        coverage_count = {}
        for assignment in assignments:
            key = (assignment["shiftType"], assignment["skill"], assignment["day"])
            # Calculate skill-qualified assignments
            if assignment["skill"] in nurse_skills.get(assignment["nurse"], set()):
                coverage_count[key] = coverage_count.get(key, 0) + 1

        # Check each requirement
        for req in week_data["requirements"]:
            shift = req["shiftType"]
            skill = req["skill"]
            for day in DAYS_WEEK:
                day_key = f"requirementOn{day}"
                if day_key in req:
                    optimal_required = req[day_key]["optimal"]
                    actual_coverage = coverage_count.get((shift, skill, day[0:3]), 0)
                    
                    # If we have more nurses than optimal, find the excess nurses
                    if actual_coverage > optimal_required:
                        # Get all nurses assigned to this shift/skill/day
                        assigned_nurses = [
                            a["nurse"] for a in assignments 
                            if (a["shiftType"] == shift and 
                                a["skill"] == skill and 
                                a["day"] == day[0:3] and
                                a["skill"] in nurse_skills.get(a["nurse"], set()))
                        ]
                        
                        # Add excess nurses to the list
                        excess_count = actual_coverage - optimal_required
                        exceed_nurses.extend(assigned_nurses[:excess_count])

        return list(set(exceed_nurses))  # Remove duplicates
    
    
    def check_h2(assignments, nurses, week_data):
        # Map nurse ID to skills
        nurse_skills = {n["id"]: set(n["skills"]) for n in nurses}

        # Count valid assignments by (day, shift, skill)
        coverage_count = {}
        for assignment in assignments:
            key = (assignment["shiftType"], assignment["skill"], assignment["day"])
            # Calculate skill-qualified assignments(H4: legel assignments)
            if assignment["skill"] in nurse_skills.get(assignment["nurse"], set()):
                coverage_count[key] = coverage_count.get(key, 0) + 1

        # Check each requirement
        for req in week_data["requirements"]:
            shift = req["shiftType"]
            skill = req["skill"]
            for day in DAYS_WEEK:
                day_key = f"requirementOn{day}"
                if day_key in req:
                    optimal_required = req[day_key]["minimum"]
                    actual_coverage = coverage_count.get((shift, skill, day[0:3]), 0)
                    
                    # If we have more nurses than optimal, find the excess nurses
                    if actual_coverage < optimal_required:
                        return False
        return True
    
    def reschedule_with_MCTS(assignments, rescheduled_nurses, week_data):
        # Use MCTS to reschedule exceeded nurses
        from MCTS import NurseSchedulerMCTS
        mcts_scheduler = NurseSchedulerMCTS(scenario, rescheduled_nurses, week_data, nurseHistory, nurses_lastday_from_lastweek)
        
        # Remove assignments for exceeded nurses
        new_assignments = [a for a in assignments if a["nurse"] not in nurses]
        for nurse in rescheduled_nurses:
            nurse_schedule = mcts_scheduler.mcts_search(nurse["id"], max_iterations=10)
            
            # Convert MCTS schedule to assignments format
            for day, shift in nurse_schedule.items():
                if shift:  # Skip empty shifts
                    nurse = next(n for n in rescheduled_nurses if n["id"] == nurse["id"])
                    valid_skills = [s for s in nurse["skills"] if (shift, s) in mcts_scheduler.shift_requirements.get(day, {})]
                    if valid_skills:
                        new_assignments.append({
                            "nurse": nurse["id"],
                            "day": day,
                            "shiftType": shift,
                            "skill": valid_skills[0]
                        })
        
        return new_assignments
        


    week_data = utils.load_data(weekdata_filepath)
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
            
            # exceed_nurses = check_exceed_nurses(current_assignments, nurses, week_data)
            # if exceed_nurses != []:
            #     print(f"\nFound {len(exceed_nurses)} nurses exceeding optimal requirements. Rescheduling with MCTS...")
                
            #     # Remove assignments for exceeded nurses
            #     new_assignments = [a for a in current_assignments if a["nurse"] not in exceed_nurses]
            
            random_choice_nurses = random.sample(nurses, 5)
            print(f"random_choice_nurses: {random_choice_nurses}")
            neighbor = reschedule_with_MCTS(current_assignments, random_choice_nurses, week_data)                


                

            # if random.random() < pMS:
            #     k = random.randint(1, kmaxMS)
            #     neighbor = multi_swap(current_assignments, nurses, shift_types, k)
            # else:
            #     k = random.randint(1, kmaxMC)
            #     if random.random() < pC / (pC + pDC):
            #         neighbor = multi_change(
            #             current_assignments,
            #             nurses,
            #             shift_types,
            #             k,
            #             poff,
            #             pchange,
            #             pstay,
            #         )
            #     else:
            #         neighbor = double_change(
            #             current_assignments,
            #             nurses,
            #             shift_types,
            #             k,
            #             poff,
            #             pchange,
            #             pstay,
            #         )
            neighbor_penalty = penalty(neighbor, run_id=run_id, print_penalty=True)
            
            delta = neighbor_penalty - current_penalty

            if delta < 0 or random.random() < math.exp(-delta / temperature):
                current_assignments = neighbor
                current_penalty = neighbor_penalty
                accepted += 1
                print(f"Accepted: {accepted}, current penalty: {current_penalty:.4f}")

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
