import json

def calculate_total_cooperation_score(file_path):
    with open(file_path, 'r') as f:
        data = json.load(f)
    
    total_score = sum(entry["cooperation_score"] for entry in data)
    print(f"Total Cooperation Score: {total_score:.6f}")
    return total_score


file_path = "Output_comc100_0515_base_test/n030w4/coop-intensity-comc100-2.json"  
calculate_total_cooperation_score(file_path)