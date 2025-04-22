

Start schedule:
```
python3 main.py \
    --input_folder "$dataset_folder" \
    --sce "$scenario" \
    --comc "$comc_weight" \
    --run_id "$i" \
    --output_dir "$output_dir"
```

e.g., 
```
python3 main.py --input_folder ./testdatasets_json --sce n005w4 --comc 200 --run_id 0 --output_dir ./Output_test

python3 main.py --input_folder ./testdatasets_json --sce n021w4 --comc 200 --run_id 0 --output_dir ./Output
```

Calculate cooperation intensity

```
python3 Simulate_coop.py "${output_dir}/${scenario}" "$sol_dir" "${i}" --comc "$comc_weight" 
```

e.g., 
```
python3 Simulate_coop.py ./Output_test/n005w4 Output_test/n005w4/Solutions-ComC200-0 1

python3 Simulate_coop.py ./Output_test/n005w4 Output_test/n005w4/Solutions-ComC200-0 1 --comc 200

```