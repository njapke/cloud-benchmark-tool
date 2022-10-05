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
min_cv_mean_p = pd.read_csv("toml_results/cv_mean_p/optimizer_results/min_config_res.csv")
min_cv_median_p = pd.read_csv("toml_results/cv_median_p/optimizer_results/min_config_res.csv")
min_rmad_mean_p = pd.read_csv("toml_results/rmad_mean_p/optimizer_results/min_config_res.csv")
min_rmad_median_p = pd.read_csv("toml_results/rmad_median_p/optimizer_results/min_config_res.csv")

min_rciw_mean_p = pd.read_csv("toml_results/rciw_mean_p/optimizer_results/min_config_res.csv")
min_rciw_median_p = pd.read_csv("toml_results/rciw_median_p/optimizer_results/min_config_res.csv")
min_rciw_mean_t = pd.read_csv("toml_results/rciw_mean_t/optimizer_results/min_config_res.csv")
min_rciw_median_t = pd.read_csv("toml_results/rciw_median_t/optimizer_results/min_config_res.csv")

full_rciw_mean_p = pd.read_csv("toml_results/rciw_mean_p/optimizer_results/full_config_res.csv")
full_rciw_median_p = pd.read_csv("toml_results/rciw_median_p/optimizer_results/full_config_res.csv")
full_rciw_mean_t = pd.read_csv("toml_results/rciw_mean_t/optimizer_results/full_config_res.csv")
full_rciw_median_t = pd.read_csv("toml_results/rciw_median_t/optimizer_results/full_config_res.csv")

# get all benchmarks
benchmarks = np.array(min_cv_mean_p["Benchmark"].drop_duplicates())

# prevent figures from showing (as they are saved)
plt.ioff()

# variables
output_folder = "plots_full/"

# for bench in ...
#bench = "BenchmarkScanComments/1kValid"

for bench in benchmarks:
    print("Processing "+bench)

    # setup
    fig = plt.figure(figsize=(14,4))
    ax = plt.axes(xlim=(0,8))
    
    min_cv_bench = min_cv_mean_p[min_cv_mean_p["Benchmark"] == bench]
    min_conf_cv = min_cv_bench["Config"].iloc[0]
    
    min_rmad_bench = min_rmad_mean_p[min_rmad_mean_p["Benchmark"] == bench]
    min_conf_rmad = min_rmad_bench["Config"].iloc[0]
    
    min_rciw_mean_p_bench = min_rciw_mean_p[min_rciw_mean_p["Benchmark"] == bench]
    min_conf_rciw_mean_p = min_rciw_mean_p_bench["Config"].iloc[0]
    
    min_rciw_median_p_bench = min_rciw_median_p[min_rciw_median_p["Benchmark"] == bench]
    min_conf_rciw_median_p = min_rciw_median_p_bench["Config"].iloc[0]
    
    min_rciw_mean_t_bench = min_rciw_mean_t[min_rciw_mean_t["Benchmark"] == bench]
    min_conf_rciw_mean_t = min_rciw_mean_t_bench["Config"].iloc[0]
    
    min_rciw_median_t_bench = min_rciw_median_t[min_rciw_median_t["Benchmark"] == bench]
    min_conf_rciw_median_t = min_rciw_median_t_bench["Config"].iloc[0]
    
    ax.set_xticks(range(1,8),["full setup\n(3, 5, 5)","cv\n"+min_conf_cv,"rmad\n"+min_conf_rmad,"rciw mean p\n"+min_conf_rciw_mean_p,"rciw median p\n"+min_conf_rciw_median_p,"rciw mean t\n"+min_conf_rciw_mean_t,"rciw median t\n"+min_conf_rciw_median_t])
    ax.set_title("optimizer results for " + bench)
    #ax.set_xlabel("tested setup")
    ax.set_ylabel("ns per op")
    
    ## BEGIN ##
    # FULL #
    
    # select full with ci p
    line_mean = full_rciw_mean_p[full_rciw_mean_p["Benchmark"] == bench]
    line_median = full_rciw_median_p[full_rciw_median_p["Benchmark"] == bench]
    
    # plot full at 1
    ax.plot([0.8,1.0],[line_mean["Average"],line_mean["Average"]],"r-")
    ax.plot([1.0,1.2],[line_median["Average"],line_median["Average"]],"r-")
    
    # ci mean p
    ymin = line_mean["CI Lower"].iloc[0]
    ywidth = line_mean["CI Upper"].iloc[0] - ymin
    ax.broken_barh([(0.8,0.2)],(ymin,ywidth), color="blue", alpha=0.2)
    
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
    ax.broken_barh([(0.8,0.2)],(ymin,ywidth), color="orangered", alpha=0.2)
    
    # ci median t
    ymin = line_median["CI Lower"].iloc[0]
    ywidth = line_median["CI Upper"].iloc[0] - ymin
    ax.broken_barh([(1.0,0.2)],(ymin,ywidth), color="orangered", alpha=0.2)
    
    # CV #
    
    # select cv with ci p
    line_mean = min_cv_mean_p[min_cv_mean_p["Benchmark"] == bench]
    line_median = min_cv_median_p[min_cv_median_p["Benchmark"] == bench]
    
    # plot cv at 2
    ax.plot([1.8,2.0],[line_mean["Average"],line_mean["Average"]],"r-")
    ax.plot([2.0,2.2],[line_median["Average"],line_median["Average"]],"r-")
    
    # ci mean p
    ymin = line_mean["CI Lower"].iloc[0]
    ywidth = line_mean["CI Upper"].iloc[0] - ymin
    ax.broken_barh([(1.8,0.2)],(ymin,ywidth), color="blue", alpha=0.2)
    
    # ci median p
    ymin = line_median["CI Lower"].iloc[0]
    ywidth = line_median["CI Upper"].iloc[0] - ymin
    ax.broken_barh([(2.0,0.2)],(ymin,ywidth), color="blue", alpha=0.2)
    
    # RMAD #
    
    # select rmad with ci p
    line_mean = min_rmad_mean_p[min_rmad_mean_p["Benchmark"] == bench]
    line_median = min_rmad_median_p[min_rmad_median_p["Benchmark"] == bench]
    
    # plot rmad at 3
    ax.plot([2.8,3.0],[line_mean["Average"],line_mean["Average"]],"r-")
    ax.plot([3.0,3.2],[line_median["Average"],line_median["Average"]],"r-")
    
    # ci mean p
    ymin = line_mean["CI Lower"].iloc[0]
    ywidth = line_mean["CI Upper"].iloc[0] - ymin
    ax.broken_barh([(2.8,0.2)],(ymin,ywidth), color="blue", alpha=0.2)
    
    # ci median p
    ymin = line_median["CI Lower"].iloc[0]
    ywidth = line_median["CI Upper"].iloc[0] - ymin
    ax.broken_barh([(3.0,0.2)],(ymin,ywidth), color="blue", alpha=0.2)
    
    # RCIW mean p #
    
    # select rciw mean p
    line_mean = min_rciw_mean_p[min_rciw_mean_p["Benchmark"] == bench]
    
    # plot rciw mean p at 4
    ax.plot([3.9,4.1],[line_mean["Average"],line_mean["Average"]],"r-")
    
    # ci mean p
    ymin = line_mean["CI Lower"].iloc[0]
    ywidth = line_mean["CI Upper"].iloc[0] - ymin
    ax.broken_barh([(3.9,0.2)],(ymin,ywidth), color="blue", alpha=0.2)
    
    # RCIW median p #
    
    # select rciw median p
    line_median = min_rciw_median_p[min_rciw_median_p["Benchmark"] == bench]
    
    # plot rciw median p at 5
    ax.plot([4.9,5.1],[line_median["Average"],line_median["Average"]],"r-")
    
    # ci median p
    ymin = line_median["CI Lower"].iloc[0]
    ywidth = line_median["CI Upper"].iloc[0] - ymin
    ax.broken_barh([(4.9,0.2)],(ymin,ywidth), color="blue", alpha=0.2)
    
    # RCIW mean t #
    
    # select rciw mean t
    line_mean = min_rciw_mean_t[min_rciw_mean_t["Benchmark"] == bench]
    
    # plot rciw mean t at 6
    ax.plot([5.9,6.1],[line_mean["Average"],line_mean["Average"]],"r-")
    
    # ci mean p
    ymin = line_mean["CI Lower"].iloc[0]
    ywidth = line_mean["CI Upper"].iloc[0] - ymin
    ax.broken_barh([(5.9,0.2)],(ymin,ywidth), color="blue", alpha=0.2)
    
    # RCIW median t #
    
    # select rciw median t
    line_median = min_rciw_median_t[min_rciw_median_t["Benchmark"] == bench]
    
    # plot rciw median p at 7
    ax.plot([6.9,7.1],[line_median["Average"],line_median["Average"]],"r-")
    
    # ci median p
    ymin = line_median["CI Lower"].iloc[0]
    ywidth = line_median["CI Upper"].iloc[0] - ymin
    ax.broken_barh([(6.9,0.2)],(ymin,ywidth), color="blue", alpha=0.2)
    
    fig.savefig(output_folder+bench.replace("/","-")+".png")
    plt.close(fig)




