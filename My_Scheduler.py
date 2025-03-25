import json
import random
import math
import copy
import os
import re
from collections import defaultdict
import pandas as pd

# Days of the week
DAYS_WEEK_ABB = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
DAYS_WEEK = [
    "Monday",
    "Tuesday",
    "Wednesday",
    "Thursday",
    "Friday",
    "Saturday",
    "Sunday",
]


def generate_carryover(schedule):
    """
    根據排班表產生 carryover 狀態：
    - 最後班別
    - 連續工作天數
    - 連續相同班別的天數
    """
    carryover = {}

    for nurse, shifts in schedule.items():
        last_shift = None
        consecutive_working_days = 0
        consecutive_same_shift = 0
        prev_shift = None

        for shift in reversed(shifts):
            if shift != "-":
                consecutive_working_days += 1
                if prev_shift is None or shift == prev_shift:
                    consecutive_same_shift += 1
                else:
                    break
                prev_shift = shift
                if last_shift is None:
                    last_shift = shift
            else:
                break

        carryover[nurse] = {
            "last_assigned_shift": last_shift,
            "consecutive_working_days": consecutive_working_days,
            "consecutive_same_shift_type": consecutive_same_shift,
        }

    return carryover


def calculate_h1_penalty(nurses, assignments):
    """
    H1: Only one assignment per day, 10 penalty points for each violation
    Check if a nurse has more than one shift on the same day
    Input: nurses (from scenario), assignments (current schedule)
    Output: penalty score (int)
    """
    penalty = 0
    for nurse_id in nurses:
        for assignment in assignments:
            if assignment["nurse"] == nurse_id:
                day = assignment["day"]
                if len(assignments[nurse_id][day]) > 1:
                    penalty += (len(assignments[nurse_id][day]) - 1) * 10

    return penalty


def calculate_h2_penalty(nurses, assignments, week_data_filepath):
    """
    H2: undersupply of required skills, 1 penalty point for each missing nurse
    Check a nurse is assigned to a shift that requires a skill they do not have
    Input: nurses (from scenario), assignments (current schedule), week_data (dict)
    Output: penalty score (int)
    """
    # Load week data
    with open(week_data_filepath, "r") as f:
        week_data = json.load(f)

    # Map nurse ID to skills
    nurse_skills = {n["id"]: set(n["skills"]) for n in nurses}

    # Count valid assignments by (day, shift, skill)
    coverage_count = {}
    for assignment in assignments:
        key = (assignment["shiftType"], assignment["skill"], assignment["day"])
        # Calculate skill-qualified assignments(H4: legel assignments)
        if assignment["skill"] in nurse_skills.get(assignment["nurse"], set()):
            coverage_count[key] = coverage_count.get(key, 0) + 1

    # Compare against week requirements (H2)
    penalty = 0

    for req in week_data["requirements"]:
        shift = req["shiftType"]
        skill = req["skill"]
        for day in DAYS_WEEK:
            day_key = f"requirementOn{day}"
            if day_key in req:
                minimum_required = req[day_key]["minimum"]
                actual_coverage = coverage_count.get((shift, skill, day[0:3]), 0)
                if actual_coverage < minimum_required:
                    penalty += minimum_required - actual_coverage
    return penalty


def calculate_h3_penalty(forbidden_successions, assignments):
    """
    H3: Forbidden shift successions, 20 penalty points for each violation
    Check if a nurse is assigned to a shift that is forbidden to follow the previous shift
    Input: forbidden_successions (from scenario), assignments (current schedule)
    Output: penalty score (int)
    """
    # Create a daily nurse shift schedule dict
    # e.g., {nurse_id: { day: shiftType }}
    nurse_schedule = {}
    for assignment in assignments:
        nurse = assignment["nurse"]
        day = assignment["day"]
        shift = assignment["shiftType"]
        nurse_schedule.setdefault(nurse, {})[day] = shift

    # Convert the forbidden successions list to a map for quick lookup
    # e.g., {"Late": {"Early", "Late"}, "Early": {"Late"}}
    forbidden_map = {}
    for rule in forbidden_successions:
        preceding = rule["precedingShiftType"]
        succeeding_list = rule["succeedingShiftTypes"]
        forbidden_map.setdefault(preceding, set()).update(succeeding_list)

    # Calculate the number of violations
    penalty = 0
    for nurse, schedule in nurse_schedule.items():
        for i in range(len(DAYS_WEEK_ABB) - 1):
            day1 = DAYS_WEEK_ABB[i]
            day2 = DAYS_WEEK_ABB[i + 1]
            shift1 = schedule.get(day1)
            shift2 = schedule.get(day2)

            if shift1 and shift2:
                if shift2 in forbidden_map.get(shift1, set()):
                    penalty += 20

    return penalty


def calculate_h4_penalty(nurses, assignments):
    """
    H4: The skill needs of each shift must be met, 1 penalty point for each missing skill
    Check if the nurse has been assigned to a shift that they do not have the required skill for
    Input: nurses (from scenario), assignments (current schedule)
    Output: penalty score (int)
    """
    # Map nurse ID to skill set
    nurse_skills = {n["id"]: set(n["skills"]) for n in nurses}

    penalty = 0
    for assignment in assignments:
        nurse_id = assignment["nurse"]
        required_skill = assignment["skill"]
        if required_skill not in nurse_skills.get(nurse_id, set()):
            penalty += 2  # Penalty +2
    return penalty


def calculate_total_penalty(nurses, forbidden_successions, assignments, week_filepath):
    h1 = calculate_h1_penalty(nurses, assignments)
    h2 = calculate_h2_penalty(nurses, assignments, week_filepath)
    h3 = calculate_h3_penalty(forbidden_successions, assignments)
    h4 = calculate_h4_penalty(nurses, assignments)
    print(f"H1: {h1}, H2: {h2}, H3: {h3} H4: {h4}")
    return h1 + h2 + h3 + h4


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
    current_penalty = calculate_h2_penalty(nurses, current_assignments, week_filepath)
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

    # Randomly assign 3–5 shifts to each nurse, skip duplicates
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

    assignment = simulated_annealing(
        assignments, forbidden_successions, nurses, shift_types, weekdata_filepath
    )

    one_week_solution = package_solution_2JSON(assignments, scenario["id"])

    return one_week_solution


def optimal_scheduler(sce_filepath, weekdata_filepath):
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
    assignments = []

    # Initialize an empty map to track assigned shifts per day
    shift_coverage = {
        day: {shift: False for shift in shift_types} for day in DAYS_WEEK_ABB
    }

    # Ensure each shift per day has at least one nurse
    for day in DAYS_WEEK_ABB:
        for shift in shift_types:
            # Find eligible nurses who can take this shift
            random.shuffle(nurses)  # Shuffle to randomize selection
            for nurse in nurses:
                # Check H1: maximum one shift per nurse per day
                if any(
                    a["nurse"] == nurse["id"] and a["day"] == day for a in assignments
                ):
                    continue
                skill = random.choice(nurse["skills"])
                prev_shift = (
                    None  # Simplified assumption: no previous shift in this pass
                )

                # Check H3: forbidden succession rules
                valid = all(
                    not (
                        rule["precedingShiftType"] == prev_shift
                        and shift in rule["succeedingShiftTypes"]
                    )
                    for rule in scenario["forbiddenShiftTypeSuccessions"]
                )
                if valid:
                    assignments.append(
                        {
                            "nurse": nurse["id"],
                            "day": day,
                            "shiftType": shift,
                            "skill": skill,
                        }
                    )
                    shift_coverage[day][shift] = True
                    break  # Move on to the next shift

    assignments = simulated_annealing(
        assignments, forbidden_successions, nurses, shift_types, weekdata_filepath
    )

    # Visualize the schedule in an easy-to-read table format in terminal
    tablate_schedule(assignments)

    return assignments


def parse_week_solution(assignments):
    """
    Parse a json format to a dictionary format.
    Input: json format solution
    Output: schedule in dictionary format
    """

    nurses = set()
    nurses.update(a["nurse"] for a in assignments)

    # Initialize empty schedule
    schedule_dict = defaultdict(lambda: ["-"] * 7)

    for assignment in assignments:
        nurse = assignment["nurse"]
        day = assignment["day"]
        shift = assignment["shiftType"]
        skill = assignment["skill"]
        day_idx = DAYS_WEEK_ABB.index(day)
        schedule_dict[nurse][day_idx] = (shift, skill)

    print(assignment)

    return schedule_dict


def tablate_schedule(assignments):
    """
    Convert a list of assignment dicts into a nurse-wise weekly schedule table
    Input: assignments (list of dicts)
    Output: print a table (row = nurse, col = day, cell = shift(skill))
    """

    schedule = {}
    for assignment in assignments:
        nurse = assignment["nurse"]
        day = assignment["day"]
        shift = assignment["shiftType"]
        skill = assignment["skill"]

        if nurse not in schedule:
            schedule[nurse] = ["-"] * 7  # 每位護士的每一天都初始化為 -

        day_index = DAYS_WEEK_ABB.index(day)
        schedule[nurse][day_index] = (shift, skill)

    # Print the header
    print(f"{'Name':<10} " + " ".join(f"{day:<10}" for day in DAYS_WEEK_ABB))
    print("-" * 10 + " " + " ".join("-" * 10 for _ in DAYS_WEEK_ABB))

    # Print each nurse's schedule
    for name, shifts in schedule.items():
        row = []
        for entry in shifts:
            if entry == "-":
                row.append("-")
            else:
                shift, skill = entry
                skill_abbr = skill[0]  # e.g., HeadNurse → H, Nurse → N
                row.append(f"{shift}({skill_abbr})")
        print(f"{name:<10} " + " ".join(f"{cell:<10}" for cell in row))


def package_solution_2JSON(assignments, weekdata_filepath):
    """
    Package the solution into a JSON format and write to a file.
    - Extracts scenario from filename (-<scenario_id>-)
    - Extracts week number (the final number before .json)
    """
    filename = os.path.basename(weekdata_filepath)  # e.g., WD-n021w4-0.json

    # Extract the scenario and week from the filename
    match = re.match(r".*-([^-]+)-(\d+)\.json", filename)
    if not match:
        raise ValueError(f"Filename format is incorrect: {filename}")

    scenario = match.group(1)  # 'n021w4'
    week = int(match.group(2))  # '0'

    # Create solution JSON
    solution = {
        "scenario": scenario,
        "week": week,
        "assignments": assignments,
    }

    # Output directory and file path
    output_dir = os.path.dirname(weekdata_filepath)  # e.g., testdatasets_json/n021w4
    output_path = os.path.join(output_dir, f"Sol-{scenario}-{week}.json")

    # Write JSON file
    with open(output_path, "w") as f:
        json.dump(solution, f, indent=4)

    return solution


# # 🧪 測試使用
# sol_file = "testdatasets_json/n005w4/Solution_H_0-WD_1-2-3-3/Sol-n005w4-1-0.json"  # 你的 JSON solution 檔案
# personal_schedule = parse_json_solution(sol_file)
# print(personal_schedule)
# carryover = generate_carryover(personal_schedule)

# # 印出結果
# for nurse, info in carryover.items():
#     print(
#         f"{nurse}: Last={info['last_assigned_shift']}, "
#         f"WorkDays={info['consecutive_working_days']}, "
#         f"SameShiftDays={info['consecutive_same_shift_type']}"
#     )


final_assignments = optimal_scheduler(
    "testdatasets_json/n021w4/Sc-n021w4.json",
    "testdatasets_json/n021w4/WD-n021w4-0.json",
)

package_solution_2JSON(final_assignments, "testdatasets_json/n021w4/WD-n021w4-0.json")
