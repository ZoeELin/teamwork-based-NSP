import matplotlib.pyplot as plt
import numpy as np

# Parameters for the model
C0 = 20  # Initial cooperation cost
k = 0.1  # Decay constant
C_min = 5  # Minimum cooperation cost after team becomes familiar
a = 10  # Constant for new staff cost
b = 2  # Scale factor for number of new staff
c = 5  # Base cost due to new staff

days = np.arange(1, 31)  # Time in days from 1 to 30

total_staff = 10  # Total number of staff

# Scenarios with specified senior staff counts
senior_counts = [1, 3, 4]  # Different numbers of senior staff
scenarios = {
    f"{m}:{int((total_staff - m))}": {"m": m, "n": (total_staff - m) / m}
    for m in senior_counts
}


# Plotting setup
plt.figure(figsize=(12, 8))

# Loop over each scenario
for label, values in scenarios.items():
    m = values["m"]
    n = values["n"]
    # Calculate cooperation cost over time for current number of new staff
    extra_costs_decay = (a * np.log(b * n + 1) + c) * np.exp(-k * days)
    cooperation_costs = (C0 - C_min) * np.exp(-k * days) + extra_costs_decay + C_min

    plt.plot(
        days,
        cooperation_costs,
        marker="o",
        linestyle="-",
        label=f"Senior:New = {label} (r={n:.2f})",
    )

# Finalizing the plot
plt.title("Cooperation Cost Over Time for Different Staff Ratios")
plt.xlabel("Time (Days)")
plt.ylabel("Cooperation Cost")
plt.grid(True)
plt.legend()
plt.show()
