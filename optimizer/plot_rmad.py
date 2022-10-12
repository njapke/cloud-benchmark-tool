#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Oct  5 17:19:39 2022

@author: njapke
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# read data
min_rmad_mean_p = pd.read_csv("toml_results/rmad_mean_p/optimizer_results/min_config_res.csv")
min_rmad_median_p = pd.read_csv("toml_results/rmad_median_p/optimizer_results/min_config_res.csv")

full_rciw_mean_p = pd.read_csv("toml_results/rciw_mean_p/optimizer_results/full_config_res.csv")
full_rciw_median_p = pd.read_csv("toml_results/rciw_median_p/optimizer_results/full_config_res.csv")
full_rciw_mean_t = pd.read_csv("toml_results/rciw_mean_t/optimizer_results/full_config_res.csv")
full_rciw_median_t = pd.read_csv("toml_results/rciw_median_t/optimizer_results/full_config_res.csv")

# get all benchmarks
benchmarks = np.array(min_rmad_mean_p["Benchmark"].drop_duplicates())

# prevent figures from showing (as they are saved)
plt.ioff()

# variables
output_folder = "plots_rmad/"

# for bench in ...
#bench = "BenchmarkScanComments/1kValid"

for bench in benchmarks:
    print("Processing "+bench)

    # setup
    fig = plt.figure(figsize=(8,4))
    ax = plt.axes(xlim=(-0.5,3))
    
    min_rmad_bench = min_rmad_mean_p[min_rmad_mean_p["Benchmark"] == bench]
    min_conf_rmad = min_rmad_bench["Config"].iloc[0]
    
    ax.set_xticks(range(1,3),["full setup\n(3, 5, 5)","reduced setup\n"+min_conf_rmad])
    ax.set_title("optimizer results for " + bench + "\nusing RMAD")
    #ax.set_xlabel("tested setup")
    ax.set_ylabel("ns per op")
    
    ## BEGIN ##
    # FULL #
    
    # select full with ci p
    line_mean = full_rciw_mean_p[full_rciw_mean_p["Benchmark"] == bench]
    line_median = full_rciw_median_p[full_rciw_median_p["Benchmark"] == bench]
    
    # plot full at 1
    mean_leg, = ax.plot([0.8,1.0],[line_mean["Average"],line_mean["Average"]],"r-")
    median_leg, = ax.plot([1.0,1.2],[line_median["Average"],line_median["Average"]],"r:")
    
    # ci mean p
    ymin = line_mean["CI Lower"].iloc[0]
    ywidth = line_mean["CI Upper"].iloc[0] - ymin
    p_leg = ax.broken_barh([(0.8,0.2)],(ymin,ywidth), color="blue", alpha=0.2)
    
    # ci median p
    ymin = line_median["CI Lower"].iloc[0]
    ywidth = line_median["CI Upper"].iloc[0] - ymin
    ax.broken_barh([(1.0,0.2)],(ymin,ywidth), color="blue", alpha=0.2)
    
    # select full with ci t
    line_mean = full_rciw_mean_t[full_rciw_mean_t["Benchmark"] == bench]
    line_median = full_rciw_median_t[full_rciw_median_t["Benchmark"] == bench]
    
    # ci mean t
    ymin = line_mean["CI Lower"].iloc[0]
    ywidth = line_mean["CI Upper"].iloc[0] - ymin
    t_leg = ax.broken_barh([(0.8,0.2)],(ymin,ywidth), color="orangered", alpha=0.2)
    
    # ci median t
    ymin = line_median["CI Lower"].iloc[0]
    ywidth = line_median["CI Upper"].iloc[0] - ymin
    ax.broken_barh([(1.0,0.2)],(ymin,ywidth), color="orangered", alpha=0.2)
    
    # RMAD #
    
    # select rmad with ci p
    line_mean = min_rmad_mean_p[min_rmad_mean_p["Benchmark"] == bench]
    line_median = min_rmad_median_p[min_rmad_median_p["Benchmark"] == bench]
    
    # plot rmad at 2
    ax.plot([1.8,2.0],[line_mean["Average"],line_mean["Average"]],"r-")
    ax.plot([2.0,2.2],[line_median["Average"],line_median["Average"]],"r:")
    
    # ci mean p
    ymin = line_mean["CI Lower"].iloc[0]
    ywidth = line_mean["CI Upper"].iloc[0] - ymin
    ax.broken_barh([(1.8,0.2)],(ymin,ywidth), color="blue", alpha=0.2)
    
    # ci median p
    ymin = line_median["CI Lower"].iloc[0]
    ywidth = line_median["CI Upper"].iloc[0] - ymin
    ax.broken_barh([(2.0,0.2)],(ymin,ywidth), color="blue", alpha=0.2)
    
    ax.legend([mean_leg, median_leg, p_leg, t_leg],["mean","median","p interval","t interval"], loc=2)
    
    fig.savefig(output_folder+bench.replace("/","-")+".png")
    plt.close(fig)




