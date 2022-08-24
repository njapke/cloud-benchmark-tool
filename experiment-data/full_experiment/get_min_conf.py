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

# Coefficient of Variation between and within instance runs
cv_ir_within = np.zeros((len(benchmarks), ir_setup))
mean_ir = np.zeros((len(benchmarks), ir_setup))
cv_ir_between = np.zeros(len(benchmarks))
for b in range(len(benchmarks)):
    bench = benchmarks[b]
    dft = df[df["b_name"] == bench]
    # ir
    for i in range(1,ir_setup+1):
        tmp = dft[(dft["ir_pos"] == i)]
        data = np.array(tmp["ns_per_op"])
        mean_ir[b,i-1] = data.mean()
        cv_ir_within[b,i-1] = np.sqrt(1/(len(data)) * ((data - mean_ir[b,i-1])**2).sum() ) / mean_ir[b,i-1]
    cv_ir_between[b] = np.sqrt(1/(len(mean_ir[b])) * ((mean_ir[b] - mean_ir[b].mean())**2).sum() ) / mean_ir[b].mean()

# Coefficient of Variation between and within suite runs
cv_sr_within = np.zeros((len(benchmarks), ir_setup, sr_setup))
mean_sr = np.zeros((len(benchmarks), ir_setup, sr_setup))
cv_sr_between = np.zeros((len(benchmarks), ir_setup))
for b in range(len(benchmarks)):
    bench = benchmarks[b]
    dft = df[df["b_name"] == bench]
    # ir
    for i in range(1,ir_setup+1):
        # sr
        for j in range(1,sr_setup+1):
            tmp = dft[(dft["ir_pos"] == i) & (dft["sr_pos"] == j)]
            data = np.array(tmp["ns_per_op"])
            mean_sr[b,i-1,j-1] = data.mean()
            cv_sr_within[b,i-1,j-1] = np.sqrt(1/(len(data)) * ((data - mean_sr[b,i-1,j-1])**2).sum() ) / mean_sr[b,i-1,j-1]
        cv_sr_between[b,i-1] = np.sqrt(1/(len(mean_sr[b,i-1])) * ((mean_sr[b,i-1] - mean_sr[b,i-1].mean())**2).sum() ) / mean_sr[b,i-1].mean()

# Coefficient of Variation between and within iterations
cv_it_within = np.zeros((len(benchmarks), ir_setup, sr_setup, it_setup))
mean_it = np.zeros((len(benchmarks), ir_setup, sr_setup, it_setup))
cv_it_between = np.zeros((len(benchmarks), ir_setup, sr_setup))
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
                mean_it[b,i-1,j-1,k-1] = data.mean()
                cv_it_within[b,i-1,j-1,k-1] = np.sqrt(1/(len(data)) * ((data - mean_it[b,i-1,j-1,k-1])**2).sum() ) / mean_it[b,i-1,j-1,k-1]
            cv_it_between[b,i-1,j-1] = np.sqrt(1/(len(mean_it[b,i-1,j-1])) * ((mean_it[b,i-1,j-1] - mean_it[b,i-1,j-1].mean())**2).sum() ) / mean_it[b,i-1,j-1].mean()


# cv of sr in within and between form, compare, see if maybe with low cv we can shave of time at that level






