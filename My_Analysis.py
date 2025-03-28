import json
from collections import Counter


def analyze_contract_distribution(data):
    """
    分析合約分佈情況
    """
    # 擷取 nurse 資訊
    nurses = data["nurses"]

    # 統計 contract 分佈
    contract_counts = Counter(nurse["contract"] for nurse in nurses)

    # 計算總人數
    total_nurses = len(nurses)

    # 顯示統計結果
    print("📊 Nurse Contract Composition:")
    for contract_type, count in contract_counts.items():
        percentage = (count / total_nurses) * 100
        print(f"{contract_type}: {count} ({percentage:.2f}%)")

    print(f"\nTotal nurses: {total_nurses}")


def analyze_contract_assignments(data):
    """
    分析每個合約的最小、平均、最大排班總數量（以班次計算，不是小時）
    傳入 JSON 資料的字典結構
    """

    nurses = data["nurses"]
    contract_counts = Counter(nurse["contract"] for nurse in nurses)
    contract_info = {c["id"]: c for c in data["contracts"]}

    print("📊 每種合約的最小、平均、最大排班數量（單位：班次）\n")

    total_min = 0
    total_avg = 0
    total_max = 0

    for contract_type, count in contract_counts.items():
        info = contract_info[contract_type]
        min_assign = info["minimumNumberOfAssignments"]
        max_assign = info["maximumNumberOfAssignments"]
        avg_assign = (min_assign + max_assign) / 2

        min_total = min_assign * count
        avg_total = avg_assign * count
        max_total = max_assign * count

        total_min += min_total
        total_avg += avg_total
        total_max += max_total

        print(f"{contract_type}:")
        print(f"  🔹 人數: {count}")
        print(f"  🔸 最小排班總數: {min_total} 班")
        print(f"  🔸 平均排班總數: {avg_total:.1f} 班")
        print(f"  🔸 最大排班總數: {max_total} 班\n")

    print("📈 全體護士總排班數（單位：班次）")
    print(f"  ✅ 最小總排班數: {total_min} 班")
    print(f"  ✅ 平均總排班數: {total_avg:.1f} 班")
    print(f"  ✅ 最大總排班數: {total_max} 班")


# Load JSON scenario data
sce_filepath = "testdatasets_json/n005w4/Sc-n005w4.json"
with open(sce_filepath, "r") as f:
    data = json.load(f)

analyze_contract_distribution(data)
analyze_contract_assignments(data)
