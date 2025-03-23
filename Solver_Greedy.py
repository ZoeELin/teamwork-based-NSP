import random

nurses = ["A", "B", "C"]
shifts = ["Early", "Late", "Night"]
schedule = {nurse: [] for nurse in nurses}

# 隨機分配班表，確保每班至少有一人
for shift in shifts:
    assigned_nurse = random.choice(nurses)
    schedule[assigned_nurse].append(shift)

print("Generated Schedule:")
for nurse, shifts in schedule.items():
    print(f"Nurse {nurse}: {shifts}")
