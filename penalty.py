import json

from constants import DAYS_WEEK_ABB, DAYS_WEEK


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
