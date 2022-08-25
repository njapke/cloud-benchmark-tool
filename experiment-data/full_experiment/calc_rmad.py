#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Aug 24 11:54:19 2022

@author: njapke
"""

import numpy as np
import pandas as pd

# read data
df = pd.read_csv("experiment.csv", index_col="m_id")

# get all benchmarks
benchmarks = list(set(df["b_name"]))

# get setup variables
bed_setup = df["bed_setup"][1]
it_setup = df["it_setup"][1]
sr_setup = df["sr_setup"][1]
ir_setup = df["ir_setup"][1]

# RMAD between and within instance runs
rmad_ir_within = np.zeros((len(benchmarks), ir_setup))
median_ir = np.zeros((len(benchmarks), ir_setup))
rmad_ir_between = np.zeros(len(benchmarks))
for b in range(len(benchmarks)):
    bench = benchmarks[b]
    dft = df[df["b_name"] == bench]
    # ir
    for i in range(1,ir_setup+1):
        tmp = dft[(dft["ir_pos"] == i)]
        data = np.array(tmp["ns_per_op"])
        median_ir[b,i-1] = np.median(data)
        rmad_ir_within[b,i-1] = np.median(np.absolute(data - median_ir[b,i-1])) / median_ir[b,i-1]
    rmad_ir_between[b] = np.median(np.absolute(median_ir[b] - np.median(median_ir[b]))) / np.median(median_ir[b])

# RMAD between and within suite runs
rmad_sr_within = np.zeros((len(benchmarks), ir_setup, sr_setup))
median_sr = np.zeros((len(benchmarks), ir_setup, sr_setup))
rmad_sr_between = np.zeros((len(benchmarks), ir_setup))
for b in range(len(benchmarks)):
    bench = benchmarks[b]
    dft = df[df["b_name"] == bench]
    # ir
    for i in range(1,ir_setup+1):
        # sr
        for j in range(1,sr_setup+1):
            tmp = dft[(dft["ir_pos"] == i) & (dft["sr_pos"] == j)]
            data = np.array(tmp["ns_per_op"])
            median_sr[b,i-1,j-1] = np.median(data)
            rmad_sr_within[b,i-1,j-1] = np.median(np.absolute(data - median_sr[b,i-1,j-1])) / median_sr[b,i-1,j-1]
        rmad_sr_between[b,i-1] = np.median(np.absolute(median_sr[b,i-1] - np.median(median_sr[b,i-1]))) / np.median(median_sr[b,i-1])

# RMAD between and within iterations
rmad_it_within = np.zeros((len(benchmarks), ir_setup, sr_setup, it_setup))
median_it = np.zeros((len(benchmarks), ir_setup, sr_setup, it_setup))
rmad_it_between = np.zeros((len(benchmarks), ir_setup, sr_setup))
for b in range(len(benchmarks)):
    bench = benchmarks[b]
    dft = df[df["b_name"] == bench]
    # ir
    for i in range(1,ir_setup+1):
        # sr
        for j in range(1,sr_setup+1):
            # it
            for k in range(1,it_setup+1):
                tmp = dft[(dft["ir_pos"] == i) & (dft["sr_pos"] == j) & (dft["it_pos"] == k)]
                data = np.array(tmp["ns_per_op"])
                median_it[b,i-1,j-1,k-1] = np.median(data)
                rmad_it_within[b,i-1,j-1,k-1] = np.median(np.absolute(data - median_it[b,i-1,j-1,k-1])) / median_it[b,i-1,j-1,k-1]
            rmad_it_between[b,i-1,j-1] = np.median(np.absolute(median_it[b,i-1,j-1] - np.median(median_it[b,i-1,j-1]))) / np.median(median_it[b,i-1,j-1])


# rmad of sr in within and between form, compare, see if maybe with low rmad we can shave of time at that level (<1%)
ts = 0.01 # threshold
benchmark_unstable = np.zeros((len(benchmarks), 6))
for b in range(len(benchmarks)):
    benchmark_unstable[b,0] = rmad_ir_between[b] > ts
    benchmark_unstable[b,1] = (rmad_ir_within[b] > ts).sum() > 0
    benchmark_unstable[b,2] = (rmad_sr_between[b] > ts).sum() > 0
    benchmark_unstable[b,3] = (rmad_sr_within[b] > ts).sum() > 0
    benchmark_unstable[b,4] = (rmad_it_between[b] > ts).sum() > 0
    benchmark_unstable[b,5] = (rmad_it_within[b] > ts).sum() > 0




