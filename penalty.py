import json
from collections import defaultdict
import itertools

from constants import DAYS_WEEK_ABB, DAYS_WEEK


def calculate_h1_penalty(assignments, nurses):
    """
    H1: Only one assignment per day, 10 penalty points for each violation
    Check if a nurse has more than one shift on the same day
    Input: nurses (from scenario), assignments (current schedule)
    Output: penalty score (int)
    """
    penalty = 0
    nurse_day_count = defaultdict(lambda: defaultdict(int))

    for assignment in assignments:
        nurse_id = assignment["nurse"]
        day = assignment["day"]
        nurse_day_count[nurse_id][day] += 1

    for nurse in nurses:
        nurse_id = nurse["id"]
        for day, count in nurse_day_count[nurse_id].items():
            if count > 1:
                penalty += (count - 1) * 1000

    return penalty


def calculate_h2_penalty(assignments, nurses, week_data_filepath):
    """
    H2: undersupply of required skills, 1 penalty point for each missing nurse.
    Check a nurse is assigned to a shift that requires a skill they do not have.
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
                    penalty += (minimum_required - actual_coverage) * 500
    return penalty


def calculate_h3_penalty(assignments, forbidden_successions):
    """
    H3: Forbidden shift successions, adding penalty points for each violation.
    Check if a nurse is assigned to a shift that is forbidden to follow the previous shift.
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
        nurse_schedule.setdefault(nurse, {}).setdefault(day, []).append(shift)

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
            shifts_day1 = schedule.get(day1, [])
            shifts_day2 = schedule.get(day2, [])

            for shift1 in shifts_day1:
                for shift2 in shifts_day2:
                    if shift2 in forbidden_map.get(shift1, set()):
                        penalty += 500

    return penalty


def calculate_h4_penalty(assignments, nurses):
    """
    H4: The skill needs of each shift must be met, adding point for each missing skill
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
            penalty += 1000  # Penalty +1
    return penalty


def calculate_s1_penalty(assignments, nurses, week_data_filepath):
    """
    S1: Insuﬃcient staﬃng for optimal coverage
    Check a nurse is assigned to a shift that requires the optimal skill they do not have.
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

    penalty = 0
    for req in week_data["requirements"]:
        shift = req["shiftType"]
        skill = req["skill"]
        for day in DAYS_WEEK:
            day_key = f"requirementOn{day}"
            if day_key in req:
                optimal_required = req[day_key]["optimal"]
                actual_coverage = coverage_count.get((shift, skill, day[0:3]), 0)
                if actual_coverage < optimal_required:
                    penalty += (optimal_required - actual_coverage) * 30
    return penalty


def calculate_ComC_penalty(assignments, cooperation_matrix, epsilon=0.01):
    """
    Calculate the ComC (Communication Cost) penalty score for the overall schedule.
    The fewer records of cooperation, the higher the ComC.
    Input: assignments (current schedule), cooperation_matrix (from cooperation graph), epsilon (default 0.01)
    Output: penalty score (float)
    """
    # Convert cooperation matrix to a dictionary for quick lookup
    coop_dict = {}
    for entry in cooperation_matrix:
        key1 = (entry["nurse1"], entry["nurse2"])
        key2 = (entry["nurse2"], entry["nurse1"])
        coop_dict[key1] = entry["cooperation_score"]
        coop_dict[key2] = entry["cooperation_score"]

    # Group assignments by (day, shiftType)
    shift_teams = defaultdict(list)
    for a in assignments:
        key = (a["day"], a["shiftType"])
        shift_teams[key].append(a["nurse"])

    # Calculate each shift's ComC
    team_penalties = 0
    for shift_key, nurses in shift_teams.items():
        if len(nurses) <= 1:
            continue
        team_total_cost = 0
        # Iterate over all nurse pairs(every two nurses) in the shift
        for i, j in itertools.combinations(nurses, 2):
            key = (i, j)
            coop_score = coop_dict.get(
                key, epsilon
            )  # Default to epsilon if they do not cooperate

            # Add the score to the total cost
            team_total_cost += coop_score / (len(nurses) - 1)

        # Calculate the ComC penalty for this shift, normalized by the number of nurses in the shift
        ComC = team_total_cost / len(nurses)
        team_penalties += ComC

    return team_penalties


def calculate_total_penalty(
    nurses, forbidden_successions, assignments, weekdata_filepath
):
    h1 = calculate_h1_penalty(assignments, nurses)
    h2 = calculate_h2_penalty(assignments, nurses, weekdata_filepath)
    h3 = calculate_h3_penalty(assignments, forbidden_successions)
    h4 = calculate_h4_penalty(assignments, nurses)
    print(f"H1: {h1}, H2: {h2}, H3: {h3} H4: {h4}")
    return h1 + h2 + h3 + h4


test_assignments = [
    {"nurse": "Stefaan", "day": "Mon", "shiftType": "Early", "skill": "HeadNurse"},
    {"nurse": "Stefaan", "day": "Mon", "shiftType": "Early", "skill": "Nurse"},
    {"nurse": "Andrea", "day": "Tue", "shiftType": "Night", "skill": "Nurse"},
    {"nurse": "Andrea", "day": "Wed", "shiftType": "Early", "skill": "Nurse"},
]

# test_assignments = [
#     {"nurse": "HN_0", "day": "Mon", "shiftType": "Early", "skill": "HeadNurse"},
#     {"nurse": "NU_3", "day": "Mon", "shiftType": "Early", "skill": "Nurse"},
#     {"nurse": "CT_14", "day": "Tue", "shiftType": "Night", "skill": "Nurse"},
#     {"nurse": "NU_3", "day": "Wed", "shiftType": "Early", "skill": "Nurse"},
#     {"nurse": "NU_2", "day": "Wed", "shiftType": "Early", "skill": "Nurse"},
# ]

test_nurses = [
    {"id": "Andrea", "contract": "FullTime", "skills": ["HeadNurse", "Nurse"]},
    {"id": "Stefaan", "contract": "PartTime", "skills": ["HeadNurse", "Nurse"]},
]

test_forbidden_successions = [
    {"precedingShiftType": "Early", "succeedingShiftTypes": []},
    {"precedingShiftType": "Late", "succeedingShiftTypes": ["Early"]},
    {"precedingShiftType": "Night", "succeedingShiftTypes": ["Early", "Late"]},
]


# print(calculate_h1_penalty(test_assignments, test_nurses))
# print(calculate_h3_penalty(test_assignments, test_forbidden_successions))
print(
    calculate_s1_penalty(
        test_assignments, test_nurses, "testdatasets_json/n005w4/WD-n005w4-0.json"
    )
)


# test_coop_matrix = [
#     {"nurse1": "HN_0", "nurse2": "NU_3", "cooperation_score": 0.5},
#     {"nurse1": "CT_14", "nurse2": "NU_10", "cooperation_score": 0.5},
#     {"nurse1": "HN_2", "nurse2": "TR_17", "cooperation_score": 1.5},
#     {"nurse1": "CT_14", "nurse2": "HN_1", "cooperation_score": 1.0},
#     {"nurse1": "NU_10", "nurse2": "TR_16", "cooperation_score": 0.5},
#     {"nurse1": "CT_14", "nurse2": "NU_3", "cooperation_score": 1.0},
#     {"nurse1": "CT_11", "nurse2": "NU_10", "cooperation_score": 0.3333333333333333},
#     {"nurse1": "NU_10", "nurse2": "NU_9", "cooperation_score": 1.0},
#     {"nurse1": "HN_0", "nurse2": "TR_17", "cooperation_score": 1.0},
#     {"nurse1": "NU_6", "nurse2": "TR_19", "cooperation_score": 0.5},
#     {"nurse1": "NU_8", "nurse2": "TR_16", "cooperation_score": 0.5},
#     {"nurse1": "CT_13", "nurse2": "TR_18", "cooperation_score": 0.5},
#     {"nurse1": "HN_0", "nurse2": "NU_5", "cooperation_score": 0.3333333333333333},
#     {"nurse1": "NU_6", "nurse2": "TR_16", "cooperation_score": 1.0},
#     {"nurse1": "NU_4", "nurse2": "NU_8", "cooperation_score": 0.5},
#     {"nurse1": "NU_9", "nurse2": "TR_20", "cooperation_score": 0.5},
#     {"nurse1": "HN_1", "nurse2": "TR_18", "cooperation_score": 0.3333333333333333},
#     {"nurse1": "NU_3", "nurse2": "TR_17", "cooperation_score": 0.5},
#     {"nurse1": "CT_13", "nurse2": "NU_7", "cooperation_score": 1.5},
#     {"nurse1": "NU_10", "nurse2": "TR_18", "cooperation_score": 0.3333333333333333},
#     {"nurse1": "HN_1", "nurse2": "TR_20", "cooperation_score": 0.5},
#     {"nurse1": "NU_9", "nurse2": "TR_18", "cooperation_score": 0.5},
#     {"nurse1": "NU_10", "nurse2": "NU_6", "cooperation_score": 1.0},
#     {"nurse1": "HN_2", "nurse2": "TR_16", "cooperation_score": 0.5},
#     {"nurse1": "NU_7", "nurse2": "TR_18", "cooperation_score": 0.5},
#     {"nurse1": "HN_1", "nurse2": "NU_9", "cooperation_score": 0.5},
#     {"nurse1": "CT_11", "nurse2": "TR_18", "cooperation_score": 0.3333333333333333},
#     {"nurse1": "NU_4", "nurse2": "TR_17", "cooperation_score": 0.5},
#     {"nurse1": "CT_11", "nurse2": "HN_1", "cooperation_score": 0.3333333333333333},
# ]


# print(calculate_ComC_penalty(test_assignments, test_coop_matrix))
