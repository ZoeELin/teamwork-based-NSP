SCENARIO="n021w4"

for i in {1..12}
do
  echo ">>> 第 $i 次執行 NSP 排班 [$SCENARIO]"
  python3 main.py "$i" > "logs/${SCENARIO}/scheduler_baseline1-${SCENARIO}-max_iter2e4_ComCw0_run${i}.txt"

  echo ">>> 模擬合作圖（模擬第 $i 次後的結果）"
  python3 Simulate_coop.py "$i"

done