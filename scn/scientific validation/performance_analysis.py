'''Compute performance metrics and generate plots for grip strength device data.'''

# imports
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

# path to excel data file 
SCRIPT_DIR = Path(__file__).resolve().parent
EXCEL_PATH = SCRIPT_DIR / "data/Grip_Strength_TestData.xlsx"

# output directory for figures
OUTPUT_DIR = SCRIPT_DIR / "figures"
OUTPUT_DIR.mkdir(exist_ok=True)

####INITIAL HELPERS AND CALCULATIONS####
# German excel uses decimal commas instead of points
def to_float_decimal_comma(x):
    """Convert numbers like '5,70' to float 5.70. Returns NaN if not parseable."""
    if x is None or (isinstance(x, float) and np.isnan(x)):
        return np.nan
    s = str(x).strip()
    if not s:
        return np.nan
    # Replace decimal comma with dot, remove spaces
    s = s.replace(" ", "").replace(",", ".")
    # return float
    return float(s)

def norm_correct(x):
    """Normalize Correct column to True/False/NaN."""
    if pd.isna(x):
        return np.nan
    s = str(x).strip().upper()
    if s == "Y":
        return True
    if s == "N":
        return False
    return np.nan

def norm_label_above_below(x, treat_max_as_above=True):
    """Normalize label column to 'Above'/'Below', map 'Max' -> 'Above')."""
    if pd.isna(x):
        return np.nan
    s = str(x).strip().lower()

    if treat_max_as_above and s == "max":
        return "Above"

    if s == "above":
        return "Above"
    if s == "below":
        return "Below"

    # else
    return np.nan

# Confusion matrix counts
def confusion_counts(y_true: pd.Series, y_pred: pd.Series, positive="Below"):
    """
    Define 'positive' as the clinically critical class (often 'Below threshold').
    Returns TP, FP, TN, FN with respect to chosen positive label.
    """
    yt = y_true.values
    yp = y_pred.values

    tp = np.sum((yt == positive) & (yp == positive)) # True Positives = true below, predicted below
    fp = np.sum((yt != positive) & (yp == positive)) # False Positives = true above, predicted below
    tn = np.sum((yt != positive) & (yp != positive)) # True Negatives = true above, predicted above
    fn = np.sum((yt == positive) & (yp != positive)) # False Negatives = true below, predicted above
    return int(tp), int(fp), int(tn), int(fn)

# Safe division to handle zero denominators
def safe_div(a, b):
    return float(a) / float(b) if b else np.nan

# compute all the important performance metrices
def compute_metrics(y_true: pd.Series, y_pred: pd.Series, positive="Below") -> dict:
    tp, fp, tn, fn = confusion_counts(y_true, y_pred, positive=positive)

    acc = safe_div(tp + tn, tp + tn + fp + fn) # accuracy: how often is device overall correct?
    sens = safe_div(tp, tp + fn) # sensitivity : When grip strength is truly below the threshold, how often does the device detect it? --> most important metric for JtG because we do not want to miss weak grips
    spec = safe_div(tn, tn + fp) # specificity: When grip strength is truly above the threshold, how often does the device say so?
    bal_acc = np.nanmean([sens, spec]) # balanced accuracy: average of sensitivity and specificity

    # Cohen's kappa: How much better is the device than random guessing?
    n = tp + tn + fp + fn
    if n:
        p0 = (tp + tn) / n # observed agreement between gold standard and device 
        # expected agreement
        p_true_pos = (tp + fn) / n
        p_true_neg = (tn + fp) / n
        p_pred_pos = (tp + fp) / n
        p_pred_neg = (tn + fn) / n
        pe = p_true_pos * p_pred_pos + p_true_neg * p_pred_neg # expected agreement by chance
        kappa = safe_div(p0 - pe, 1 - pe) if (1 - pe) else np.nan
    else:
        kappa = np.nan

    return {
        "N": n,
        "TP": tp, "FP": fp, "TN": tn, "FN": fn,
        "Accuracy": acc,
        "Sensitivity_(pos={})".format(positive): sens,
        "Specificity": spec,
        "Balanced_Accuracy": bal_acc,
        "Cohens_Kappa": kappa
    }

####ACTUAL ANALYSIS####
# Load Excel (single sheet) and identify columns
xlsx_path = Path(EXCEL_PATH)
if not xlsx_path.exists():
    raise FileNotFoundError(f"Excel file not found: {xlsx_path}")

df = pd.read_excel(xlsx_path)

#Identify columns 
col_force = "Dynamometer Peak Force (kg)"
col_gt = "Ground Truth (Above/Below)"
col_dev = "Device Output (Above/Below)"
col_correct = "Correct? (Y/N)"
col_hand = "Hand (D/ND)"
col_pid = "Participant ID"

# Clean data
df = df.dropna(how="all").copy() # drop completely empty rows
df["Dynamometer_kg"] = df[col_force].apply(to_float_decimal_comma)
df["Correct_trusted"] = df[col_correct].apply(norm_correct)
df["GT"] = df[col_gt].apply(lambda x: norm_label_above_below(x, treat_max_as_above=True)) # max is above
df["DEV"] = df[col_dev].apply(lambda x: norm_label_above_below(x, treat_max_as_above=True))

# Accuracy from Correct? column
valid_correct = df["Correct_trusted"].notna()
n = int(valid_correct.sum()) # number of total trials used for accuracy computation
accuracy = df.loc[valid_correct, "Correct_trusted"].mean()  # True=1, False=0
print(f"\nAccuracy from Correct? column: {accuracy:.3f} (N={n})")

# compute metrics 
positive = "Below"  # clinically relevant class
metrics = compute_metrics(df["GT"], df["DEV"], positive=positive)

print("\nPerformance Metrics:")
for k, v in metrics.items():
    if isinstance(v, float):
        print(f"{k:>28}: {v:.3f}")
    else:
        print(f"{k:>28}: {v}")


### PLOTS ###
# -------------------------------------------------------------------------------------
# 1.Confusion matrix plot
tp, fp, tn, fn = metrics["TP"], metrics["FP"], metrics["TN"], metrics["FN"]
cm = np.array([[tp, fn], [fp, tn]], dtype=int)
fig, ax = plt.subplots(figsize=(5, 4))
# Custom colors
green = np.array([0.80, 0.93, 0.80, 1.0])  # light green for correct
red = np.array([0.98, 0.80, 0.80, 1.0])  # light red for incorrect
colors = np.array([[green, red],
                   [red,   green]], dtype=float)
ax.imshow(colors)
# Labels
ax.set_xticks([0, 1], labels=["Pred Below", "Pred Above"])
ax.set_yticks([0, 1], labels=["True Below", "True Above"])
ax.set_title("Confusion Matrix")
# counts + cell type labels
cell_labels = np.array([["TP", "FN"],
                        ["FP", "TN"]])
for (i, j), v in np.ndenumerate(cm):
    ax.text(j, i, f"{cell_labels[i, j]}\n{v}", ha="center", va="center", fontsize=12)
# grid lines for clarity
ax.set_xticks(np.arange(-.5, 2, 1), minor=True)
ax.set_yticks(np.arange(-.5, 2, 1), minor=True)
ax.grid(which="minor", linewidth=1)
ax.tick_params(which="minor", bottom=False, left=False)
plt.tight_layout()
plt.show()
fig.savefig(OUTPUT_DIR / "confusion_matrix.png", dpi=300, bbox_inches="tight")
# -------------------------------------------------------------------------------------

# -------------------------------------------------------------------------------------
# 2. Histogram of dynamometer peak forces (1kg bins) and their correctness rates
plot_df = df[np.isfinite(df["Dynamometer_kg"]) & df["Correct_trusted"].notna()].copy()
correct_series = plot_df["Correct_trusted"].astype(bool)

# Define 1 kg bin edges (inclusive lower, exclusive upper)
min_f = np.floor(plot_df["Dynamometer_kg"].min())
max_f = np.ceil(plot_df["Dynamometer_kg"].max())

# Make sure bins include the clinical threshold (9 kg) and extend at least one bin beyond it
CLINICAL_THRESHOLD_KG = 9
min_f = min(min_f, CLINICAL_THRESHOLD_KG)
max_f = max(max_f, CLINICAL_THRESHOLD_KG + 1)

bin_edges = np.arange(min_f, max_f + 1, 1)  # 1kg bins

# Assign each trial to a bin
plot_df["bin"] = pd.cut(plot_df["Dynamometer_kg"], bins=bin_edges, right=False, include_lowest=True)

# Aggregate per bin: count + correctness rate
summary = (
    plot_df.groupby("bin")
    .agg(
        n_trials=("Dynamometer_kg", "size"),
        pct_correct=("Correct_trusted", "mean")
    )
    .reset_index()
)
# Drop empty bins to save space
summary = summary[summary["n_trials"] > 0].copy()

# Create x positions and bar labels (bin ranges)
bin_left = summary["bin"].apply(lambda x: x.left).astype(int)
bin_right = summary["bin"].apply(lambda x: x.right).astype(int)
x_labels = [f"{l}–{r}" for l, r in zip(bin_left, bin_right)]
x = np.arange(len(summary))

# Color bars by correctness: red (0%) -> green (100%)
cmap = plt.cm.RdYlGn # (matplotlib colormap 'RdYlGn' goes red->yellow->green)
colors = cmap(summary["pct_correct"].fillna(0).values)

fig, ax = plt.subplots(figsize=(12, 5))
bars = ax.bar(x, summary["n_trials"].values, color=colors, edgecolor="black", linewidth=0.8)

# Add percentage text on top of each bar
for i, (bar, pct) in enumerate(zip(bars, summary["pct_correct"].values)):
    ax.text(
        bar.get_x() + bar.get_width() / 2,
        bar.get_height() + 0.1,
        f"{pct*100:.0f}%",
        ha="center",
        va="bottom",
        fontsize=10
    )
ax.set_xticks(x)
ax.set_xticklabels(x_labels, rotation=45, ha="right")
ax.set_xlabel("Dynamometer peak force bin (kg), 1 kg width")
ax.set_ylabel("Number of trials")
ax.set_title("Force distribution (ground truth) with % correct per 1 kg bin")

# Add a colorbar legend for % correct
sm = plt.cm.ScalarMappable(cmap=cmap, norm=plt.Normalize(vmin=0, vmax=1))
sm.set_array([])
cbar = plt.colorbar(sm, ax=ax)
cbar.set_label("Proportion correct")

# Add vertical dashed line at clinical threshold (9 kg)
# Because x-axis is bin indices, convert threshold value to index: threshold boundary is at the start of the 9–10 bin.
threshold_idx = int(CLINICAL_THRESHOLD_KG - min_f)  # position of bin with left edge 9
ax.axvline(
    x=threshold_idx - 0.5, # boundary between 8–9 and 9–10
    ymin=0, ymax=1,
    color="black",
    linestyle="--",
    linewidth=2,
    zorder=10
)
# Label the clinical threshold line
ax.text(
    threshold_idx - 0.5 + 0.1, # slightly to the right of the line
    ax.get_ylim()[1] * 0.95, # near top of the plot
    "Clinical threshold (9 kg)",
    rotation=90,
    va="top",
    ha="left",
    fontsize=10,
    bbox=dict(
        facecolor="white",
        edgecolor="none",
        alpha=0.8,
        pad=2
    ),
    zorder=11
)

plt.tight_layout()
plt.show()
fig.savefig(OUTPUT_DIR / "force_distribution_with_correctness.png", dpi=300, bbox_inches="tight")
# -------------------------------------------------------------------------------------

# -------------------------------------------------------------------------------------
# 3. Box plots of device accuracy; individual dots denote individual participants 
acc_by_pid = (
    df.loc[valid_correct]
      .groupby(col_pid)["Correct_trusted"]
      .mean()
      .dropna()
)

vals = acc_by_pid.values.astype(float)
pids = acc_by_pid.index.astype(str).tolist()

fig, ax = plt.subplots(figsize=(6.5, 5))
# Box plot
ax.boxplot(
    vals,
    widths=0.35,
    patch_artist=True,
    boxprops=dict(facecolor="#dddddd", edgecolor="black"),
    medianprops=dict(color="black", linewidth=2),
    whiskerprops=dict(color="black"),
    capprops=dict(color="black"),
)

# Beeswarm-style horizontal spreading for identical/near-identical values (grouped by rounded accuracy)
decimals = 3
rounded = np.round(vals, decimals=decimals)
# For each group, assign symmetric x offsets: 0, +d, -d, +2d, -2d, ...
base_x = 1.0
spread = 0.06  # horizontal spacing between stacked points
x_positions = np.full_like(vals, fill_value=base_x, dtype=float)

for r in np.unique(rounded):
    idx = np.where(rounded == r)[0]
    k = len(idx)
    if k == 1:
        x_positions[idx[0]] = base_x
        continue
    offsets = []
    # sequence: 0, +1, -1, +2, -2, ...
    for i in range(k):
        if i == 0:
            offsets.append(0)
        else:
            j = (i + 1) // 2
            offsets.append(j if i % 2 == 1 else -j)
    offsets = np.array(offsets, dtype=float) * spread
    # keep deterministic order
    idx_sorted = idx[np.argsort([pids[ii] for ii in idx])]
    x_positions[idx_sorted] = base_x + offsets[:k]

# Scatter points
ax.scatter(
    x_positions, vals,
    s=70,
    color="#1f77b4",
    edgecolor="black",
    zorder=3
)

# Label each dot with its accuracy
for x, y in zip(x_positions, vals):
    ax.text(
        x + 0.015, y,
        f"{y:.3f}",
        fontsize=7,
        va="center",
        ha="left",
        alpha=0.85
    )

# Mean accuracy line + label
mean_acc = float(np.mean(vals))
ax.axhline(mean_acc, color="black", linestyle="--", linewidth=1)
ax.text(
    1.22, mean_acc,
    f"Mean = {mean_acc:.3f}",
    va="center",
    ha="left",
    fontsize=10,
    bbox=dict(facecolor="white", edgecolor="none", alpha=0.7, pad=1.5)
)

# Axes
ax.set_xticks([1])
ax.set_xticklabels(["Participants"])
ax.set_ylabel("Accuracy")
ax.set_ylim(0.6, 1.0)
ax.set_xlim(0.75, 1.35)
ax.set_title("Distribution of device accuracy across participants")
ax.grid(axis="y", linestyle="--", alpha=0.35)

plt.tight_layout()
plt.show()
fig.savefig(OUTPUT_DIR / "accuracy_by_participant_boxplot.png", dpi=300, bbox_inches="tight")
# -------------------------------------------------------------------------------------

# -------------------------------------------------------------------------------------
# 4. Box plots of accuracy by hand (D vs ND), with paired lines per participant
acc_by_pid_hand = (
    df.loc[valid_correct]
      .groupby([col_pid, col_hand])["Correct_trusted"]
      .mean()
      .reset_index()
)

# Pivot: rows=participant, cols=hand
wide = acc_by_pid_hand.pivot(index=col_pid, columns=col_hand, values="Correct_trusted")

# Keep consistent order and drop participants missing a hand (if any)
hand_order = [h for h in ["D", "ND"] if h in wide.columns]
wide = wide[hand_order].dropna().sort_index()

# Data for boxplots
data = [wide[h].values for h in hand_order]
xpos = np.arange(1, len(hand_order) + 1)

fig, ax = plt.subplots(figsize=(8, 5))

# Box plots
ax.boxplot(
    data,
    positions=xpos,
    widths=0.5,
    patch_artist=True,
    boxprops=dict(facecolor="#dddddd", edgecolor="black"),
    medianprops=dict(color="black", linewidth=2),
    whiskerprops=dict(color="black"),
    capprops=dict(color="black"),
)

# Beeswarm-style x positions per hand to avoid overlapping identical values
def beeswarm_x_positions(y_values, x_center, spread=0.06, decimals=3):
    """
    For a set of y-values at a given x-center, return x positions that spread out
    identical/near-identical y-values horizontally.
    """
    y_values = np.asarray(y_values, dtype=float)
    rounded = np.round(y_values, decimals=decimals)
    x_positions = np.full_like(y_values, fill_value=x_center, dtype=float)

    for r in np.unique(rounded):
        idx = np.where(rounded == r)[0]
        k = len(idx)
        if k == 1:
            x_positions[idx[0]] = x_center
            continue

        # symmetric offsets: 0, +1, -1, +2, -2, ...
        offsets = []
        for i in range(k):
            if i == 0:
                offsets.append(0)
            else:
                j = (i + 1) // 2
                offsets.append(j if i % 2 == 1 else -j)
        offsets = np.array(offsets, dtype=float) * spread

        # deterministic order so it doesn't jump between runs
        idx_sorted = idx[np.argsort(idx)]
        x_positions[idx_sorted] = x_center + offsets[:k]

    return x_positions

# Compute x positions for each participant per hand (so dots can spread)
x_pos_by_hand = {}
for j, hand in enumerate(hand_order):
    x_center = xpos[j]
    x_pos_by_hand[hand] = beeswarm_x_positions(
        wide[hand].values,
        x_center=x_center,
        spread=0.07,    
        decimals=3    
    )

# Participant lines: different color per participant + legend
participants = wide.index.tolist()
cmap = plt.cm.get_cmap("tab10", len(participants))  # distinct colors

line_handles = []
for i, pid in enumerate(participants):
    color = cmap(i)
    yvals = wide.loc[pid, hand_order].values

    # x positions for this participant (may be shifted by beeswarm)
    xvals = [x_pos_by_hand[hand][i] for hand in hand_order]

    h, = ax.plot(
        xvals, yvals,
        marker="o",
        linewidth=2,
        markersize=7,
        color=color,
        alpha=0.9,
        label=f"P{int(pid)}"
    )
    line_handles.append(h)

# Mean markers + mean labels for each hand
means = [float(np.mean(wide[h].values)) for h in hand_order]
ax.scatter(xpos, means, marker="D", s=90, color="black", zorder=5, label="Mean")

for x, m, hand in zip(xpos, means, hand_order):
    ax.text(
        x + 0.12, m,
        f"{hand} mean = {m:.3f}",
        va="center",
        ha="left",
        fontsize=10,
        bbox=dict(facecolor="white", edgecolor="none", alpha=0.7, pad=1.5)
    )

# Axes / styling
ax.set_xticks(xpos)
ax.set_xticklabels(hand_order)
ax.set_xlabel("Hand")
ax.set_ylabel("Accuracy")
ax.set_ylim(0.6, 1.0)
ax.set_title("Device accuracy by hand (paired within participants)")
ax.grid(axis="y", linestyle="--", alpha=0.35)

# Legend: participant colors + mean marker
ax.legend(loc="center left", bbox_to_anchor=(1.02, 0.5), frameon=True, title="Participants")

plt.tight_layout()
plt.show()
fig.savefig(OUTPUT_DIR / "accuracy_by_hand_paired.png", dpi=300, bbox_inches="tight")
# -------------------------------------------------------------------------------------