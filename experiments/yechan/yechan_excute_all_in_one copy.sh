
# run greybox 10 times
for i in {1..38}; do
    echo "greybox running: $i"
    echo "executing: python3 SimAPR/simapr.py -o experiments/yechan/tbar/Mockito_result/Mockito_$i-greybox-out -m greybox --instr-cp /root/project/JPatchInst -w /root/project/SimAPR/TBar/d4j/Mockito_$i -t 36000 -T 18000 --seed $i --use-simulation-mode /root/project/SimAPR/experiments/tbar/result/cache/Mockito_$i-cache.json -k template --skip-valid -- python3 /root/project/SimAPR/SimAPR/script/d4j_run_test.py /root/project/SimAPR/TBar/buggy"

    python3 SimAPR/simapr.py -o experiments/yechan/tbar/Mockito_result/Mockito_$i-greybox-$i-out -m greybox --instr-cp /root/project/JPatchInst --branch-output experiments/tbar/Mockito_result/branch/Mockito_$i -w /root/project/SimAPR/TBar/d4j/Mockito_$i -t 36000 -T 18000 --seed $i --use-simulation-mode /root/project/SimAPR/experiments/tbar/result/cache/Mockito_$i-cache.json -k template --skip-valid -- python3 /root/project/SimAPR/SimAPR/script/d4j_run_test.py /root/project/SimAPR/TBar/buggy
done
