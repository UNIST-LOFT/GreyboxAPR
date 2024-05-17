import json
import os
from sys import argv

def remove_branch_time(file):
    print(file)
    with open(file) as f:
        data = json.load(f)
    for patch_id in data:
        if 'fail_time_branch' in data[patch_id]:
            del data[patch_id]['fail_time_branch']

    with open(file, 'w') as f:
        json.dump(data, f, indent=2)
    
tool=argv[1]
for proj in os.listdir(f'{tool}/result/cache'):
    if proj.endswith('.json'):
        remove_branch_time(f'{tool}/result/cache/{proj}')