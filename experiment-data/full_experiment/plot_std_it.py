#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Aug 15 14:11:12 2022

@author: njapke
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# prevent figures from showing (as they are saved)
plt.ioff()

# variables
output_folder = "plots_it/"

# read data
df = pd.read_csv("experiment.csv", index_col="m_id")

# get all benchmarks
benchmarks = set(df["b_name"])

# get setup variables
bed_setup = df["bed_setup"][1]
it_setup = df["it_setup"][1]
sr_setup = df["sr_setup"][1]
ir_setup = df["ir_setup"][1]


# warm-up: discard first iteration
# df = df[df["it_pos"] > 1]
# it_setup = it_setup - 1


for bench in benchmarks:
    print("Processing "+bench)
    dft = df[df["b_name"] == bench]
    # calc var
    std = np.zeros((ir_setup,sr_setup,it_setup-1))
    # ir
    for i in range(1,ir_setup+1):
        # sr
        for j in range(1,sr_setup+1):
            tmp = dft[(dft["ir_pos"] == i) & (dft["sr_pos"] == j)]
            data = np.array(tmp["ns_per_op"])
            # it
            for k in range(2,it_setup+1):
                n = k*bed_setup
                std[i-1,j-1,k-2] = np.sqrt(1/(n-1) * ((data[:n] - data[:n].mean())**2).sum() )
    
    # plot
    fig = plt.figure(figsize=(14,4))
    ax = plt.axes()
    ax.set_xticks(range(it_setup-1), range(2,it_setup+1))

    for i in range(ir_setup):
        for j in range(sr_setup):
            ax.plot(std[i,j,:], alpha=1.0)

    ax.set_title('Std of ns per op for different it for benchmark ' + bench)
    ax.set_xlabel('iterations')
    ax.set_ylabel('Std ns per op')

    fig.savefig(output_folder+bench.replace("/","-")+".png")
    plt.close(fig)




