for i in {1..12}
do
  echo ">>> 第 $i 次執行 NSP 排班"
  python3 main.py "$i" > "logs/n021w4/scheduler_baseline1-n021w4-max_iter2e4_ComCw100_run${i}.txt"

  echo ">>> 模擬合作圖（模擬第 $i 次後的結果）"
  python3 Simulate_coop.py "$i"

done