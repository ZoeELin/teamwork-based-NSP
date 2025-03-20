import numpy as np
import matplotlib.pyplot as plt

# Parameters for the simulation using the inverse proportion model
a_inverse = 5  # Scale factor for the inverse proportion model
b_inverse = 1  # Adjustment factor for the proportion
c_inverse = 5  # Base time cost for the model

# Veteran proportion range from 10% to 100%
veteran_proportions = np.linspace(0.1, 1.0, 10)  # Proportions from 10% to 100%

# Calculating time costs using the inverse proportion function
time_costs_inverse = a_inverse / (b_inverse * veteran_proportions) + c_inverse

# Plotting the data
plt.figure(figsize=(10, 6))
plt.plot(
    veteran_proportions * 100,
    time_costs_inverse,
    marker="o",
    linestyle="-",
    color="blue",
)
plt.title("Time Cost vs. Veteran Proportion")
plt.xlabel("Veteran Proportion")
plt.ylabel("Time Cost")

# Setting X-axis ticks and labels
x_ticks = np.linspace(10, 100, 10)
x_labels = ["10%", "20%", "30%", "40%", "50%", "60%", "70%", "80%", "90%", "100%"]
plt.xticks(x_ticks, x_labels)

# Adding secondary X-axis labels
ax = plt.gca()  # Get current axis
ax2 = ax.twiny()  # Create a twin of the original x-axis
ax2.set_xlim(
    ax.get_xlim()
)  # Ensure the secondary x-axis has the same limits as the primary x-axis
ax2.set_xticks(x_ticks)  # Set the same x-ticks as the primary x-axis
ax2.set_xticklabels(
    ["1:9", "2:8", "3:7", "4:6", "5:5", "6:4", "7:3", "8:2", "9:1", "10:0"]
)

plt.grid(True)
plt.show()
