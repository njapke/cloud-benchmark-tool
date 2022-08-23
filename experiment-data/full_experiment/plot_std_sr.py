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
output_folder = "plots_sr/"

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
    std = np.zeros((ir_setup,sr_setup))
    # ir
    for i in range(1,ir_setup+1):
        tmp = dft[(dft["ir_pos"] == i)]
        data = np.array(tmp["ns_per_op"])
        # sr
        for j in range(1,sr_setup+1):
            n = it_setup * bed_setup
            n0 = it_setup * bed_setup * (j-1)
            n1 = it_setup * bed_setup * j
            std[i-1,j-1] = np.sqrt(1/(n-1) * ((data[n0:n1] - data[n0:n1].mean())**2).sum() )
    
    # plot
    fig = plt.figure(figsize=(14,4))
    ax = plt.axes()
    ax.set_xticks(range(sr_setup-1), range(1,sr_setup))

    for i in range(ir_setup):
        ax.plot(std[i,:], alpha=1.0)

    ax.set_title('Std of ns per op for different sr for benchmark ' + bench)
    ax.set_xlabel('sr')
    ax.set_ylabel('Std ns per op')

    fig.savefig(output_folder+bench.replace("/","-")+".png")
    plt.close(fig)




