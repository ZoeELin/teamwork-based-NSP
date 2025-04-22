import os
import json
import itertools
import argparse

import networkx as nx
import matplotlib.pyplot as plt

from collections import defaultdict


# Read and get solution in a scenario
def read_solution(dir_path):
    """
    Read all JSON file in directory and return the parsed data(a schedule).
    """
    # Read all files start with "Sol-" in the directory
    print(f"\nReading solution files from {dir_path}...📂")
    json_files = [f for f in os.listdir(dir_path) if f.startswith("Sol-")]
    final_schedule = []

    for json_file in json_files:
        file_path = os.path.join(dir_path, json_file)

        # Read JSON file
        with open(file_path, "r") as f:
            data = json.load(f)

        final_schedule.append(data["assignments"])

    return final_schedule


def cal_coop_graph(final_schedule):
    """
    Given a list of assignment dictionaries, calculate cooperation intensity w_{ij}
    and return it as a list of dicts.
    """
    print("Calculating cooperation intensity...")
    # Flatten if it's a list of lists (e.g., multi-week schedule)
    if isinstance(final_schedule, list) and all(isinstance(x, list) for x in final_schedule):
        final_schedule = [item for sublist in final_schedule for item in sublist]

    # Group by (day, shiftType)
    shift_assignments = defaultdict(list)
    for a in final_schedule:
        key = (a["day"], a["shiftType"])
        shift_assignments[key].append(a["nurse"])

    # Compute cooperation weights
    cooperation_weights = defaultdict(float)
    for nurses in shift_assignments.values():
        unique_nurses = sorted(set(nurses))
        if len(unique_nurses) <= 1:
            continue
        weight = 1 / (len(unique_nurses) - 1)
        for i, j in itertools.combinations(unique_nurses, 2):
            cooperation_weights[(i, j)] += weight

    # Format as list of dicts (only one direction per pair)
    nurses_coop_pairs = set()
    for (i, j), w in cooperation_weights.items():
        nurse1, nurse2 = sorted([i, j])
        nurses_coop_pairs.add((nurse1, nurse2, w))

    # Convert to list of dicts
    cooperation_list = [
        {"nurse1": i, "nurse2": j, "cooperation_score": w}
        for (i, j, w) in nurses_coop_pairs
    ]

    print(f"They are {len(cooperation_list)} pairs of nurses👥 in cooperations.")

    return cooperation_list


def load_previous_coopdata(output_dir, prev_filename):
    print(f"Loading previous cooperation data from {prev_filename}...📂")
    
    path = os.path.join(output_dir, prev_filename)
    if not os.path.exists(path):
        return []
    with open(path, "r") as f:
        return json.load(f)


def accumulate_coopdata(current, previous):
    print("Accumulating history cooperation data into current coopration data...")
    coop_dict = defaultdict(float)

    # Add previous data
    for entry in previous:
        key = tuple(sorted((entry["nurse1"], entry["nurse2"])))
        coop_dict[key] += entry["cooperation_score"]

    # Add previous data to current data
    for entry in current:
        key = tuple(sorted((entry["nurse1"], entry["nurse2"])))
        coop_dict[key] += entry["cooperation_score"]

    # Convert to list of dicts
    return [
        {"nurse1": i, "nurse2": j, "cooperation_score": w}
        for (i, j), w in coop_dict.items()
    ]


def write_coopdata_2json(data, output_dir, run_id, comcw=0):
    """
    Write data to a JSON file.
    """
    print(f"\nWriting cooperation data to JSON file...💾")

    if comcw == 0:
        output_path = os.path.join(output_dir, f"coop-intensity-{run_id}.json")
    else:
        output_path = os.path.join(
            output_dir, f"coop-intensity-comc{comcw}-{run_id}.json"
        )
    
    try:
        with open(output_path, "w") as f:
            json.dump(data, f, indent=4)
    except Exception as e:
        print(f"Error writing to JSON file: {e}")
        return

    print(f"✅ Cooperation data saved to {output_path}")


def visual_cooperation_graph(data, output_dir, run_id, comcw=0):
    """
    Visualize the cooperation graph using NetworkX and Matplotlib.
    """
    print("\nVisualizing cooperation graph...📊")
    G = nx.Graph()
    for entry in data:
        n1, n2 = entry["nurse1"], entry["nurse2"]
        score = entry["cooperation_score"]
        G.add_edge(n1, n2, weight=score)

    pos = nx.spring_layout(G, seed=42)
    nx.draw_networkx_nodes(G, pos, node_size=700, node_color="skyblue")
    edges = G.edges(data=True)
    weights = [d["weight"] for (_, _, d) in edges]
    nx.draw_networkx_edges(G, pos, width=[w * 2 for w in weights])
    # edge_labels = {(u, v): f'{d["weight"]:.1f}' for u, v, d in edges}
    # nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_size=8)
    nx.draw_networkx_labels(G, pos, font_size=8, font_weight="bold")
    plt.title("Nurse Cooperation Graph")
    plt.axis("off")
    # plt.tight_layout()

    # Save the graph as an image
    if comcw == 0:
        output_img_path = output_dir + f"/coop-graph-{run_id}.png"
    else:
        output_img_path = output_dir + f"/coop-graph-comc{comcw}-{run_id}.png"

    plt.savefig(output_img_path)
    plt.close()
    print(f"✅ Cooperation graph saved to {output_img_path}")


def simulate_one_run(output_dir, solution_dir, run_id, comc_w):
    """
    Main callable function to simulate and accumulate cooperation graphㄡ
    """
    # Read the solution
    print(f"Calculate {run_id}th execution of schedule(solutions) in {solution_dir} directory...")
    schedule = read_solution(solution_dir)

    # Calculate cooperation intensity from the solution
    coop_intensity = cal_coop_graph(schedule)

    # Merge with previous cooperation data
    if comc_w == 0:
        prev_filename = f"coop-intensity-{run_id}.json"
    else:
        prev_filename = f"coop-intensity-comc{comc_w}-{int(run_id)-1}.json"
    
    if int(run_id) > 1:
        prev_coop = load_previous_coopdata(output_dir, prev_filename)
        coop_intensity = accumulate_coopdata(coop_intensity, prev_coop)

    write_coopdata_2json(coop_intensity, output_dir, run_id, comc_w)
    visual_cooperation_graph(coop_intensity, output_dir, run_id, comc_w)


if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument("output_dir", help="Output folder to store results")
    parser.add_argument("sol_dir", help="Path to the solution folder")
    parser.add_argument("run_id", nargs="?", default="0", help="Run ID (default: 0)")
    parser.add_argument("--comc", type=int, default=0, help="Cooperation cost weight")

    args = parser.parse_args()

    dir = args.output_dir
    sol_dir = args.sol_dir
    run_id = args.run_id
    comc_weight = args.comc
    
    print(f"Start simulating intensity from {sol_dir}, and saving to {dir}\n")

    simulate_one_run(dir, sol_dir, run_id, comc_weight)
