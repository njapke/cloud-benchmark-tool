#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Oct  5 14:19:46 2022

@author: njapke
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# read data
min_config_res = pd.read_csv("optimizer_results/min_config_res.csv")
full_config_res = pd.read_csv("optimizer_results/full_config_res.csv")
quality_df = pd.read_csv("optimizer_results/quality_df.csv")

# get all benchmarks
benchmarks = np.array(min_config_res["Benchmark"].drop_duplicates())

# prevent figures from showing (as they are saved)
plt.ioff()

# variables
output_folder = "plots/"

for bench in benchmarks:
    print("Processing "+bench)
    min_line = min_config_res[min_config_res["Benchmark"] == bench]
    full_line = full_config_res[full_config_res["Benchmark"] == bench]

    fig = plt.figure(figsize=(14,4))
    ax = plt.axes(xlim=(0,3))

    min_conf = min_line["Config"].iloc[0]

    ax.set_xticks([1,2],["full setup (3, 5, 5)","minimal setup " + min_conf])
    ax.set_title("optimizer results for " + bench)
    #ax.set_xlabel("tested setup")
    ax.set_ylabel("ns per op")

    # plot full at 1
    ax.plot([0.8,1.2],[full_line["Average"],full_line["Average"]],"r-")

    ymin = full_line["CI Lower"].iloc[0]
    ywidth = full_line["CI Upper"].iloc[0] - ymin
    ax.broken_barh([(0.8,0.4)],(ymin,ywidth), color="blue", alpha=0.2)

    # plot min at 2
    ax.plot([1.8,2.2],[min_line["Average"],min_line["Average"]],"r-")

    ymin = min_line["CI Lower"].iloc[0]
    ywidth = min_line["CI Upper"].iloc[0] - ymin
    ax.broken_barh([(1.8,0.4)],(ymin,ywidth), color="blue", alpha=0.2)
    #ax.broken_barh([(0.8,0.4)],(ymin,ywidth), color="orangered", alpha=0.2)
    
    fig.savefig(output_folder+bench.replace("/","-")+".png")
    plt.close(fig)



