# 배열 선언
my_array=("Closure_129" "Math_49" "Lang_53" "Mockito_38" "Time_11")

cd /root/project/SimAPR

for element in "${my_array[@]}"; do

    # run greybox 10 times
    for i in {1..10}; do
        echo "greybox running: $i"
        echo "executing: python3 SimAPR/simapr.py -o experiments/yechan/tbar/result/$element-greybox-$i-out -m greybox --instr-cp /root/project/JPatchInst -w /root/project/SimAPR/TBar/d4j/$element -t 36000 -T 18000 --seed $i --use-simulation-mode /root/project/SimAPR/experiments/tbar/result/cache/$element-cache.json -k template --skip-valid -- python3 /root/project/SimAPR/SimAPR/script/d4j_run_test.py /root/project/SimAPR/TBar/buggy"

        python3 SimAPR/simapr.py -o experiments/yechan/tbar/result/$element--greybox-$i-out -m greybox --instr-cp /root/project/JPatchInst --branch-output experiments/tbar/result/branch/$element -w /root/project/SimAPR/TBar/d4j/$element -t 36000 -T 18000 --seed $i --use-simulation-mode /root/project/SimAPR/experiments/tbar/result/cache/$element-cache.json -k template --skip-valid -- python3 /root/project/SimAPR/SimAPR/script/d4j_run_test.py /root/project/SimAPR/TBar/buggy
    done

    # run casino 10 times
    for i in {1..10}; do
        echo "casino running: $i"
        echo "executing: python3 SimAPR/simapr.py -o experiments/yechan/tbar/result/$element-casino-$i-out -m casino -w /root/project/SimAPR/TBar/d4j/$element -t 36000 -T 18000 --seed $i --use-simulation-mode /root/project/SimAPR/experiments/tbar/result/cache/$element-cache.json -k template --skip-valid -- python3 /root/project/SimAPR/SimAPR/script/d4j_run_test.py /root/project/SimAPR/TBar/buggy"

        python3 SimAPR/simapr.py -o experiments/yechan/tbar/result/$element--casino-$i-out -m casino -w /root/project/SimAPR/TBar/d4j/$element -t 36000 -T 18000 --seed $i --use-simulation-mode /root/project/SimAPR/experiments/tbar/result/cache/$element-cache.json -k template --skip-valid -- python3 /root/project/SimAPR/SimAPR/script/d4j_run_test.py /root/project/SimAPR/TBar/buggy
    done

    #run original once
    echo "executing: python3 SimAPR/simapr.py -o experiments/yechan/tbar/result/$element-orig-out -m orig -w /root/project/SimAPR/TBar/d4j/$element -t 36000 -T 18000 --seed 1 --use-simulation-mode /root/project/SimAPR/experiments/tbar/result/cache/$element-cache.json -k template --skip-valid -- python3 /root/project/SimAPR/SimAPR/script/d4j_run_test.py /root/project/SimAPR/TBar/buggy"
    python3 SimAPR/simapr.py -o experiments/yechan/tbar/result/$element--orig-out -m orig -w /root/project/SimAPR/TBar/d4j/$element -t 36000 -T 18000 --seed 1 --use-simulation-mode /root/project/SimAPR/experiments/tbar/result/cache/$element-cache.json -k template --skip-valid -- python3 /root/project/SimAPR/SimAPR/script/d4j_run_test.py /root/project/SimAPR/TBar/buggy
done
