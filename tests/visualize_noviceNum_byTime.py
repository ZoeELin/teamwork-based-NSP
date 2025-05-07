import matplotlib.pyplot as plt
import numpy as np

# Parameters for the model
C0 = 20  # Initial cooperation cost
k = 0.1  # Decay constant
C_min = 5  # Minimum cooperation cost after team becomes familiar
a = 10  # Constant for new staff cost
b = 2  # Scale factor for number of new staff
c = 5  # Base cost due to new staff

days = np.arange(
    1, 60
)  # Time in days set to 60, that novice staffs will inprove their skills
new_staff_counts = np.arange(1, 11)  # Number of new staff from 0 to 10

# Plotting setup
plt.figure(figsize=(12, 8))


# Loop over each new staff count
for n in new_staff_counts:
    # Calculate cooperation cost over time for current number of new staff
    extra_costs_decay = (a * np.log(b * n + 1) + c) * np.exp(-k * days)
    cooperation_costs = (C0 - C_min) * np.exp(-k * days) + extra_costs_decay + C_min

    plt.plot(
        days,
        cooperation_costs,
        marker="o",
        linestyle="-",
        label=f"New Staff = {n}",
    )

# Finalizing the plot
plt.title("Cooperation Cost Over Time with New Staff")
plt.xlabel("Time (Days)")
plt.ylabel("Cooperation Cost")
plt.grid(True)
plt.legend()
plt.show()
