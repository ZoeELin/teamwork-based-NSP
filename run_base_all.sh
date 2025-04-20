SCENARIOS=("n021w4" "n014w3" "n028w2")  # << 這裡自己加你想跑的 scenario 名稱

for SCENARIO in "${SCENARIOS[@]}"
do
  echo "=== 開始處理 Scenario: $SCENARIO ==="

  # 確保 logs 目錄存在
  mkdir -p "logs/${SCENARIO}"

  for i in {1..12}
  do
    echo ">>> 第 $i 次執行 NSP 排班 [$SCENARIO]"
    python3 main.py "$i" > "logs/${SCENARIO}/scheduler_baseline1-${SCENARIO}-max_iter2e4_ComCw100_run${i}.txt"

    echo ">>> 模擬合作圖（模擬第 $i 次後的結果）"
    python3 Simulate_coop.py "$i" --comc > "logs/${SCENARIO}/simulator-max_iter2e4_${i}th-coop.txt"
  done

  echo "=== 完成 Scenario: $SCENARIO ==="
  echo
done