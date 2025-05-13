import json
from collections import defaultdict
import itertools
import os

import utils
from constants import DAYS_WEEK_ABB, DAYS_WEEK, WEEKEND_DAYS


def calculate_h1_penalty(assignments):
    """
    H1: Only one assignment per day
    Check if a nurse has more than one shift on the same day
    Input: nurses (from scenario), assignments (current schedule)
    Output: penalty score (int)
    """
    penalty = 0
    penalty_points = 1000
    nurse_day_count = defaultdict(lambda: defaultdict(int))

    for a in assignments:
        nurse_day_count[a["nurse"]][a["day"]] += 1

    for nurse_id, day_counts in nurse_day_count.items():
        for day, count in day_counts.items():
            if count > 1:
                penalty += (count - 1) * penalty_points

    return penalty


def calculate_h2_penalty(assignments, nurses, week_data):
    """
    H2: undersupply of required skills, 500 penalty point for each missing nurse.
    Check a nurse is assigned to a shift that requires a skill they do not have.
    Input: nurses (from scenario), assignments (current schedule), week_data (dict)
    Output: penalty score (int)
    """
    penalty_points = 500

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
                    penalty += (minimum_required - actual_coverage) * penalty_points
    return penalty


def calculate_h3_penalty(
    assignments, forbidden_successions, nurse_lastdayoflastweek_shift
):
    """
    H3: Forbidden shift successions, adding penalty points for each violation.
    Check if a nurse is assigned to a shift that is forbidden to follow the previous shift.
    Input: forbidden_successions (from scenario), assignments (current schedule)
    Output: penalty score (int)
    """
    penalty_points = 700

    # Step 1: Build nurse schedule per day
    nurse_schedule = {}
    for assignment in assignments:
        nurse = assignment["nurse"]
        day = assignment["day"]
        shift = assignment["shiftType"]
        nurse_schedule.setdefault(nurse, {}).setdefault(day, []).append(
            shift
        )  # e.g., {nurse_id: { day: shiftType }}

    # Step 2: Build forbidden map for fast lookup
    forbidden_map = {}
    for rule in forbidden_successions:
        preceding = rule["precedingShiftType"]
        succeeding_list = rule["succeedingShiftTypes"]
        forbidden_map.setdefault(preceding, set()).update(
            succeeding_list
        )  # e.g., {"Late": {"Early", "Late"}, "Early": {"Late"}}

    # Step 3: Calculate the number of violations
    penalty = 0
    for nurse, schedule in nurse_schedule.items():
        # 3.1 Check Mon vs. nurseHistory (previous week)
        history_shift = nurse_lastdayoflastweek_shift.get(nurse)
        monday_shifts = schedule.get("Mon", [])
        if history_shift and history_shift != "None":
            for shift in monday_shifts:
                if shift in forbidden_map.get(history_shift, set()):
                    penalty += penalty_points

        # 3.2 Check current week (Tue ~ Sun)
        for i in range(len(DAYS_WEEK_ABB) - 1):
            day1 = DAYS_WEEK_ABB[i]
            day2 = DAYS_WEEK_ABB[i + 1]
            shifts_day1 = schedule.get(day1, [])
            shifts_day2 = schedule.get(day2, [])

            for shift1 in shifts_day1:
                for shift2 in shifts_day2:
                    if shift2 in forbidden_map.get(shift1, set()):
                        penalty += penalty_points

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
    penalty_points = 1000
    for assignment in assignments:
        nurse_id = assignment["nurse"]
        required_skill = assignment["skill"]
        if required_skill not in nurse_skills.get(nurse_id, set()):
            penalty += penalty_points
    return penalty


def calculate_s1_penalty(assignments, nurses, week_data):
    """
    S1: Insuﬃcient staﬃng for optimal coverage
    Check a nurse is assigned to a shift that requires the optimal skill they do not have.
    Input: nurses (from scenario), assignments (current schedule), week_data (dict)
    Output: penalty score (int)
    """

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


def calculate_consecutive_work_penalty(work_seq, min_work, max_work, weight):
    penalty = 0
    sequences = utils.get_consecutive_sequences(work_seq)
    for length in sequences:
        if length < min_work:
            penalty += (min_work - length) * weight
        elif length > max_work:
            penalty += (length - max_work) * weight
    return penalty


def calculate_consecutive_off_penalty(work_seq, min_off, max_off, weight):
    penalty = 0
    off_seq = [1 - w for w in work_seq]
    sequences = utils.get_consecutive_sequences(off_seq)
    for length in sequences:
        if length < min_off:
            penalty += (min_off - length) * weight
        elif length > max_off:
            penalty += (length - max_off) * weight
    return penalty


def calculate_shift_specific_penalty(
    schedule, shift_constraints, nurse_id, days, weight
):
    penalty = 0
    for shift_type, limits in shift_constraints.items():
        shift_seq = [
            1 if schedule[nurse_id].get(day) == shift_type else 0 for day in days
        ]
        sequences = utils.get_consecutive_sequences(shift_seq)
        for length in sequences:
            if length < limits["min"]:
                penalty += (limits["min"] - length) * weight
            elif length > limits["max"]:
                penalty += (length - limits["max"]) * weight
    return penalty


def calculate_incomplete_weekend_penalty(schedule, nurse, weekend_days, weight):
    penalty = 0
    if nurse.get("completeWeekends", False):
        for sat, sun in weekend_days:
            worked_sat = schedule[nurse["id"]].get(sat) is not None
            worked_sun = schedule[nurse["id"]].get(sun) is not None
            if worked_sat != worked_sun:
                penalty += weight
    return penalty


def calculate_s2_s3_s5_penalty(assignments, nurses, scenario, nurseHistory):
    """
    Calculates penalties for:
    S2: Consecutive assignments
    S3: Consecutive days off
    S5: Complete weekend (only Sat+Sun or none)
    """
    nurse_contract_map = {n["id"]: n["contract"] for n in scenario["nurses"]}
    contract_limits = {c["id"]: c for c in scenario["contracts"]}
    shift_constraints = {
        s["id"]: {
            "min": s["minimumNumberOfConsecutiveAssignments"],
            "max": s["maximumNumberOfConsecutiveAssignments"],
        }
        for s in scenario["shiftTypes"]
    }

    history_lookup = {h["nurse"]: h for h in nurseHistory}

    schedule = defaultdict(lambda: defaultdict(lambda: None))  # nurse -> day -> shift
    for a in assignments:
        schedule[a["nurse"]][a["day"]] = a["shiftType"]

    total_penalty = 0
    for nurse in nurses:
        nurse_id = nurse["id"]
        contract_id = nurse_contract_map[nurse_id]
        contract = contract_limits[contract_id]
        history = history_lookup.get(
            nurse_id,
            {
                "numberOfConsecutiveAssignments": 0,
                "numberOfConsecutiveWorkingDays": 0,
                "numberOfConsecutiveDaysOff": 0,
            },
        )

        working_seq = [
            1 if schedule[nurse_id].get(day) else 0 for day in DAYS_WEEK_ABB
        ]  # e.g., [1, 0, 1, 1, 0, ...]
        # Extend the beginning with historical values
        if history["numberOfConsecutiveWorkingDays"] > 0:
            working_seq = [1] * history["numberOfConsecutiveWorkingDays"] + working_seq
        elif history["numberOfConsecutiveDaysOff"] > 0:
            working_seq = [0] * history["numberOfConsecutiveDaysOff"] + working_seq

        # S2
        total_penalty += calculate_consecutive_work_penalty(
            working_seq,
            contract["minimumNumberOfConsecutiveWorkingDays"],
            contract["maximumNumberOfConsecutiveWorkingDays"],
            weight=30,
        )
        total_penalty += calculate_shift_specific_penalty(
            schedule, shift_constraints, nurse_id, DAYS_WEEK_ABB, weight=15
        )

        # S3
        total_penalty += calculate_consecutive_off_penalty(
            working_seq,
            contract["minimumNumberOfConsecutiveDaysOff"],
            contract["maximumNumberOfConsecutiveDaysOff"],
            weight=30,
        )

        # S5
        total_penalty += calculate_incomplete_weekend_penalty(
            schedule, nurse, WEEKEND_DAYS, weight=30
        )

    return total_penalty


def calculate_s4_penalty(assignments, week_data):
    """
    S4: Preferences - Each assignment to an undesired shift is penalised.
    Nurses' shift off requests come from week_data["shiftOffRequests"].
    If a nurse is assigned to a shift they requested off, add penalty points.
    """
    # Build set of off requests for quick lookup
    off_requests = set()
    for req in week_data.get("shiftOffRequests", []):
        off_requests.add((req["nurse"], req["day"][0:3], req["shiftType"]))

    # Check all assignments
    penalty = 0
    penalty_points = 10
    for a in assignments:
        nurse = a["nurse"]
        day = a["day"]
        shift = a["shiftType"]

        # Match specific or 'Any' shift request
        if (nurse, day, shift) in off_requests or (nurse, day, "Any") in off_requests:
            penalty += penalty_points

    return penalty


def calculate_ComC_penalty(assignments, coop_filepath, weight, epsilon=0.01):
    """
    Calculate the ComC (Communication Cost) penalty score for the overall schedule.
    The fewer records of cooperation, the higher the ComC.
    Input: assignments (current schedule), epsilon (default 0.01), coop_dir (directory of cooperation matrix), id (iteration number)
    Output: penalty score (float)
    """
    cooperation_matrix = utils.load_data(coop_filepath)

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
        team_penalties += (ComC) * weight

    return team_penalties


def calculate_total_penalty(
    nurses,
    forbidden_successions,
    assignments,
    weekdata_filepath,
    scenario,
    nurses_lastshift_from_lastweek,
    nurseHistory,
    output_dir,
    comc_weight=0,
    print_each_penalty=False,
    run_id=0,
):
    # Load week data
    week_data = utils.load_data(weekdata_filepath)

    h1 = calculate_h1_penalty(assignments)
    h2 = calculate_h2_penalty(assignments, nurses, week_data)
    h3 = calculate_h3_penalty(
        assignments, forbidden_successions, nurses_lastshift_from_lastweek
    )
    h4 = calculate_h4_penalty(assignments, nurses)
    s1 = calculate_s1_penalty(assignments, nurses, week_data)
    s2_s3_s5 = calculate_s2_s3_s5_penalty(assignments, nurses, scenario, nurseHistory)
    s4 = calculate_s4_penalty(assignments, week_data)

    ComC = 0
    if run_id > 1 and comc_weight > 0:
        coop_filepath = os.path.join(
            output_dir, f"coop-intensity-comc{comc_weight}-{run_id-1}.json"
        )
        ComC = calculate_ComC_penalty(assignments, coop_filepath, comc_weight)

    total_penalties = h1 + h2 + h3 + h4 + s1 + s2_s3_s5 + s4 + ComC
    if print_each_penalty:
        print(
            f"penalties {round(total_penalties)} -- H1: {h1}, H2: {h2}, H3: {h3} H4: {h4}, S1: {s1}, S2+S3+S5: {s2_s3_s5}, S4: {s4}, ComC: {ComC:.4f}"
        )
    return total_penalties


# test_assignments = [
#     {"nurse": "Stefaan", "day": "Mon", "shiftType": "Early", "skill": "HeadNurse"},
#     {"nurse": "Stefaan", "day": "Mon", "shiftType": "Early", "skill": "Nurse"},
#     {"nurse": "Andrea", "day": "Tue", "shiftType": "Night", "skill": "Nurse"},
#     {"nurse": "Andrea", "day": "Wed", "shiftType": "Early", "skill": "Nurse"},
#     {"nurse": "Sara", "day": "Thu", "shiftType": "Early", "skill": "Nurse"},
#     {"nurse": "Stefaan", "day": "Sat", "shiftType": "Late", "skill": "Nurse"},
# ]

# test_assignments = [
#     {"nurse": "HN_0", "day": "Mon", "shiftType": "Early", "skill": "HeadNurse"},
#     {"nurse": "NU_3", "day": "Mon", "shiftType": "Early", "skill": "Nurse"},
#     {"nurse": "CT_14", "day": "Tue", "shiftType": "Night", "skill": "Nurse"},
#     {"nurse": "NU_3", "day": "Wed", "shiftType": "Early", "skill": "Nurse"},
#     {"nurse": "NU_2", "day": "Wed", "shiftType": "Early", "skill": "Nurse"},
# ]

# test_nurses = [
#     {"id": "Andrea", "contract": "FullTime", "skills": ["HeadNurse", "Nurse"]},
#     {"id": "Stefaan", "contract": "PartTime", "skills": ["HeadNurse", "Nurse"]},
# ]

# test_forbidden_successions = [
#     {"precedingShiftType": "Early", "succeedingShiftTypes": []},
#     {"precedingShiftType": "Late", "succeedingShiftTypes": ["Early"]},
#     {"precedingShiftType": "Night", "succeedingShiftTypes": ["Early", "Late"]},
# ]


# print(calculate_h1_penalty(test_assignments, test_nurses))
# print(calculate_h3_penalty(test_assignments, test_forbidden_successions))
# print(
#     calculate_s1_penalty(
#         test_assignments, test_nurses, "testdatasets_json/n005w4/WD-n005w4-0.json"
#     )
# )

# print(
#     calculate_s2_s3_s5_penalty(
#         test_assignments,
#         test_nurses,
#         "testdatasets_json/n005w4/Sc-n005w4.json",
#     )
# )

# print(
#     calculate_s4_penalty(test_assignments, "testdatasets_json/n005w4/WD-n005w4-0.json")
# )

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
