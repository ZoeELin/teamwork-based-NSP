import json
import random
import math
import copy
import os
import re
import time
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


def build_cooperation_lookup(cooperation_data):
    """
    Turn cooperation_data (list of dicts) into a two-way lookup table
    e.g., lookup["Alice"]["Bob"] = 15
    """
    lookup = {}
    for entry in cooperation_data:
        n1 = entry["nurse1"]
        n2 = entry["nurse2"]
        score = entry["cooperation_score"]
        lookup.setdefault(n1, {})[n2] = score
        lookup.setdefault(n2, {})[n1] = score  # 雙向對稱
    return lookup


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

    assignments = simulated_annealing(
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
            history = json.load(f)
        nurseHistory = {
            data["nurse"]: data["lastAssignedShiftType"]
            for data in history["nurseHistory"]
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
    nurse_last_shift = defaultdict(lambda: None)  # nurse_id -> (day, shift)
    nurse_day_shift = defaultdict(lambda: {})  # nurse_id -> {day: shift}

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
                if count >= needed:
                    break
                nurse_id = nurse["id"]

                # H1: Only one assignment per day
                if day in nurse_day_shift[nurse_id]:
                    continue  # Break h1, skip this nurse

                # H4: Nurses missing required skill
                if skill not in nurse["skills"]:
                    continue  # Break h4, ship this nurse

                # H3: Chech forbidden succession
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

    tablate_schedule(assignments)

    calculate_total_penalty(
        nurses, forbidden_successions, assignments, weekdata_filepath
    )

    create_next_history_data(assignments, his_filepath)

    return assignments


def create_next_history_data(assignments, prev_history_filepath):
    """
    Create a new history record based on the current week's assignments and the previous history data.
    Input: assignments (list of dicts), history filepath (str)
    Output: new history data (dict)
    """

    # Create nurses list
    nurses_list = defaultdict(list)
    for a in assignments:
        nurses_list[a["nurse"]].append(a)

    # Read and get previous history data
    with open(prev_history_filepath, "r") as f:
        prev_history_data = json.load(f)

    prev_week = prev_history_data["week"]
    scenario = prev_history_data["scenario"]
    prev_nurseHistory = prev_history_data["nurseHistory"]

    prev_nurse_history = {n["nurse"]: n for n in prev_nurseHistory}

    new_nurse_history = []

    for nurse_id in prev_nurse_history:
        prev_record = prev_nurse_history[nurse_id]
        new_record = {
            "nurse": nurse_id,
            "numberOfAssignments": prev_record["numberOfAssignments"],
            "numberOfWorkingWeekends": prev_record["numberOfWorkingWeekends"],
            "lastAssignedShiftType": "None",
            "numberOfConsecutiveAssignments": 0,
            "numberOfConsecutiveWorkingDays": 0,
            "numberOfConsecutiveDaysOff": 0,
        }

        # Get this week's assignments for the nurse
        nurse_week_assignments = nurses_list.get(nurse_id, [])
        assigned_days = [
            a["day"] for a in nurse_week_assignments
        ]  # e.g., ['Mon', 'Tue', 'Wed']
        last_shift = None

        # Change numberOfAssignments of this week
        num_assignments = len(nurse_week_assignments)
        new_record["numberOfAssignments"] += num_assignments

        # Change numberOfWorkingWeekends if the nurse worked on Sat or Sun
        if "Sat" in assigned_days:
            new_record["numberOfWorkingWeekends"] += 1
        if "Sun" in assigned_days:
            new_record["numberOfWorkingWeekends"] += 1

        # Change lastAssignedShiftType if the nurse worked on Sunday
        if "Sun" in assigned_days:
            for a in nurse_week_assignments:
                if a["day"] == "Sun":
                    last_shift = a["shiftType"]
                    break
            new_record["lastAssignedShiftType"] = last_shift

        if last_shift:
            # Counting consecutive equal classes in reverse week day order
            count_work_day = 0
            count_same_shift = 0
            for day in reversed(DAYS_WEEK_ABB):
                for a in reversed(nurse_week_assignments):
                    if a["day"] == day and a["shiftType"] == last_shift:
                        count_same_shift += 1
                        count_work_day += 1
                    elif a["day"] == day:
                        count_work_day += 1
                    else:
                        continue  # Skip this nurse_week_assignment
                break  # Stop counting when not work at that day
            new_record["numberOfConsecutiveAssignments"] = count_same_shift
            new_record["numberOfConsecutiveWorkingDays"] = count_work_day
        else:
            count_off_day = 0
            for day in reversed(DAYS_WEEK_ABB):
                if day not in assigned_days:
                    count_off_day += 1
                else:
                    break
            new_record["numberOfConsecutiveDaysOff"] = count_off_day

        new_nurse_history.append(new_record)

    # Formating to JSON history
    history_json = {
        "week": prev_week + 1,
        "scenario": scenario,
        "nurseHistory": new_nurse_history,
    }

    # Output directory and file path
    output_dir = os.path.dirname(prev_history_filepath)
    output_path = os.path.join(output_dir, f"H{prev_week+1}-{scenario}.json")

    # Write JSON file
    with open(output_path, "w") as f:
        json.dump(history_json, f, indent=4)


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
            schedule[nurse] = [
                "-"
            ] * 7  # Initialize each nurse's shift '-' for each day

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


def package_solution_2JSON(assignments, output_dir, scenario_id, week_id):
    """
    Package the solution into a JSON format and write to a file.
    - Extracts scenario from filename (-<scenario_id>-)
    - Extracts week number (the final number before .json)
    """
    # Create solution JSON
    solution = {
        "scenario": scenario_id,
        "week": week_id,
        "assignments": assignments,
    }

    # Output directory and file path
    output_path = os.path.join(output_dir, f"Sol-{scenario_id}-{week_id}.json")

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


# final_assignments = supreme_scheduler(
#     "testdatasets_json/n021w4/Sc-n021w4.json",
#     "testdatasets_json/n021w4/WD-n021w4-0.json",
# )

# package_solution_2JSON(final_assignments, "testdatasets_json/n021w4/WD-n021w4-0.json")


def main():
    sce_path = "testdatasets_json/n005w4/Sc-n005w4.json"
    output_dir = os.path.dirname(sce_path)
    WD_files = [f for f in os.listdir(output_dir) if f.startswith("WD-")]

    start = time.perf_counter()

    for week_data_filename in WD_files:
        print(f"\nProcessing: {week_data_filename}")
        print("=" * 80)
        wd_path = os.path.join(output_dir, week_data_filename)
        print(wd_path)
        final_assignments = supreme_scheduler(sce_path, wd_path)

        # Extract the scenario and week from the filename
        match = re.match(r".*-([^-]+)-(\d+)\.json", week_data_filename)
        if not match:
            raise ValueError(f"Filename format is incorrect: {week_data_filename}")

        scenario_name = match.group(1)
        week_id = int(match.group(2))

        package_solution_2JSON(final_assignments, output_dir, scenario_name, week_id)

    end = time.perf_counter()

    print(f"\nExecution time: {end - start:.4f} seconds")


def test_one_week():
    sce_path = "testdatasets_json/n005w4/Sc-n005w4.json"
    weekdata_path = "testdatasets_json/n005w4/WD-n005w4-0.json"
    history_path = "testdatasets_json/n005w4/H0-n005w4-0.json"
    supreme_scheduler(sce_path, weekdata_path, history_path)


if __name__ == "__main__":
    test_one_week()
