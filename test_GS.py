import random
import copy
import json
from collections import defaultdict

# -----------------------------
# Load Data Utilities
# -----------------------------
def load_json(path):
    with open(path, 'r') as f:
        return json.load(f)

# -----------------------------
# Encoding & Initialization
# -----------------------------
def generate_random_schedule(nurses, days, shift_types):
    schedule = []
    for day in range(days):
        for nurse in nurses:
            shift = random.choice(shift_types + ['O'])  # 'O' means Off
            schedule.append({
                "nurse": nurse["id"],
                "day": day,
                "shiftType": shift
            })
    return schedule

# -----------------------------
# Fitness Evaluation
# -----------------------------
def calculate_penalty(schedule, nurses, scenario):
    # Simplified: penalize too many consecutive days worked
    nurse_days = defaultdict(list)
    for a in schedule:
        if a['shiftType'] != 'O':
            nurse_days[a['nurse']].append(a['day'])

    penalty = 0
    for nurse, days in nurse_days.items():
        days.sort()
        consecutive = 1
        for i in range(1, len(days)):
            if days[i] == days[i-1] + 1:
                consecutive += 1
                if consecutive > 5:
                    penalty += 5
            else:
                consecutive = 1
    return penalty

# -----------------------------
# Genetic Operators
# -----------------------------
def crossover(parent1, parent2):
    point = len(parent1) // 2
    return parent1[:point] + parent2[point:]

def mutate(schedule, shift_types, mutation_rate=0.01):
    for a in schedule:
        if random.random() < mutation_rate:
            a['shiftType'] = random.choice(shift_types + ['O'])
    return schedule

# -----------------------------
# Genetic Algorithm
# -----------------------------
def genetic_algorithm(nurses, shift_types, days, scenario, generations=100, pop_size=20):
    population = [generate_random_schedule(nurses, days, shift_types) for _ in range(pop_size)]
    
    for gen in range(generations):
        fitness_scores = [(s, calculate_penalty(s, nurses, scenario)) for s in population]
        fitness_scores.sort(key=lambda x: x[1])
        population = [fs[0] for fs in fitness_scores[:pop_size//2]]  # Select top half

        new_population = copy.deepcopy(population)
        while len(new_population) < pop_size:
            p1, p2 = random.sample(population, 2)
            child = crossover(copy.deepcopy(p1), copy.deepcopy(p2))
            child = mutate(child, shift_types)
            new_population.append(child)

        population = new_population
        print(f"Generation {gen}, Best Penalty: {fitness_scores[0][1]}")

    return fitness_scores[0][0]  # Best schedule

# -----------------------------
# Example Usage
# -----------------------------
if __name__ == '__main__':
    # Replace with your actual paths
    scenario = load_json('./datasets/scenario.json')
    week_data = load_json('./datasets/1week.json')

    nurses = scenario["nurses"]
    shift_types = [s["id"] for s in scenario["shiftTypes"]]
    days = scenario["numDays"]  # usually 7

    best_schedule = genetic_algorithm(nurses, shift_types, days, scenario)
    
    # Output best schedule
    print(json.dumps(best_schedule, indent=2))
