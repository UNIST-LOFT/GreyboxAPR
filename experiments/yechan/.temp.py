import os
import json
import numpy as np

iters=[]
for i in range(10):
    with open(f'tbar/result/Chart_9-casino-{i}/simapr-result.json','r') as f:
        result=json.load(f)
        for res in result:
            if res['pass_result']:
                iters.append(res['iteration'])
                break
            
print(np.mean(iters))