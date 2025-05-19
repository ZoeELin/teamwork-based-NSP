import re
import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import OneHotEncoder
from sklearn.model_selection import train_test_split
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline


log_filepath = "logs-datasets0515_0-250/n030w4/scheduler_ComCw100_run12_20250515_135618.txt"
with open(log_filepath, "r") as f:
    log_text = f.read()

# print(log_text)
# --- Step 1: 解析 log ---
lines = log_text.strip().split('\n')
print(len(lines))
data = []
i = 0

while i < len(lines):
    print(f"Processing line {i}: {lines[i]}")
    if lines[i].startswith("Finish multi"):
        move_line = lines[i]
        penalty_line = lines[i+1] if i+1 < len(lines) else ""
        i += 3  # Skip to next block

        move_type = "swap" if "swap" in move_line else "change"
        nurse_types = re.findall(r'([A-Z]{2})_\d+', move_line)

        days_match = re.search(r'for (\d+) days from (\w+)', move_line)
        if not days_match:
            continue
        duration = int(days_match.group(1))
        start_day = days_match.group(2)

        penalty_match = re.search(r'penalties (\d+) -- .*?S1: (\d+), S2\+S3\+S5: (\d+), S4: (\d+), ComC: ([\d\.]+)', penalty_line)
        if penalty_match:
            penalty_total = int(penalty_match.group(1))
            s1 = int(penalty_match.group(2))
            s235 = int(penalty_match.group(3))
            s4 = int(penalty_match.group(4))
            comc = float(penalty_match.group(5))

            data.append({
                "Move_Type": move_type,
                "Nurse1_Type": nurse_types[0] if len(nurse_types) > 0 else None,
                "Nurse2_Type": nurse_types[1] if len(nurse_types) > 1 else None,
                "Duration": duration,
                "Start_Day": start_day,
                "Penalty_Total": penalty_total,
                "Penalty_S1": s1,
                "Penalty_S235": s235,
                "Penalty_S4": s4,
                "Penalty_ComC": comc
            })
            print("Match successfully!")
        else:
            print(f"No penalty match for line: {penalty_line}")
    else:
        i += 1

# --- Step 2: 建 DataFrame ---
df = pd.DataFrame(data)
print(df)

# --- Step 3: 建回歸模型 ---
cols_to_drop = [col for col in ["Penalty_ComC", "Penalty_Total"] if col in df.columns]
X = df.drop(columns=cols_to_drop)
y = df["Penalty_ComC"]

# 分類欄位與數值欄位
categorical_features = ["Move_Type", "Nurse1_Type", "Nurse2_Type", "Start_Day"]
numeric_features = ["Duration", "Penalty_S1", "Penalty_S235", "Penalty_S4"]

# 建立轉換流程
preprocessor = ColumnTransformer([
    ("cat", OneHotEncoder(), categorical_features)
], remainder='passthrough')

# 建 pipeline 模型
model = Pipeline([
    ("preprocess", preprocessor),
    ("regressor", LinearRegression())
])

model.fit(X, y)

# --- Step 4: 輸出回歸係數 ---
feature_names = model.named_steps["preprocess"].get_feature_names_out()
coefficients = model.named_steps["regressor"].coef_

# 包成 DataFrame
regression_df = pd.DataFrame({
    "Feature": feature_names,
    "Coefficient": coefficients
}).sort_values(by="Coefficient", key=abs, ascending=False)

print("\n📊 回歸係數（影響 ComC Penalty 的特徵）")
print(regression_df)
