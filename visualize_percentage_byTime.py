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
new_staff_ratios = [
    1 / 9,
    2 / 8,
    3 / 7,
    4 / 6,
    5 / 5,
    6 / 4,
    7 / 3,
    8 / 2,
    9 / 1,
]  # Ratios of new staff to existing staff

# Plotting setup
plt.figure(figsize=(12, 8))

# Loop over each new staff ratio
for n in new_staff_ratios:
    # Calculate cooperation cost over time for current number of new staff
    cooperation_costs = C0 * np.exp(-k * days) + a * np.log(b * n + 1) + c
    plt.plot(
        days,
        cooperation_costs,
        marker="o",
        linestyle="-",
        label=f"New Staff Ratio = {n:.3f}",
        color="gray",
    )

# Finalizing the plot
plt.title("Cooperation Cost Over Time for 1 Senior with Various New Staff Ratios")
plt.xlabel("Time (Days)")
plt.ylabel("Cooperation Cost")
plt.grid(True)
plt.legend()
plt.show()
