import matplotlib.pyplot as plt
import numpy as np

# Parameters for the exponential decay simulation
C0 = 20  # Initial cooperation cost
k = 0.1  # Decay constant
C_min = 5  # Minimum cooperation cost after team becomes familiar
days = np.arange(1, 31)  # Time in days from 1 to 30

# Calculating cooperation costs over time using the exponential decay function
cooperation_costs = C0 * np.exp(-k * days) + C_min

# Plotting the data
plt.figure(figsize=(12, 8))
plt.plot(days, cooperation_costs, marker="o", linestyle="-", color="darkblue")
plt.title("Cooperation Cost Over Time with Exponential Decay")
plt.xlabel("Time (Days)")
plt.ylabel("Cooperation Cost")
plt.grid(True)
plt.show()
