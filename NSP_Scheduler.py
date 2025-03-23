import json
import random
import copy
import math
from collections import defaultdict

# Days of the week
DAYS = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]


def calculate_h2_penalty(nurses, assignments, week_data_filepath):
    """
    Calculate the total number of missing required skills from week data,
    based on the current schedule. Check against hard constraint H2.
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
        # Check H4: if nurse has the required skill
        if assignment["skill"] in nurse_skills.get(assignment["nurse"], set()):
            coverage_count[key] = coverage_count.get(key, 0) + 1

    # Compare against week requirements (H2)
    penalty = 0
    days_of_the_week = [
        "Monday",
        "Tuesday",
        "Wednesday",
        "Thursday",
        "Friday",
        "Saturday",
        "Sunday",
    ]
    for req in week_data["requirements"]:
        shift = req["shiftType"]
        skill = req["skill"]
        for day in days_of_the_week:
            day_key = f"requirementOn{day}"
            if day_key in req:
                minimum_required = req[day_key]["minimum"]
                actual_coverage = coverage_count.get((shift, skill, day[0:3]), 0)
                if actual_coverage < minimum_required:
                    penalty += minimum_required - actual_coverage
    return penalty


def get_neighbor(assignments, scenario, shift_ids):
    """
    Generate a neighbor solution by randomly modifying an assignment.
    """
    new_assignments = copy.deepcopy(assignments)

    # Randomly pick one assignment to modify
    index = random.randint(0, len(new_assignments) - 1)
    assignment = new_assignments[index]

    # Get the nurse object
    nurse = next(n for n in scenario["nurses"] if n["id"] == assignment["nurse"])

    # Randomly pick a new skill (nurse must have this skill)
    new_skill = random.choice(nurse["skills"])

    # Randomly pick a new shift
    new_shift = random.choice(shift_ids)

    # Apply the changes
    assignment["skill"] = new_skill
    assignment["shiftType"] = new_shift

    return new_assignments


def optimal_scheduler(sce_filepath, week_filepath):
    """
    Generate a random schedule for a given scenario,
    with consideration of hard constraints(H1, H3 from INRC2 definitions).
    Input: filepath to the scenario JSON file
    Output: a JSON object representing
    """
    # Load scenario
    with open(sce_filepath, "r") as f:
        scenario = json.load(f)

    shift_ids = [s["id"] for s in scenario["shiftTypes"]]
    nurses = scenario["nurses"]
    assignments = []

    # Initialize an empty map to track assigned shifts per day
    shift_coverage = {day: {shift: False for shift in shift_ids} for day in DAYS}

    # Ensure each shift per day has at least one nurse
    for day in DAYS:
        for shift in shift_ids:
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

    # ==== Simulated Annealing (SA) ====
    temperature = 100.0
    cooling_rate = 0.98
    min_temp = 0.1
    max_iter = 2000

    current_assignments = assignments
    current_penalty = calculate_h2_penalty(nurses, current_assignments, week_filepath)
    best_assignments = current_assignments
    best_penalty = current_penalty

    # for iteration in range(max_iter):
    #     if temperature < min_temp or best_penalty == 0:
    #         break

    #     neighbor_assignment = get_neighbor(current_assignments, scenario, shift_ids)
    #     neighbor_penalty = calculate_h2_penalty(
    #         nurses, neighbor_assignment, week_filepath
    #     )

    #     delta = neighbor_penalty - current_penalty
    #     if delta < 0 or random.random() < math.exp(-delta / temperature):
    #         current_assignments = neighbor_assignment
    #         current_penalty = neighbor_penalty

    #         if current_penalty < best_penalty:
    #             best_assignments = current_assignments
    #             best_penalty = current_penalty

    #     temperature *= cooling_rate

    print(f"Final H2 penalty: {best_penalty}")

    # Package as JSON
    one_week_solution = {
        "scenario": scenario["id"],
        "week": 0,
        "assignments": best_assignments,
    }

    return one_week_solution


def basic_scheduler(sce_filepath):
    """
    For Testing: generate a basic random schedule for a given scenario.
    Input: filepath to the scenario JSON file
    """
    # Load scenario
    with open(sce_filepath, "r") as f:
        scenario = json.load(f)

    shift_ids = [s["id"] for s in scenario["shiftTypes"]]
    nurses = scenario["nurses"]
    assignments = []

    # Initialize an empty map to track assigned shifts per day
    shift_coverage = {day: {shift: False for shift in shift_ids} for day in DAYS}

    # Randomly assign 3–5 shifts to each nurse, skip duplicates
    for nurse in scenario["nurses"]:

        assigned_days = random.sample(
            DAYS, k=random.randint(3, 5)
        )  # Randomly assign 3-5 shifts to each nurse

        prev_shift = None
        for day in sorted(
            assigned_days, key=lambda d: DAYS.index(d)
        ):  # Sort by day index
            valid_shifts = [
                s
                for s in shift_ids
                if not any(
                    rule["precedingShiftType"] == prev_shift
                    and s in rule["succeedingShiftTypes"]
                    for rule in scenario["forbiddenShiftTypeSuccessions"]
                )
            ]

    # Package as JSON
    one_week_schedule = {
        "scenario": scenario["id"],
        "week": 0,
        "assignments": assignments,
    }

    tablate_schedule(one_week_schedule)


def parse_week_solution(data):
    """
    Parse a json format to a dictionary format.
    Input: json format solution
    Output: schedule in dictionary format
    """
    assignments = data["assignments"]

    nurses = set()
    nurses.update(a["nurse"] for a in assignments)

    # Initialize empty schedule
    schedule_dict = defaultdict(lambda: ["-"] * 7)

    for assignment in data["assignments"]:
        nurse = assignment["nurse"]
        day = assignment["day"]
        shift = assignment["shiftType"]
        skill = assignment["skill"]
        day_idx = DAYS.index(day)
        schedule_dict[nurse][day_idx] = (shift, skill)

    return schedule_dict


def tablate_schedule(data):
    """
    Visualize the weekly schedule from a dictionary format to a table format,
    including assigned skill for each
    Input: schedule in JSON format
    Output: print in table format
    """

    # Parse the data
    data = parse_week_solution(data)

    # Print the header
    print(f"{'Name':<10} " + " ".join(f"{day:<10}" for day in DAYS))
    print("-" * 10 + " " + " ".join("-" * 10 for _ in DAYS))

    # Print each nurse's schedule
    for name, shifts in data.items():
        row = []
        for entry in shifts:
            if entry == "-":
                row.append("-")
            else:
                shift, skill = entry
                skill_abbr = skill[0]  # e.g., HeadNurse → H, Nurse → N
                row.append(f"{shift}({skill_abbr})")
        print(f"{name:<10} " + " ".join(f"{cell:<10}" for cell in row))


json_sol = optimal_scheduler(
    "testdatasets_json/n005w4/Sc-n005w4.json",
    "testdatasets_json/n005w4/WD-n005w4-0.json",
)
tablate_schedule(json_sol)
