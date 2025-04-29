# Init_nurse_pairs.py

import os
import json
import argparse
import itertools


def read_nurses_from_scenario(scenario_file):
    """
    Read all nurse IDs from a scenario folder.
    """
    nurses = set()

    with open(scenario_file, "r") as f:
        data = json.load(f)
        sce_nurses = data.get("nurses", [])
        for nurse in sce_nurses:
            nurses.add(nurse["id"])

    print(f"Found {len(nurses)} unique nurses.")
    return nurses


def generate_all_pairs(nurses):
    """
    Generate all unique nurse pairs.
    """
    pairs = []
    for n1, n2 in itertools.combinations(nurses, 2):
        pairs.append({"nurse1": n1, "nurse2": n2, "cooperation_score": 0.0})

    print(f"Generated {len(pairs)} unique nurse pairs.")
    return pairs


def save_pairs(pairs, output_dir):
    """
    Save pairs to JSON.
    """
    os.makedirs(output_dir, exist_ok=True)

    with open(os.path.join(output_dir, "nurse_pairs.json"), "w") as f:
        json.dump(pairs, f, indent=4)
    print(f"✅ Nurse pairs saved to {output_dir}")


def main(scenario_dir, output_file):
    nurses = read_nurses_from_scenario(scenario_dir)

    pairs = generate_all_pairs(nurses)
    save_pairs(pairs, output_file)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("sce_file", help="Path to scenario file")
    parser.add_argument("output_dir", help="Path to output JSON directory")

    args = parser.parse_args()
    main(args.sce_file, args.output_dir)
