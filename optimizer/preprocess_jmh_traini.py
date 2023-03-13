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
data_traini = "/home/njapke/TU_Berlin/Doktor/Paper Projects/uoptime/SEALABQualityGroup-steady-state-traini/raw-data/data/jmh"
# data_traini = "/home/njapke/TU_Berlin/Doktor/Paper Projects/uoptime/SEALABQualityGroup-steady-state-traini/raw-data/data/tmp"

# get sorted list of all files
files = list(os.walk(data_traini))[0][2]
files.sort()
    
# init
proj_name = files[0].split("#")[0] # get project of first file
print("New project: " + proj_name)
df = pd.DataFrame(columns=["n","ns_per_op","it_setup","fork_setup","it_pos","fork_pos","b_name"])

# iterate over all files in subdir
for file in files:
    # get project name
    proj_of_mb = file.split("#")[0]
    if proj_of_mb != proj_name:
        print("New project: " + proj_of_mb)
        # save data
        df.index.name = "m_id"
        df.to_csv("traini_preprocessed/traini_" + proj_name + ".csv")
        # init new project
        proj_name = proj_of_mb
        df = pd.DataFrame(columns=["n","ns_per_op","it_setup","fork_setup","it_pos","fork_pos","b_name"])
    
    print("Processing " + data_traini + "/" + file)
    # skip empty files and dotfiles
    if os.path.getsize(data_traini + "/" + file) == 0 or file[0] == ".":
        continue
    with open(data_traini + "/" + file) as f:
        try:
            j = json.load(f)
        except json.JSONDecodeError:
            print("Skipping: Encountered JSONDecodeError")
            continue
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
# save data from last iteration
df.index.name = "m_id"
df.to_csv("traini_preprocessed/traini_" + proj_name + ".csv")

# f = open("results-zipkin/zipkin#zipkin2.codec.ProtoCodecBenchmarks.bytebuffer_protobufDecoder#.json")
# j = json.load(f)