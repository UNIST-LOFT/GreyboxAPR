import argparse
import os
import sys
import shutil
import json
from typing import Any, Dict, List, Set, Tuple
import logging

import field_change

if __name__=='__main__':
    parser=argparse.ArgumentParser(description='Simulate a grey-box model')
    parser.add_argument('result_path',action='store',type=str,help='Path to the SimAPR result file')
    parser.add_argument('field_path',action='store',type=str,help='Path to the field data(cache) file')
    args=parser.parse_args(sys.argv[1:])

    # Parse field in original
    orig_field_data:Dict[str,field_change.FieldChange]=dict()
    field_data:Dict[str,Dict[str,field_change.FieldChange]]=dict() # field_data[patch][test,values]
    test_list:List[str]=list()
    for file in os.listdir(args.field_path):
        data=field_change.parse_change(logging.getLogger(),f'{args.field_path}/{file}')
        _text=file.removesuffix('.txt').split('_')
        patch=_text[0]
        test='_'.join(_text[1:])
        patch=patch.replace('#','/')
        if patch=='original':
            orig_field_data[test]=data
        else:
            if patch not in field_data:
                field_data[patch]=dict()
            field_data[patch][test]=data

        if patch=='original':
            test_list.append(test)
    
    if len(orig_field_data)==0:
        print('No original field data found, exit!')
        sys.exit(0)

    with open(f'{args.result_path}/simapr-result.json','r') as f:
        results=json.load(f)
    
    interesting_critical_field_freq:Dict[str,Dict[str,int]]=dict()
    plausible_critical_field_freq:Dict[str,Dict[str,int]]=dict()
    unplausible_critical_field_freq:Dict[str,Dict[str,int]]=dict()

    intersting_critical_field_diff:Dict[str,Dict[str,List[float]]]=dict()
    plausible_critical_field_diff:Dict[str,Dict[str,List[float]]]=dict()
    unplausible_critical_field_diff:Dict[str,Dict[str,List[float]]]=dict()
    
    total_int_patch=0
    total_plau_patch=0
    total_unplau_patch=0
    # Log the critical field info
    for result in results:
        is_plausible=result['pass_result']
        is_interesting=result['result']
        cur_patch=result['config'][0]['location']

        # Update critical field
        if is_interesting:
            for test in test_list:
                # Diff value between original and current, and update critical field
                if cur_patch not in field_data or test not in field_data[cur_patch]:
                    continue
                total_int_patch+=1
                field_difference_list: List[Tuple[str,float]] = field_data[cur_patch][test].diff(orig_field_data[test])

                # Update critical field frequency when interesting
                if test not in interesting_critical_field_freq:
                    interesting_critical_field_freq[test]=dict()
                for field,diff in field_difference_list:
                    if field not in interesting_critical_field_freq[test]:
                        interesting_critical_field_freq[test][field]=0
                    interesting_critical_field_freq[test][field]+=1

                # Update critical field diff when interesting
                if test not in intersting_critical_field_diff:
                    intersting_critical_field_diff[test]=dict()
                for field,diff in field_difference_list:
                    if field not in intersting_critical_field_diff[test]:
                        intersting_critical_field_diff[test][field]=[]
                    intersting_critical_field_diff[test][field].append(abs(diff))
        
        # Update critical field frequency when plausible
        if is_plausible:
            for test in test_list:
                print(f'Plausible {test} in {cur_patch}')
                if cur_patch not in field_data or test not in field_data[cur_patch]:
                    print(f'No field data for {cur_patch}')
                    continue
                total_plau_patch+=1
                field_difference_list: List[Tuple[str,float]] = field_data[cur_patch][test].diff(orig_field_data[test])

                # Update critical field frequency when plausible
                if test not in plausible_critical_field_freq:
                    plausible_critical_field_freq[test]=dict()
                for field,diff in field_difference_list:
                    if field not in plausible_critical_field_freq[test]:
                        plausible_critical_field_freq[test][field]=0
                    plausible_critical_field_freq[test][field]+=1

                # Update critical field diff when plausible
                if test not in plausible_critical_field_diff:
                    plausible_critical_field_diff[test]=dict()
                for field,diff in field_difference_list:
                    if field not in plausible_critical_field_diff[test]:
                        plausible_critical_field_diff[test][field]=[]
                    plausible_critical_field_diff[test][field].append(abs(diff))

        # Update critical field frequency when unplausible
        elif is_interesting:
            print(f'Unplausible {test} in {cur_patch}')
            for test in test_list:
                if cur_patch not in field_data or test not in field_data[cur_patch]:
                    print(f'No field data for {cur_patch}')
                    continue
                total_unplau_patch+=1
                field_difference_list: List[Tuple[str,float]] = field_data[cur_patch][test].diff(orig_field_data[test])

                # Update critical field frequency when plausible
                if test not in unplausible_critical_field_freq:
                    unplausible_critical_field_freq[test]=dict()
                for field,diff in field_difference_list:
                    if field not in unplausible_critical_field_freq[test]:
                        unplausible_critical_field_freq[test][field]=0
                    unplausible_critical_field_freq[test][field]+=1

                # Update critical field diff when plausible
                if test not in unplausible_critical_field_diff:
                    unplausible_critical_field_diff[test]=dict()
                for field,diff in field_difference_list:
                    if field not in unplausible_critical_field_diff[test]:
                        unplausible_critical_field_diff[test][field]=[]
                    unplausible_critical_field_diff[test][field].append(abs(diff))
    
    for test in interesting_critical_field_freq:
        for field in interesting_critical_field_freq[test]:
            interesting_critical_field_freq[test][field]/=total_int_patch
    for test in plausible_critical_field_freq:
        for field in plausible_critical_field_freq[test]:
            plausible_critical_field_freq[test][field]/=total_plau_patch
    for test in unplausible_critical_field_freq:
        for field in unplausible_critical_field_freq[test]:
            unplausible_critical_field_freq[test][field]/=total_unplau_patch
            
    with open(f'{args.result_path}/critical-field.json','w') as f:
        json.dump({
            'interesting_freq':interesting_critical_field_freq,
            'plausible_freq':plausible_critical_field_freq,
            'unplausible_freq':unplausible_critical_field_freq,
            'interesting_diff':intersting_critical_field_diff,
            'plausible_diff':plausible_critical_field_diff,
            'unplausible_diff':unplausible_critical_field_diff
        },f,indent=4)