import random
import json
import os
import networkx as nx
import matplotlib.pyplot as plt

# === 1. Read scenario file ===
# Put the path of the scenario file here!
sce_filepath = "testdatasets_json/n012w8/Sc-n012w8.json"
with open(sce_filepath, "r") as f:
    scenario = json.load(f)

nurses = [nurse["id"] for nurse in scenario["nurses"]]  # Get nurse name or id

# === 2. Build graph and create the degree of random cooperation ===
G = nx.Graph()
G.add_nodes_from(nurses)

cooperation_data = []

for i in range(len(nurses)):
    for j in range(i + 1, len(nurses)):
        nurse1 = nurses[i]
        nurse2 = nurses[j]
        score = round(random.randint(0, 30), 2)
        if score > 0:
            G.add_edge(nurse1, nurse2, weight=score)

        # Add cooperation data
        cooperation_data.append(
            {"nurse1": nurse1, "nurse2": nurse2, "cooperation_score": score}
        )

# === 3. Store graph into JSON ===
output_dir = os.path.dirname(sce_filepath)
output_json_path = output_dir + "/colab_graph.json"
with open(output_json_path, "w") as f:
    json.dump(cooperation_data, f, indent=2)

# === 4. Drawing and saving pictures ===
plt.figure(figsize=(8, 6))
pos = nx.spring_layout(G, seed=42)
edge_labels = nx.get_edge_attributes(G, "weight")
nx.draw(G, pos, with_labels=True, node_color="lightblue", node_size=2000, font_size=10)
# nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels)  # Show edge labels

plt.title("Nurse Cooperation Graph")
plt.tight_layout()

output_img_path = output_dir + "/colab_graph.png"
plt.savefig(output_img_path)
plt.close()
