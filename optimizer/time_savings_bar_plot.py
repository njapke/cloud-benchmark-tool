#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Feb 27 16:52:26 2023

@author: njapke
"""

import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.gridspec as gs

method_map = {"cv__mean__ci_bootstrap_mean_p":"Mean (CV)",
              "cv__median__ci_bootstrap_median_p":"Median (CV)",
              "rciw_mean_p__mean__ci_bootstrap_mean_p": "Mean (RCIW_1)",
              "rciw_mean_t__mean__ci_bootstrap_mean_t":"Mean (RCIW_2)",
              "rciw_median_p__median__ci_bootstrap_median_p":"Median (RCIW_3)",
              "rmad__mean__ci_bootstrap_mean_p":"Mean (RMAD)",
              "rmad__median__ci_bootstrap_median_p":"Median (RMAD)",
              "cv_mean_p":"Mean (CV)",
              "cv_median_p":"Median (CV)",
              "rciw_mean_p": "Mean (RCIW_1)",
              "rciw_mean_t":"Mean (RCIW_2)",
              "rciw_median_p":"Median (RCIW_3)",
              "rciw_median_t":"Median (RCIW_4)",
              "rmad_mean_p":"Mean (RMAD)",
              "rmad_median_p":"Median (RMAD)"}

go_data_path = "go_optimization"

# get sorted list of all files
go_projects = list(os.walk(go_data_path))[0][1]
go_projects.sort()

# read in go data
go_optimization_quality = []
for project in go_projects:
    data_path = go_data_path+"/"+project
    
    # get sorted list of all files
    folders = list(os.walk(data_path))[0][1]
    folders.sort()
    
    print("Begin reading "+project)
    if len(go_optimization_quality) == 0:
        go_optimization_quality = pd.read_csv(data_path+"/quality_analysis.csv")
    else:
        new_df = pd.read_csv(data_path+"/quality_analysis.csv")
        go_optimization_quality = pd.concat([go_optimization_quality, new_df])

list_of_go_projects = list(np.array(go_optimization_quality["Project"].drop_duplicates()))
L = len(list_of_go_projects)

# plot variables
max_time_color = "tab:blue"
min_time_color = "tab:orange"
leq001_color = "tab:red"
leq003_color = "tab:green"


# initialize figure
fig = plt.figure(figsize=(12,8))
# fig.set_layout_engine("tight")

# subfigures for methods
subfigs = fig.subfigures(2, 3).flat # flatten the two-dimensional array for easier indexing


# create each subfigure
for i in range(5):
    # prepare iteration
    if i == 0:
        go_projs = go_optimization_quality[go_optimization_quality["Method"] == "cv_mean_p"]
        subfigs[i].suptitle("CV")
    elif i == 1:
        go_projs = go_optimization_quality[go_optimization_quality["Method"] == "rmad_median_p"]
        subfigs[i].suptitle("RMAD")
    elif i == 2:
        go_projs = go_optimization_quality[go_optimization_quality["Method"] == "rciw_mean_p"]
        subfigs[i].suptitle("RCIW$_1$")
    elif i == 3:
        go_projs = go_optimization_quality[go_optimization_quality["Method"] == "rciw_mean_t"]
        subfigs[i].suptitle("RCIW$_2$")
    elif i == 4:
        go_projs = go_optimization_quality[go_optimization_quality["Method"] == "rciw_median_p"]
        subfigs[i].suptitle("RCIW$_3$")
    
    # GridSpec for facets
    inner = gs.GridSpec(1, 2, wspace=0.1, hspace=0.1, width_ratios=[1,3])
    
    # initialize go subplot
    # subfigs[i].set_facecolor('none')
    ax1 = plt.Subplot(subfigs[i], inner[0])
    
    # setup title, ticks, limits, labels
    ax1.set_title("Go projects")
    ax1.set_xticks(range(L), list_of_go_projects, rotation="vertical")
    ax1.set_xlim(-0.5, L-0.5)
    ax1.set_ylim(0, max(go_projs["Max Time in h"]) + 0.1)
    ax1.set_ylabel("execution time (h)")
    
    # plot bars
    l1 = ax1.bar(range(L), go_projs["Max Time in h"], color=max_time_color, label="execution time of full configuration")
    l2 = ax1.bar(range(L), go_projs["Min Time in h"], color=min_time_color, label="execution time of optimized configuration")
    subfigs[i].add_subplot(ax1)
    
    # twin x and quality marks (only works when plotted on twin after original is added to figure)
    ax1t = ax1.twinx()
    ax1t.set_ylim(0,1.1)
    ax1t.set_ylabel("fraction of microbenchmarks (x marks)")
    
    l3 = ax1t.scatter(np.array(range(L)) - 0.1, go_projs["Fraction of leq 0.01 change"], marker="x", color=leq001_color, label="fraction of 0.01 change")
    l4 = ax1t.scatter(np.array(range(L)) + 0.1, go_projs["Fraction of leq 0.03 change"], marker="x", color=leq003_color, label="fraction of 0.03 change")
    
    
    # initialize java subplot
    ax2 = plt.Subplot(subfigs[i], inner[1])
    ax2.bar([0],[2])
    subfigs[i].add_subplot(ax2)

# fix last (unused) subfigure hiding legend (matplotlib bug)
subfigs[-1].set_facecolor('none')

# add legend
# fig.legend(handles, labels, loc='lower right', bbox_to_anchor=(0.9,0.3))
fig.legend(handles=[l1,l2,l3,l4], loc='lower right')

# plt.close(fig)
# fig.savefig("time_savings2.pdf")
