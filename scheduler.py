import json
import random

import optimizer
import utils
import penalty
import history
from collections import defaultdict

from constants import DAYS_WEEK, DAYS_WEEK_ABB


def basic_scheduler(sce_filepath, weekdata_filepath):
    """
    Generate a basic random schedule for a given scenario.
    Input: filepath to the scenario JSON file
    """
    # Load scenario
    with open(sce_filepath, "r") as f:
        scenario = json.load(f)

    shift_types = [s["id"] for s in scenario["shiftTypes"]]
    nurses = scenario["nurses"]
    forbidden_successions = scenario["forbiddenShiftTypeSuccessions"]
    assignments = []

    # Initialize an empty map to track assigned shifts per day
    shift_coverage = {
        day: {shift: False for shift in shift_types} for day in DAYS_WEEK_ABB
    }

    # Randomly assign 5-7 shifts to each nurse, skip duplicates
    for nurse in scenario["nurses"]:
        nurse_id = nurse["id"]
        assigned_days = random.sample(
            DAYS_WEEK_ABB, k=random.randint(5, 7)
        )  # Randomly assign 5-7 shifts to each nurse

        prev_shift = None
        for day in sorted(
            assigned_days, key=lambda d: DAYS_WEEK_ABB.index(d)
        ):  # Sort by day index
            valid_shifts = [
                s
                for s in shift_types
                if not any(
                    rule["precedingShiftType"] == prev_shift
                    and s in rule["succeedingShiftTypes"]
                    for rule in scenario["forbiddenShiftTypeSuccessions"]
                )
            ]
            if not valid_shifts:
                continue  # skip iteration if no valid shift

            shift = random.choice(valid_shifts)
            prev_shift = shift
            assignments.append(
                {
                    "nurse": nurse_id,
                    "day": day,
                    "shiftType": shift,
                    "skill": random.choice(nurse["skills"]),
                }
            )

    assignments = optimizer.simulated_annealing(
        assignments, forbidden_successions, nurses, shift_types, weekdata_filepath
    )

    one_week_solution = utils.package_solution_2JSON(assignments, scenario["id"])

    return one_week_solution


def optimal_scheduler(sce_filepath, weekdata_filepath, his_filepath):
    """
    Generate a random schedule for a given scenario,
    with consideration of hard constraints(H1, H3 from INRC2 definitions).
    Input: filepath to the scenario JSON file
    Output: a JSON object representing
    """
    # Load scenario
    with open(sce_filepath, "r") as f:
        scenario = json.load(f)

    shift_types = [s["id"] for s in scenario["shiftTypes"]]
    nurses = scenario["nurses"]
    forbidden_successions = scenario["forbiddenShiftTypeSuccessions"]

    nurseHistory = dict()
    if his_filepath:
        with open(his_filepath, "r") as f:
            history_data = json.load(f)
        nurseHistory = {
            data["nurse"]: data["lastAssignedShiftType"]
            for data in history_data["nurseHistory"]
        }  # e.g., {'Patrick': 'Night', 'Andrea': 'None', ...}

    assignments = []

    nurse_day_shift = defaultdict(lambda: {})  # {nurse_id : {day: shift}}

    # Initialize an empty map to track assigned shifts per day
    shift_coverage = {
        day: {shift: False for shift in shift_types} for day in DAYS_WEEK_ABB
    }

    # Ensure each shift per day has at least one nurse
    for day in DAYS_WEEK_ABB:
        for shift in shift_types:
            if shift_coverage[day][shift]:
                break

            # Find eligible nurses who can take this shift
            random.shuffle(nurses)  # Shuffle to randomize selection
            for nurse in nurses:

                nurse_id = nurse["id"]

                # Check H1: Only one assignment per day
                if day in nurse_day_shift[nurse_id]:
                    continue  # Break h1, skip this nurse

                skill = random.choice(nurse["skills"])

                # Check H3: forbidden succession rules
                prev_day_idx = DAYS_WEEK_ABB.index(day) - 1
                prev_shift = None
                if prev_day_idx == -1 and his_filepath:  # Sunday (last day of the week)
                    prev_shift = nurseHistory.get(nurse_id)

                if prev_day_idx >= 0:
                    prev_day = DAYS_WEEK_ABB[prev_day_idx]
                    prev_shift = nurse_day_shift[nurse_id].get(prev_day)

                if prev_shift:
                    forbidden = any(
                        rule["precedingShiftType"] == prev_shift
                        and shift in rule["succeedingShiftTypes"]
                        for rule in forbidden_successions
                    )
                    if forbidden:
                        continue  # Break the succession day, skip this nurse

                nurse_day_shift[nurse_id] = {day: shift}
                assignments.append(
                    {
                        "nurse": nurse_id,
                        "day": day,
                        "shiftType": shift,
                        "skill": skill,
                    }
                )
            shift_coverage[day][shift] = True

    # assignments = optimizer.simulated_annealing(
    #     assignments, forbidden_successions, nurses, shift_types, weekdata_filepath
    # )

    # Visualize the schedule in an easy-to-read table format in terminal
    utils.display_schedule(assignments)

    penalty.calculate_total_penalty(
        nurses, forbidden_successions, assignments, weekdata_filepath
    )

    history.create_next_history_data(assignments, his_filepath)

    return assignments


def supreme_scheduler(sce_filepath, weekdata_filepath, his_filepath=None):
    """
    Generate a schedule that satisfies H1-H4.
    Input: scenario file path, week data file path
    Output: a list of assignments(list of dictionary), e.g., {nurse, day, shiftType, skill}
    """
    with open(sce_filepath, "r") as f:
        scenario = json.load(f)
    with open(weekdata_filepath, "r") as f:
        week_data = json.load(f)

    shift_types = [s["id"] for s in scenario["shiftTypes"]]
    nurses = scenario["nurses"]
    forbidden_successions = scenario["forbiddenShiftTypeSuccessions"]

    nurseHistory = dict()
    if his_filepath:
        with open(his_filepath, "r") as f:
            history_data = json.load(f)
        nurseHistory = {
            data["nurse"]: data["lastAssignedShiftType"]
            for data in history_data["nurseHistory"]
        }  # e.g., {'Patrick': 'Night', 'Andrea': 'None', ...}

    # Requirements for the number of persons needed per day per skill per shift (H2)
    shift_requirements = {
        day: {} for day in DAYS_WEEK_ABB
    }  # e.g., {'Mon': {('Early', 'Nurse'): 2, ('Late', 'Nurse'): 1}}
    for req in week_data["requirements"]:
        shift = req["shiftType"]
        skill = req["skill"]

        for day in DAYS_WEEK:
            day_key = f"requirementOn{day}"
            if day_key in req:
                minimum_required = req[day_key]["minimum"]
                if minimum_required > 0:
                    shift_requirements[day[0:3]][(shift, skill)] = minimum_required

    assignments = []
    nurse_day_shift = defaultdict(lambda: {})  # {nurse_id : {day: shift}}

    for day in DAYS_WEEK_ABB:
        # All that day (shiftType, skill) needed
        required_slots = shift_requirements.get(
            day, {}
        )  # e.g., {('Early', 'Nurse'): 2, ('Late', 'Nurse'): 1}

        # Each shift-skill pair needs a certain number of nurses
        for (shift, skill), needed in required_slots.items():
            count = 0
            random.shuffle(nurses)  # Randomize the order of nurses

            for nurse in nurses:
                # Check H2: Under-staﬃng
                if count >= needed:
                    break
                nurse_id = nurse["id"]

                # Check H1: Only one assignment per day
                if day in nurse_day_shift[nurse_id]:
                    continue  # Break h1, skip this nurse

                # Check H4: Nurses missing required skill
                if skill not in nurse["skills"]:
                    continue  # Break h4, ship this nurse

                # Check H3: Chech forbidden succession
                prev_day_idx = DAYS_WEEK_ABB.index(day) - 1
                prev_shift = None
                if prev_day_idx == -1 and his_filepath:  # Sunday (last day of the week)
                    prev_shift = nurseHistory.get(nurse_id)

                if prev_day_idx >= 0:
                    prev_day = DAYS_WEEK_ABB[prev_day_idx]
                    prev_shift = nurse_day_shift[nurse_id].get(prev_day)

                if prev_shift:
                    forbidden = any(
                        rule["precedingShiftType"] == prev_shift
                        and shift in rule["succeedingShiftTypes"]
                        for rule in forbidden_successions
                    )
                    if forbidden:
                        continue  # Break the succession day, skip this nurse

                # No previous day, no violation
                assignments.append(
                    {
                        "nurse": nurse_id,
                        "day": day,
                        "shiftType": shift,
                        "skill": skill,
                    }
                )
                nurse_day_shift[nurse_id][day] = shift
                count += 1

    utils.display_schedule(assignments)

    penalty.calculate_total_penalty(
        nurses, forbidden_successions, assignments, weekdata_filepath
    )

    history.create_next_history_data(assignments, his_filepath)

    return assignments


def base_scheduler(sce_filepath, weekdata_filepath, his_filepath=None):
    """
    Initial solution that randomly assigns nurses to meet shift requirements (H2 only).
    Input: scenario file path, week data file path
    Output: a list of assignments (list of dictionaries), e.g., {nurse, day, shiftType, skill}
    """
    with open(sce_filepath, "r") as f:
        scenario = json.load(f)
    with open(weekdata_filepath, "r") as f:
        week_data = json.load(f)

    nurses = scenario["nurses"]
    shift_types = [s["id"] for s in scenario["shiftTypes"]]
    forbidden_successions = scenario["forbiddenShiftTypeSuccessions"]
    assignments = []

    # Build shift requirements from week data
    shift_requirements = {day: {} for day in DAYS_WEEK_ABB}
    for req in week_data["requirements"]:
        shift = req["shiftType"]
        skill = req["skill"]

        for day in DAYS_WEEK:
            day_key = f"requirementOn{day}"
            if day_key in req:
                minimum_required = req[day_key]["minimum"]
                if minimum_required > 0:
                    shift_requirements[day[:3]][(shift, skill)] = minimum_required

    # Randomly assign nurses to each required shift (satisfying only H2)
    for day in DAYS_WEEK_ABB:
        required_slots = shift_requirements.get(day, {})
        for (shift, skill), needed in required_slots.items():
            eligible_nurses = [n for n in nurses if skill in n["skills"]]
            if len(eligible_nurses) < needed:
                print(
                    f"Warning: not enough nurses with skill {skill} for {shift} on {day}"
                )

            for _ in range(needed):
                if not eligible_nurses:
                    break
                nurse = random.choice(eligible_nurses)
                assignments.append(
                    {
                        "nurse": nurse["id"],
                        "day": day,
                        "shiftType": shift,
                        "skill": skill,
                    }
                )

    assignments = optimizer.simulated_annealing(
        assignments, forbidden_successions, nurses, shift_types, weekdata_filepath
    )

    penalty.calculate_total_penalty(
        nurses, forbidden_successions, assignments, weekdata_filepath
    )

    history.create_next_history_data(assignments, his_filepath)

    # Visualize the schedule in an easy-to-read table format in terminal
    # utils.display_schedule(assignments)

    return assignments
