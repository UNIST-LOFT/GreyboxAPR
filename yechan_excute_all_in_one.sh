# 배열 선언
my_array=("Chart_1" "Chart_15" "Closure_115" "Closure_129" "Math_49" "Lang_53" "Mockito_38" "Time_11")

cd /root/project/SimAPR

for element in "${my_array[@]}"; do
    #run original once
    echo "executing: python3 SimAPR/simapr.py -o experiments/yechan/tbar/result/$element-out -m orig --instr-cp /root/project/JPatchInst -w /root/project/SimAPR/TBar/d4j/$element -t 360000 -T 180000 --seed 1 --use-simulation-mode /root/project/SimAPR/experiments/tbar/result/cache/$element.json -k template --skip-valid -- python3 /root/project/SimAPR/SimAPR/script/d4j_run_test.py /root/project/SimAPR/TBar/buggy"
    python3 SimAPR/simapr.py -o experiments/yechan/tbar/result/$element-out -m orig --instr-cp /root/project/JPatchInst -w /root/project/SimAPR/TBar/d4j/$element -t 360000 -T 180000 --seed 1 --use-simulation-mode /root/project/SimAPR/experiments/tbar/result/cache/$element.json -k template --skip-valid -- python3 /root/project/SimAPR/SimAPR/script/d4j_run_test.py /root/project/SimAPR/TBar/buggy
    
    # run casino 10 times
    for i in {1..10}; do
        echo "casino running: $i"
        echo "executing: python3 SimAPR/simapr.py -o experiments/yechan/tbar/result/$element-out -m casino --instr-cp /root/project/JPatchInst -w /root/project/SimAPR/TBar/d4j/$element -t 360000 -T 180000 --seed 1 --use-simulation-mode /root/project/SimAPR/experiments/tbar/result/cache/$element.json -k template --skip-valid -- python3 /root/project/SimAPR/SimAPR/script/d4j_run_test.py /root/project/SimAPR/TBar/buggy"

        python3 SimAPR/simapr.py -o experiments/yechan/tbar/result/$element-out -m casino --instr-cp /root/project/JPatchInst -w /root/project/SimAPR/TBar/d4j/$element -t 360000 -T 180000 --seed $i --use-simulation-mode /root/project/SimAPR/experiments/tbar/result/cache/$element.json -k template --skip-valid -- python3 /root/project/SimAPR/SimAPR/script/d4j_run_test.py /root/project/SimAPR/TBar/buggy
    done

    # run greybox 10 times
    for i in {1..10}; do
        echo "greybox running: $i"
        echo "executing: python3 SimAPR/simapr.py -o experiments/yechan/tbar/result/$element-out -m greybox --instr-cp /root/project/JPatchInst -w /root/project/SimAPR/TBar/d4j/$element -t 360000 -T 180000 --seed $i --use-simulation-mode /root/project/SimAPR/experiments/tbar/result/cache/$element.json -k template --skip-valid -- python3 /root/project/SimAPR/SimAPR/script/d4j_run_test.py /root/project/SimAPR/TBar/buggy"

        python3 SimAPR/simapr.py -o experiments/yechan/tbar/result/$element-out -m greybox --instr-cp /root/project/JPatchInst -w /root/project/SimAPR/TBar/d4j/$element -t 360000 -T 180000 --seed $i --use-simulation-mode /root/project/SimAPR/experiments/tbar/result/cache/$element.json -k template --skip-valid -- python3 /root/project/SimAPR/SimAPR/script/d4j_run_test.py /root/project/SimAPR/TBar/buggy
    done
done