#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Aug 24 11:54:19 2022

@author: njapke
"""

import numpy as np
import pandas as pd
import json
import stat_functions as st

# read data
df = pd.read_csv("experiment.csv", index_col="m_id")

# get all benchmarks
benchmarks = np.array(df["b_name"].drop_duplicates())

# get setup variables
bed_setup = df["bed_setup"][1]
it_setup = df["it_setup"][1]
sr_setup = df["sr_setup"][1]
ir_setup = df["ir_setup"][1]
df.drop(columns=["bed_setup", "it_setup", "sr_setup", "ir_setup"], inplace=True)

# Select instability measure
calc_inst = st.rciw

# Select threshold to mark benchmarks as unstable
ts = 0.01

# Calculate instability
instability_overall = np.zeros(len(benchmarks))
instability_within_ir = np.zeros((len(benchmarks), ir_setup))
instability_within_sr = np.zeros((len(benchmarks), ir_setup, sr_setup))
instability_within_it = np.zeros((len(benchmarks), ir_setup, sr_setup, it_setup))
for b in range(len(benchmarks)):
    bench = benchmarks[b]
    dft = df[df["b_name"] == bench]
    # overall
    data = np.array(dft["ns_per_op"])
    instability_overall[b] = calc_inst(data)
    # ir
    for i in range(1,ir_setup+1):
        tmp = dft[(dft["ir_pos"] == i)]
        data = np.array(tmp["ns_per_op"])
        instability_within_ir[b,i-1] = calc_inst(data)
        # sr
        for j in range(1,sr_setup+1):
            tmp = dft[(dft["ir_pos"] == i) & (dft["sr_pos"] == j)]
            data = np.array(tmp["ns_per_op"])
            instability_within_sr[b,i-1,j-1] = calc_inst(data)
            # it
            for k in range(1,it_setup+1):
                tmp = dft[(dft["ir_pos"] == i) & (dft["sr_pos"] == j) & (dft["it_pos"] == k)]
                data = np.array(tmp["ns_per_op"])
                instability_within_it[b,i-1,j-1,k-1] = calc_inst(data)

# Mark unstable benchmarks
instability_matrix = np.zeros((len(benchmarks), 4))
min_config = {}
for b in range(len(benchmarks)):
    instability_matrix[b,0] = instability_overall[b] > ts
    instability_matrix[b,1] = (instability_within_ir[b] > ts).sum() / len(instability_within_ir[b].flatten())
    instability_matrix[b,2] = (instability_within_sr[b] > ts).sum() / len(instability_within_sr[b].flatten())
    instability_matrix[b,3] = (instability_within_it[b] > ts).sum() / len(instability_within_it[b].flatten())
    
    bench_ir = 3 if instability_matrix[b,0] == 1 else 2 # nicht sinnvoll
    
    bench_sr = 3
    if instability_matrix[b,1] < 0.1:
        bench_sr = 1
    elif instability_matrix[b,1] < 0.4:
        bench_sr = 2
    
    bench_it = 5
    if instability_matrix[b,2] < 0.1:
        bench_it = 3
    elif instability_matrix[b,2] < 0.3:
        bench_it = 4
    
    bench_bed = 5
    if instability_matrix[b,3] < 0.1:
        bench_bed = 1
    elif instability_matrix[b,3] < 0.2:
        bench_bed = 2
    elif instability_matrix[b,3] < 0.3:
        bench_bed = 3
    elif instability_matrix[b,3] < 0.4:
        bench_bed = 4
    
    min_config[benchmarks[b]] = (bench_ir,bench_sr,bench_it,bench_bed)

with open("min_config.json","w") as f:
    json.dump(min_config, f)

np.savez("arrays.npz",
         instability_overall=instability_overall,
         instability_within_ir=instability_within_ir,
         instability_within_sr=instability_within_sr,
         instability_within_it=instability_within_it,
         instability_matrix=instability_matrix)



