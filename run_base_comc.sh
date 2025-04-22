dataset_folder="./testdatasets_json"
scenario="n005w4"
comc_weight=200
output_dir="./Output"

mkdir -p "logs/${scenario}"


for i in {1..2}

# python3 main.py --input_folder ./testdatasets_json --sce n021w4 --comc 200 --run_id 0 --output_dir ./Output

do
  timestamp=$(date +"%Y%m%d_%H%M%S")
  echo ">>> 第 $i 次執行 NSP 排班"
  python3 main.py \
    --input_folder "$dataset_folder" \
    --sce "$scenario" \
    --comc "$comc_weight" \
    --run_id "$i" \
    --output_dir "$output_dir" > "logs/${scenario}/scheduler_ComCw${comc_weight}_run${i}_${timestamp}.txt"

  
  echo ">>> 模擬合作圖（模擬第 $i 次後的結果）"
  python3 Simulate_coop.py "${output_dir}/${scenario}" "${i}" > "logs/${scenario}/simulator-${i}th-coop.txt"

done