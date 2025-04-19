import os
import json
import itertools

import networkx as nx
import matplotlib.pyplot as plt

from collections import defaultdict


# Read and get solution in a scenario
def read_solution(dir_path):
    """
    Read a JSON file and return the parsed data.
    """
    # Read all files start with "Sol-" in the directory
    json_files = [f for f in os.listdir(dir_path) if f.startswith("Sol-")]

    for json_file in json_files:
        file_path = os.path.join(dir_path, json_file)

        # Read JSON file
        with open(file_path, "r") as f:
            data = json.load(f)

        final_schedule = []
        final_schedule.append(data["assignments"])

    return final_schedule


def cal_coop_graph(final_schedule):
    """
    Given a list of assignment dictionaries, calculate cooperation intensity w_{ij}
    and return it as a list of dicts.
    """
    # Flatten if needed
    if (
        isinstance(final_schedule, list)
        and len(final_schedule) == 1
        and isinstance(final_schedule[0], list)
    ):
        final_schedule = final_schedule[0]

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

    return cooperation_list


def load_previous_coopdata(output_dir, prev_run_id):
    path = os.path.join(output_dir, f"coop-intensity-{prev_run_id}.json")
    if not os.path.exists(path):
        return []
    with open(path, "r") as f:
        return json.load(f)


def accumulate_coopdata(current, previous):
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



def write_coopdata_2json(data, output_dir, run_id):
    """
    Write data to a JSON file.
    """
    output_path = os.path.join(output_dir, f"coop-intensity-{run_id}.json")
    with open(output_path, "w") as f:
        json.dump(data, f, indent=4)


def visual_cooperation_graph(data, output_dir, run_id):
    """
    Visualize the cooperation graph using NetworkX and Matplotlib.
    """

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

    output_img_path = output_dir + "/coop-graph.png"
    plt.savefig(output_img_path)
    plt.close()



def simulate_one_run(sol_dir, run_id=0):
    """
    Main callable function to simulate and accumulate cooperation graphㄡ
    """
    
    schedule = read_solution(f"{sol_dir}/Solutions-{run_id}")
    coop_intensity = cal_coop_graph(schedule)
    
    # Merge with previous cooperation data
    if int(run_id) > 1:
        prev_coop = load_previous_coopdata(sol_dir, str(int(run_id) - 1))
        coop_intensity = accumulate_coopdata(coop_intensity, prev_coop)

    write_coopdata_2json(coop_intensity, sol_dir, run_id)
    visual_cooperation_graph(coop_intensity, sol_dir, run_id)


if __name__ == "__main__":
    import sys
    run_id = sys.argv[1] if len(sys.argv) > 1 else "0"
    simulate_one_run("Output/n021w4", run_id)