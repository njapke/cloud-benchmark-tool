#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Aug  9 23:52:21 2022

@author: njapke
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import bootstrap as bt

# prevent figures from showing (as they are saved)
plt.ioff()

# variables
output_folder = "plots/"

# read files
df_1 = pd.read_csv("ir1-1.csv", index_col="m_id")
df_2 = pd.read_csv("ir1-2.csv", index_col="m_id")
df_3 = pd.read_csv("ir1-3.csv", index_col="m_id")

# transform bed
df_1["bed"] = df_1["bed"].apply(lambda s : int(s[:-1]))
df_2["bed"] = df_2["bed"].apply(lambda s : int(s[:-1]))
df_3["bed"] = df_3["bed"].apply(lambda s : int(s[:-1]))

# get all benchmarks
benchmarks = set(df_1["b_name"])

# get data across a dimension
for bench in benchmarks:
    print("Processing "+bench)
    df_filtered = df_1[df_1["b_name"] == bench]
    means = []
    ci_bounds = []
    for i in range(1,6): # 1 to 5
        tmp = df_filtered[(df_filtered["bed"] == 5) & (df_filtered["iterations"] == i) & (df_filtered["sr"] == 3)]
        #tmp = np.array(tmp["ns_per_op"])

        # bootstrap distribution
        bs_dist = bt.bootstrap_distribution(np.array(tmp["ns_per_op"]), 10_000)
        means.append(bs_dist.mean()) # mean
        ci_bounds.append(np.percentile(bs_dist, [2.5, 97.5])) # 95% CI bounds
    means = np.array(means)
    ci_bounds = np.array(ci_bounds)

    # plot
    fig = plt.figure(figsize=(14,4))
    ax = plt.axes()

    x = range(1,6)
    ax.plot(x, means, color="blue", alpha=1.0)
    ax.fill_between(x, ci_bounds[:,0], ci_bounds[:,1], color="blue", alpha=0.2)
    
    ax.set_title('ns per op for different it for benchmark ' + bench)
    ax.set_xlabel('iterations')
    ax.set_ylabel('ns per op')

    fig.savefig(output_folder+bench.replace("/","-")+".png")
    plt.close(fig)

