#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jan 23 13:40:53 2023

@author: njapke
"""

import os
import json
import numpy as np
import pandas as pd

# paths
data_laaber = "/home/njapke/TU_Berlin/Doktor/Paper Projects/uoptime/replication_package_fse20_laaber/raw-data/json"

# iterate over all folders by christoph
for subdir, _, files in os.walk(data_laaber):
    # skip root dir
    if data_laaber == subdir:
        continue
    
    # get project name from subdir
    subdir_split = subdir.split("/")[-1].split("-")
    proj_name = "-".join(subdir_split[1:])
    
    df = pd.DataFrame(columns=["n","ns_per_op","it_setup","fork_setup","it_pos","fork_pos","b_name"])
    
    # iterate over all files in subdir
    for file in files:
        print("Processing " + subdir + "/" + file)
        # skip empty files and dotfiles
        if os.path.getsize(subdir + "/" + file) == 0 or file[0] == ".":
            continue
        with open(subdir + "/" + file) as f:
            j = json.load(f)
            # skip empty json
            if len(j) == 0:
                continue
            bench_name = file[:-5] # removes .json from filename
        
            # process data
            data_j = j[0]["primaryMetric"]["rawDataHistogram"]
            score_unit = j[0]["primaryMetric"]["scoreUnit"]
            unit_conv = 1
            if score_unit == "us/op":
                unit_conv = 1e3
            elif score_unit == "ms/op":
                unit_conv = 1e6
            elif score_unit == "s/op":
                unit_conv = 1e9
            it_setup = j[0]["measurementIterations"]
            fork_setup = j[0]["forks"]
            
            fork_no = 1
            for fork in data_j:
                it_no = 1
                for it in fork:
                    it_arr = np.array(it)
                    weighted_sum = (it_arr[:,0]*it_arr[:,1]).sum()
                    N = it_arr[:,1].sum()
                    m = weighted_sum / N
                    df = pd.concat([df, pd.DataFrame([[N,m*unit_conv,it_setup,fork_setup,it_no,fork_no,bench_name]], columns=df.columns)], ignore_index=True)
                    it_no = it_no + 1
                fork_no = fork_no + 1
    df.index.name = "m_id"
    df.to_csv("laaber_traini_preprocessed/laaber_" + proj_name + ".csv")
