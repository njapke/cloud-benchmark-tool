#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Aug 23 13:08:53 2022

@author: njapke
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# read data
df = pd.read_csv("experiment.csv", index_col="m_id")

# get all benchmarks
benchmarks = list(set(df["b_name"]))

# get setup variables
bed_setup = df["bed_setup"][1]
it_setup = df["it_setup"][1]
sr_setup = df["sr_setup"][1]
ir_setup = df["ir_setup"][1]

std_ir_within = np.zeros((len(benchmarks), ir_setup))
mean_ir = np.zeros((len(benchmarks), ir_setup))
std_ir_between = np.zeros(len(benchmarks))
for b in range(len(benchmarks)):
    bench = benchmarks[b]
    dft = df[df["b_name"] == bench]
    # ir
    for i in range(1,ir_setup+1):
        tmp = dft[(dft["ir_pos"] == i)]
        data = np.array(tmp["ns_per_op"])
        mean_ir[b,i-1] = data.mean()
        std_ir_within[b,i-1] = np.sqrt(1/(len(data)-1) * ((data - mean_ir[b,i-1])**2).sum() ) / mean_ir[b,i-1]
    std_ir_between[b] = np.sqrt(1/(len(mean_ir[b])-1) * ((mean_ir[b] - mean_ir[b].mean())**2).sum() )

fig = plt.figure(figsize=(14,4))
ax = plt.axes()
ax.set_xticks(range(len(benchmarks)), benchmarks, rotation="vertical")
#ax.bar(range(len(benchmarks)), std_ir_between, width=0.1)
for i in range(ir_setup):
    ax.scatter(range(len(benchmarks)), std_ir_within[:,i])


#plt.close(fig)
