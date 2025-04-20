import json
import os
from collections import defaultdict

from constants import DAYS_WEEK_ABB


def create_next_history_data(assignments, prev_history_filepath, output_dir):
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
    output_path = os.path.join(output_dir, f"H{prev_week+1}-{scenario}.json")

    # Write JSON file
    with open(output_path, "w") as f:
        json.dump(history_json, f, indent=4)

    return output_path
