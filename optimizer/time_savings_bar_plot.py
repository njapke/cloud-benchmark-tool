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
java_data_path = "laaber_optimization_warmup"

### GO PROJECTS ###
# get sorted list of all folders
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
L_go = len(list_of_go_projects)


### JAVA PROJECTS ###
# get sorted list of all folders
java_projects = list(os.walk(java_data_path))[0][1]
java_projects.sort()

# read in go data
java_optimization_quality = []
for project in java_projects:
    data_path = java_data_path+"/"+project
    
    # get sorted list of all files
    folders = list(os.walk(data_path))[0][1]
    folders.sort()
    
    print("Begin reading "+project)
    if len(java_optimization_quality) == 0:
        java_optimization_quality = pd.read_csv(data_path+"/quality_analysis.csv")
    else:
        new_df = pd.read_csv(data_path+"/quality_analysis.csv")
        java_optimization_quality = pd.concat([java_optimization_quality, new_df])

list_of_java_projects = list(np.array(java_optimization_quality["Project"].drop_duplicates()))
L_java = len(list_of_java_projects)


# plot variables
max_time_color = "tab:blue"
min_time_color = "tab:orange"
leq001_color = "tab:red"
leq003_color = "tab:green"
leq005_color = "tab:purple"
leq010_color = "tab:gray"


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
        java_projs = java_optimization_quality[java_optimization_quality["Method"] == "cv__mean__ci_bootstrap_mean_p"]
        subfigs[i].suptitle("CV")
    elif i == 1:
        go_projs = go_optimization_quality[go_optimization_quality["Method"] == "rmad_median_p"]
        java_projs = java_optimization_quality[java_optimization_quality["Method"] == "rmad__median__ci_bootstrap_median_p"]
        subfigs[i].suptitle("RMAD")
    elif i == 2:
        go_projs = go_optimization_quality[go_optimization_quality["Method"] == "rciw_mean_p"]
        java_projs = java_optimization_quality[java_optimization_quality["Method"] == "rciw_mean_p__mean__ci_bootstrap_mean_p"]
        subfigs[i].suptitle("RCIW$_1$")
    elif i == 3:
        go_projs = go_optimization_quality[go_optimization_quality["Method"] == "rciw_mean_t"]
        java_projs = java_optimization_quality[java_optimization_quality["Method"] == "rciw_mean_t__mean__ci_bootstrap_mean_t"]
        subfigs[i].suptitle("RCIW$_2$")
    elif i == 4:
        go_projs = go_optimization_quality[go_optimization_quality["Method"] == "rciw_median_p"]
        java_projs = java_optimization_quality[java_optimization_quality["Method"] == "rciw_median_p__median__ci_bootstrap_median_p"]
        subfigs[i].suptitle("RCIW$_3$")
    
    # GridSpec for facets
    inner = gs.GridSpec(1, 2, wspace=0.3, hspace=0.1, width_ratios=[1,3])
    
    # initialize go subplot
    ax1 = plt.Subplot(subfigs[i], inner[0])
    
    # setup title, ticks, limits, labels
    ax1.set_title("Go projects")
    ax1.set_xticks(range(L_go), list_of_go_projects, rotation="vertical")
    ax1.set_xlim(-0.5, L_go-0.5)
    ax1.set_ylim(0, max(go_projs["Max Time in h"]) + 0.1)
    # ax1.set_yscale("log")
    # ax1.set_ylim(0, max(java_projs["Max Time in h"]) + 0.1)
    ax1.set_ylabel("execution time (h)")
    
    # plot bars
    l1 = ax1.bar(range(L_go), go_projs["Max Time in h"], color=max_time_color, label="execution time of full configuration")
    l2 = ax1.bar(range(L_go), go_projs["Min Time in h"], color=min_time_color, label="execution time of optimized configuration")
    subfigs[i].add_subplot(ax1)
    
    # twin x and quality marks (only works when plotted on twin after original is added to figure)
    ax1t = ax1.twinx()
    ax1t.set_ylim(0,1.1)
    ax1t.set_yticks([])
    # ax1t.set_ylabel("fraction of microbenchmarks (x marks)")
    
    l3 = ax1t.scatter(np.array(range(L_go)) - 0.1, go_projs["Fraction of leq 0.01 change"], marker="x", color=leq001_color, label="fraction of 0.01 change")
    l4 = ax1t.scatter(np.array(range(L_go)) + 0.1, go_projs["Fraction of leq 0.03 change"], marker="x", color=leq003_color, label="fraction of 0.03 change")
    
    
    # initialize java subplot
    ax2 = plt.Subplot(subfigs[i], inner[1])
    
    # setup title, ticks, limits, labels
    ax2.set_title("Java projects")
    ax2.set_xticks(range(L_java), list_of_java_projects, rotation="vertical")
    ax2.set_xlim(-0.5, L_java-0.5)
    # ax2.set_yscale("log")
    ax2.set_ylim(0, max(java_projs["Max Time in h"]) + 0.1)
    # ax2.set_ylabel("execution time (h)")
    
    # plot bars, l1,l2 missing
    ax2.bar(range(L_java), java_projs["Max Time in h"], color=max_time_color, label="execution time of full configuration")
    ax2.bar(range(L_java), java_projs["Min Time in h"], color=min_time_color, label="execution time of optimized configuration")
    subfigs[i].add_subplot(ax2)
    
    # twin x and quality marks (only works when plotted on twin after original is added to figure)
    ax2t = ax2.twinx()
    ax2t.set_ylim(0,1.1)
    # ax2t.set_yticks([])
    ax2t.set_ylabel("fraction of microbenchmarks (x marks)")
    
    ax2t.scatter(np.array(range(L_java)) - 0.1, java_projs["Fraction of leq 0.01 change"], marker="x", color=leq001_color, label="fraction of 0.01 change")
    ax2t.scatter(np.array(range(L_java)) + 0.1, java_projs["Fraction of leq 0.03 change"], marker="x", color=leq003_color, label="fraction of 0.03 change")
    l5 = ax2t.scatter(np.array(range(L_java)) + 0.1, java_projs["Fraction of leq 0.05 change"], marker="x", color=leq005_color, label="fraction of 0.05 change")
    # ax2t.scatter(np.array(range(L_java)) + 0.1, java_projs["Fraction of leq 0.1 change"], marker="x", color=leq010_color, label="fraction of 0.1 change")

# fix last (unused) subfigure hiding legend (matplotlib bug)
subfigs[-1].set_facecolor('none')

# add legend
# fig.legend(handles, labels, loc='lower right', bbox_to_anchor=(0.9,0.3))
fig.legend(handles=[l1,l2,l3,l4,l5], loc='lower right')

# plt.close(fig)
fig.savefig("time_savings2.pdf")
