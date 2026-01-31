'''Create boxplot for SUS scores.'''

import matplotlib.pyplot as plt

# Data
data = [67.5, 82.5, 75, 87.5, 72.5, 80]

# Wide, short figure for one-column layout
plt.figure(figsize=(6, 4))  # width > height

plt.boxplot(
    data,
    vert=True,
    widths=0.4,
    patch_artist=True,
    showfliers=True,
    boxprops=dict(facecolor="lightgray", edgecolor="black", linewidth=1),
    medianprops=dict(color="black", linewidth=1.5),
    whiskerprops=dict(color="black", linewidth=1),
    capprops=dict(color="black", linewidth=1),
    flierprops=dict(marker="o", markersize=4,
                    markerfacecolor="white", markeredgecolor="black")
)

# Overlay raw data points
x = [1] * len(data)
plt.scatter(x, data, zorder=3, s=20)

# Axis formatting
ax = plt.gca()
ax.set_xticks([])
ax.set_xlabel("")
ax.spines["bottom"].set_visible(False)
ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)

plt.ylabel("SUS Score", fontsize=9)
plt.yticks(fontsize=8)

plt.grid(axis="y", linestyle="--", alpha=0.4)

plt.tight_layout(pad=0.3)

# Save for LaTeX
plt.savefig("sus_boxplot.pdf", bbox_inches="tight")

plt.show()
