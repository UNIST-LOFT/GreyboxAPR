# this shellcode is to get the list of passed test in the greybox.
# the list is for the estimate the greybox time result by running them again.

import json
from sys import argv

def find_test_name(subjects:str, count:int)->list[str]:
    result = []
    for i in range(0,count):
        file_location = f"./experiments/{argv[1]}/result/{subjects}-greybox-{i}/simapr-result.json"
        print(file_location)
        with open(file_location, "r") as f:
            data = json.load(f)
            filtered_data = [item for item in data if item.get('result') == True]
            for e in filtered_data:
                patch_location = e.get("config")[0].get("location")
                if patch_location not in result:
                    result.append(patch_location)
    return result

def main(target_list:list[str]):
    result = dict()
    for target in target_list:
        try:
            result[target] = find_test_name(target, 10)
        except:
            print("error", target)
    with open("experiments/scripts/data_for_plot/passed_patch_list.json", "w") as f:
        f.write(json.dumps(result, indent=4))

CHART_SIZE=26
CLOSURE_SIZE=133
LANG_SIZE=65
MATH_SIZE=106
MOCKITO_SIZE=38
TIME_SIZE=27

CHART_LIST=[f'Chart_{i}' for i in range(1,CHART_SIZE+1)]
CLOSURE_LIST=[f'Closure_{i}' for i in range(1,CLOSURE_SIZE+1)]
LANG_LIST=[f'Lang_{i}' for i in range(1,LANG_SIZE+1)]
MATH_LIST=[f'Math_{i}' for i in range(1,MATH_SIZE+1)]
MOCKITO_LIST=[f'Mockito_{i}' for i in range(1,MOCKITO_SIZE+1)]
TIME_LIST=[f'Time_{i}' for i in range(1,TIME_SIZE+1)]

target_list = CHART_LIST + CLOSURE_LIST + LANG_LIST + MATH_LIST + TIME_LIST

if __name__ == "__main__":
    main(target_list)