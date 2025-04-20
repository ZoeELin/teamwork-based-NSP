import json
import os


from constants import DAYS_WEEK_ABB, DAYS_WEEK


def load_data(filepath):
    with open(filepath, "r") as f:
        return json.load(f)


def get_consecutive_sequences(binary_list):
    sequences = []
    count = 0
    for val in binary_list:
        if val:
            count += 1
        else:
            if count > 0:
                sequences.append(count)
            count = 0
    if count > 0:
        sequences.append(count)
    return sequences


def package_solution_2JSON(
    assignments, output_dir, scenario_id, week_id, run_id, use_ComC=False
):
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

    output_dir = f"Output/{scenario_id}/Solutions-{run_id}"
    if use_ComC:
        output_dir = f"Output/{scenario_id}/Solutions-ComC200-{run_id}"
    os.makedirs(output_dir, exist_ok=True)

    # Output directory and file path
    output_path = os.path.join(output_dir, f"Sol-{scenario_id}-{week_id}.json")

    # Write JSON file
    with open(output_path, "w") as f:
        json.dump(solution, f, indent=4)

    return solution


def display_schedule(assignments):
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
