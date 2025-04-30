import re
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.cm as cm


def parse_observation_file(filename="observations_SA_processed.txt"):
    data = []
    comc_weight = None
    week = None
    current_entry = {}

    with open(filename, "r") as f:
        lines = f.readlines()

    for line in lines:
        line = line.strip()
        if not line:
            continue
        if line.startswith("ComC weight"):
            comc_weight = int(re.search(r"\d+", line).group())
        elif line.startswith("week"):
            week = line.strip()
            current_entry = {"ComC_weight": comc_weight, "Week": week}
        elif re.match(
            r"Hard constraints|Soft constraints|ComC constraints|Total constraints",
            line,
        ):
            parts = re.split(r"\s{2,}", line)
            if len(parts) == 3:
                category, initial, best = parts
                key = category.split()[0]
                current_entry[f"Initial_{key}"] = float(initial)
                current_entry[f"Best_{key}"] = float(best)
            if category.startswith("Total constraints"):
                data.append(current_entry)

    df = pd.DataFrame(data)
    df["Label"] = df.apply(lambda row: f"{row['Week']}-W{row['ComC_weight']}", axis=1)
    return df


import numpy as np
import matplotlib.pyplot as plt


def plot_grouped_bar_chart(df, output_filename="grouped_bar_chart.png"):
    categories = ["Soft", "ComC", "Total"]
    bar_width = 0.2  # 調小以避免柱狀圖互相遮擋
    x = np.arange(len(df))

    # 顏色設定（Initial 淺色, Best 深色）
    colors = {
        "Soft": ("lightblue", "blue"),
        "ComC": ("navajowhite", "orange"),
        "Total": ("lightgreen", "green"),
    }

    fig, ax = plt.subplots(figsize=(20, 6))

    n_categories = len(categories)
    n_bars_per_group = n_categories * 2  # 每類別有 Initial 和 Best 各一個

    total_group_width = n_bars_per_group * bar_width

    for i, cat in enumerate(categories):
        print(f"Processing category: {cat}, index: {i}")

        # 計算位移，讓每組的 Initial/Best 條狀圖分開
        x_offset = i * 2 * bar_width
        x_initial = x - total_group_width / 2 + x_offset
        x_best = x_initial + bar_width

        ax.bar(
            x_initial,
            df[f"Initial_{cat}"],
            width=bar_width,
            hatch="//",
            color=colors[cat][0],
            label=f"Initial {cat}",
        )
        ax.bar(
            x_best,
            df[f"Best_{cat}"],
            width=bar_width,
            color=colors[cat][1],
            label=f"Best {cat}",
        )

    # 設定x軸
    ax.set_xticks(x)
    ax.set_xticklabels(df["Label"], rotation=90)

    ax.set_xlabel("Week - ComC Weight")
    ax.set_ylabel("Score")
    ax.set_title("Initial vs Best Scores by Constraint Category (Grouped Bar Chart)")

    # 避免legend重複
    handles, labels = ax.get_legend_handles_labels()
    by_label = dict(zip(labels, handles))
    ax.legend(
        by_label.values(), by_label.keys(), loc="upper left", bbox_to_anchor=(1, 1)
    )

    ax.grid(True, axis="y")

    plt.tight_layout()
    plt.savefig(output_filename, dpi=300, bbox_inches="tight")
    plt.show()


def plot_score_trend_line(df, output_filename="score_trend.png"):
    categories = ["Soft", "ComC", "Total"]
    colors = {"Soft": "tab:blue", "ComC": "tab:orange", "Total": "tab:green"}

    fig, ax = plt.subplots(figsize=(12, 6))
    for cat in categories:
        ax.plot(
            df["Label"],
            df[f"Initial_{cat}"],
            marker="o",
            linestyle="--",
            label=f"Initial {cat}",
            color=colors[cat],
        )
        ax.plot(
            df["Label"],
            df[f"Best_{cat}"],
            marker="x",
            linestyle="-",
            label=f"Best {cat}",
            color=colors[cat],
        )

    ax.set_xlabel("Week - ComC Weight")
    ax.set_ylabel("Score")
    ax.set_title("Score Trend Line: Initial vs Best (Line Chart)")
    ax.legend()

    # 設定 xticks 為所有 Label
    ax.set_xticks(np.arange(len(df)))
    ax.set_xticklabels(df["Label"], rotation=90)

    # y 軸格線
    ax.grid(True)
    # ax.grid(True, axis='y')

    ax.set_xlim(-0.5, len(df) - 0.5)

    plt.xticks(rotation=90)
    plt.tight_layout()
    plt.savefig(output_filename, dpi=300, bbox_inches="tight")
    plt.show()


def plot_comc_per_weight(df, output_filename="comc_per_weight.png"):
    """
    畫出 ComC constraints penalty 每單位 weight 的結果。
    """
    fig, ax = plt.subplots(figsize=(12, 6))

    # 計算每單位 weight 的 ComC 分數
    df["ComC_per_weight_Initial"] = df["Initial_ComC"] / df["ComC_weight"]
    df["ComC_per_weight_Best"] = df["Best_ComC"] / df["ComC_weight"]

    # 畫線圖
    ax.plot(
        df["Label"],
        df["ComC_per_weight_Initial"],
        marker="o",
        linestyle="--",
        label="Initial ComC per Weight",
        color="tab:purple",
    )
    ax.plot(
        df["Label"],
        df["ComC_per_weight_Best"],
        marker="x",
        linestyle="-",
        label="Best ComC per Weight",
        color="tab:pink",
    )

    ax.set_xlabel("Week - ComC Weight")
    ax.set_ylabel("ComC Constraint per Weight")
    ax.set_title("ComC Constraint per Weight (Initial vs Best)")
    ax.legend()

    # 設定 x 軸
    ax.set_xticks(np.arange(len(df)))
    ax.set_xticklabels(df["Label"], rotation=90)

    # 加上格線
    ax.grid(True)

    # 設定邊界
    ax.set_xlim(-0.5, len(df) - 0.5)

    plt.tight_layout()
    plt.savefig(output_filename, dpi=300, bbox_inches="tight")
    plt.show()


def plot_comc_per_weight_by_weight(df, output_filename="comc_per_weight_by_weight.png"):
    """
    把同一個 weight 的 Initial 和 Best 成績分組統計後，畫出每單位 weight 的合作成本。
    """
    # 先計算每一筆資料的 per weight 值
    df["ComC_per_weight_Initial"] = df["Initial_ComC"] / df["ComC_weight"]
    df["ComC_per_weight_Best"] = df["Best_ComC"] / df["ComC_weight"]

    # 選出只有數值的欄位來 groupby + mean（避免文字欄位）
    numeric_cols = df.select_dtypes(include="number").columns
    grouped = df.groupby("ComC_weight")[numeric_cols].mean()

    fig, ax = plt.subplots(figsize=(10, 6))

    # 畫線圖
    ax.plot(
        grouped.index,
        grouped["ComC_per_weight_Initial"],
        marker="o",
        linestyle="--",
        label="Initial ComC per Weight",
        color="tab:purple",
    )
    ax.plot(
        grouped.index,
        grouped["ComC_per_weight_Best"],
        marker="x",
        linestyle="-",
        label="Best ComC per Weight",
        color="tab:pink",
    )

    ax.set_xlabel("ComC Weight")
    ax.set_ylabel("ComC Constraint per Weight")
    ax.set_title("Average ComC Constraint per Weight (Grouped by ComC Weight)")
    ax.legend()

    # x 軸設成 weight的間隔
    ax.set_xticks(grouped.index)

    ax.grid(True)

    plt.tight_layout()
    plt.savefig(output_filename, dpi=300, bbox_inches="tight")
    plt.show()


def plot_total_minus_comc_penalty_by_weight(
    df, output_filename="total_minus_comc_by_weight.png"
):
    """
    畫出 Total penalty 減去 ComC penalty 的統計圖，
    每個 ComC weight 分別畫出 Initial / Best 的統計結果。
    """
    # 計算 Total - ComC
    df["Total_minus_ComC_Initial"] = df["Initial_Total"] - df["Initial_ComC"]
    df["Total_minus_ComC_Best"] = df["Best_Total"] - df["Best_ComC"]

    # 以 weight 分組取平均
    grouped = df.groupby("ComC_weight")[
        ["Total_minus_ComC_Initial", "Total_minus_ComC_Best"]
    ].mean()

    fig, ax = plt.subplots(figsize=(12, 6))

    x = np.arange(len(grouped))
    bar_width = 0.35

    # 畫柱狀圖
    ax.bar(
        x - bar_width / 2,
        grouped["Total_minus_ComC_Initial"],
        width=bar_width,
        label="Initial (Total - ComC)",
    )
    ax.bar(
        x + bar_width / 2,
        grouped["Total_minus_ComC_Best"],
        width=bar_width,
        label="Best (Total - ComC)",
    )

    ax.set_xlabel("ComC Weight")
    ax.set_ylabel("Total - ComC Penalty")
    ax.set_title("Total Penalty Minus ComC Penalty (Grouped by ComC Weight)")
    ax.set_xticks(x)
    ax.set_xticklabels(grouped.index)

    ax.legend()
    ax.grid(True, axis="y")

    plt.tight_layout()
    plt.savefig(output_filename, dpi=300, bbox_inches="tight")
    plt.show()


def main():
    filename = 'procession_with_each_weight50_1000.txt'
    filename = "observations_SA_processed.txt"
    df = parse_observation_file(filename)

    # print(df.head())
    # plot_grouped_bar_chart(df)
    # plot_score_trend_line(df)
    # plot_comc_per_weight(df)
    # plot_comc_per_weight_by_weight(df)
    plot_total_minus_comc_penalty_by_weight(df)


if __name__ == "__main__":
    main()
