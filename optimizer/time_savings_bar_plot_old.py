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
outer = gs.GridSpec(2, 3)


# initialize subplot
# ax1 = fig.add_subplot(2,3,1)
ax1 = plt.Subplot(fig, outer)

# prepare data
go_cv = go_optimization_quality[go_optimization_quality["Method"] == "cv_mean_p"]

# set title, ticks, limits, labels
ax1.set_title("CV")
ax1.set_xticks(range(L), list_of_go_projects, rotation="vertical")
ax1.set_xlim(-0.5, L-0.5)
ax1.set_ylim(0, max(go_cv["Max Time in h"]) + 0.1)
# ax1.set_xlabel("projects")
ax1.set_ylabel("execution time (h)")

# plot bars
ax1.bar(range(L), go_cv["Max Time in h"], color=max_time_color)
ax1.bar(range(L), go_cv["Min Time in h"], color=min_time_color)
# ax1.bar([5], [3], color=max_time_color)

# twin x and quality marks
ax11 = ax1.twinx()
ax11.set_ylim(0,1.1)
ax11.set_ylabel("fraction of microbenchmarks (x marks)")

ax11.scatter(np.array(range(L)) - 0.1, go_cv["Fraction of leq 0.01 change"], marker="x", color=leq001_color)
ax11.scatter(np.array(range(L)) + 0.1, go_cv["Fraction of leq 0.03 change"], marker="x", color=leq003_color)
fig.add_subplot(ax1)

# initialize subplot
ax2 = fig.add_subplot(2,3,2, sharex=ax1, sharey=ax1)

# prepare data
go_rmad = go_optimization_quality[go_optimization_quality["Method"] == "rmad_median_p"]

# set title, ticks, limits, labels
ax2.set_title("RMAD")
ax2.set_xticks(range(L), list_of_go_projects, rotation="vertical")
# ax2.set_xlim(-0.5, L-0.5)
# ax2.set_ylim(0, max(go_rmad["Max Time in h"]) + 0.1)
# ax2.set_xlabel("projects")
ax2.set_ylabel("execution time (h)")

# plot bars
ax2.bar(range(L), go_rmad["Max Time in h"], color=max_time_color)
ax2.bar(range(L), go_rmad["Min Time in h"], color=min_time_color)

# twin x and quality marks
ax21 = ax2.twinx()
ax21.set_ylim(0,1.1)
ax21.set_ylabel("fraction of microbenchmarks (x marks)")

ax21.scatter(np.array(range(L)) - 0.1, go_rmad["Fraction of leq 0.01 change"], marker="x", color=leq001_color)
ax21.scatter(np.array(range(L)) + 0.1, go_rmad["Fraction of leq 0.03 change"], marker="x", color=leq003_color)


# initialize subplot
ax3 = fig.add_subplot(2,3,3, sharex=ax1, sharey=ax1)

# prepare data
go_rciw1 = go_optimization_quality[go_optimization_quality["Method"] == "rciw_mean_p"]

# set title, ticks, limits, labels
ax3.set_title("RCIW$_1$")
ax3.set_xticks(range(L), list_of_go_projects, rotation="vertical")
# ax3.set_xlim(-0.5, L-0.5)
# ax3.set_ylim(0, max(go_rciw1["Max Time in h"]) + 0.1)
# ax3.set_xlabel("projects")
ax3.set_ylabel("execution time (h)")

# plot bars
ax3.bar(range(L), go_rciw1["Max Time in h"], color=max_time_color)
ax3.bar(range(L), go_rciw1["Min Time in h"], color=min_time_color)

# twin x and quality marks
ax31 = ax3.twinx()
ax31.set_ylim(0,1.1)
ax31.set_ylabel("fraction of microbenchmarks (x marks)")

ax31.scatter(np.array(range(L)) - 0.1, go_rciw1["Fraction of leq 0.01 change"], marker="x", color=leq001_color)
ax31.scatter(np.array(range(L)) + 0.1, go_rciw1["Fraction of leq 0.03 change"], marker="x", color=leq003_color)


# initialize subplot
ax4 = fig.add_subplot(2,3,4, sharex=ax1, sharey=ax1)

# prepare data
go_rciw2 = go_optimization_quality[go_optimization_quality["Method"] == "rciw_mean_t"]

# set title, ticks, limits, labels
ax4.set_title("RCIW$_2$")
ax4.set_xticks(range(L), list_of_go_projects, rotation="vertical")
# ax4.set_xlim(-0.5, L-0.5)
# ax4.set_ylim(0, max(go_rciw2["Max Time in h"]) + 0.1)
# ax4.set_xlabel("projects")
ax4.set_ylabel("execution time (h)")

# plot bars
ax4.bar(range(L), go_rciw2["Max Time in h"], color=max_time_color)
ax4.bar(range(L), go_rciw2["Min Time in h"], color=min_time_color)

# twin x and quality marks
ax41 = ax4.twinx()
ax41.set_ylim(0,1.1)
ax41.set_ylabel("fraction of microbenchmarks (x marks)")

ax41.scatter(np.array(range(L)) - 0.1, go_rciw2["Fraction of leq 0.01 change"], marker="x", color=leq001_color)
ax41.scatter(np.array(range(L)) + 0.1, go_rciw2["Fraction of leq 0.03 change"], marker="x", color=leq003_color)


# initialize subplot
ax5 = fig.add_subplot(2,3,5, sharex=ax1, sharey=ax1)

# prepare data
go_rciw3 = go_optimization_quality[go_optimization_quality["Method"] == "rciw_median_p"]

# set title, ticks, limits, labels
ax5.set_title("RCIW$_3$")
ax5.set_xticks(range(L), list_of_go_projects, rotation="vertical")
# ax5.set_xlim(-0.5, L-0.5)
# ax5.set_ylim(0, max(go_rciw3["Max Time in h"]) + 0.1)
# ax5.set_xlabel("projects")
ax5.set_ylabel("execution time (h)")

# plot bars
ax5.bar(range(L), go_rciw3["Max Time in h"], color=max_time_color, label="execution time of full configuration")
ax5.bar(range(L), go_rciw3["Min Time in h"], color=min_time_color, label="execution time of optimized configuration")

# twin x and quality marks
ax51 = ax5.twinx()
ax51.set_ylim(0,1.1)
ax51.set_ylabel("fraction of microbenchmarks (x marks)")

ax51.scatter(np.array(range(L)) - 0.1, go_rciw3["Fraction of leq 0.01 change"], marker="x", color=leq001_color, label="fraction of 0.01 change")
ax51.scatter(np.array(range(L)) + 0.1, go_rciw3["Fraction of leq 0.03 change"], marker="x", color=leq003_color, label="fraction of 0.03 change")


# add legend based on ax5 and ax51
h1, l1 = ax5.get_legend_handles_labels()
h2, l2 = ax51.get_legend_handles_labels()
handles = h1 + h2
labels = l1 + l2
fig.legend(handles, labels, loc='lower right', bbox_to_anchor=(0.9,0.3))

# plt.close(fig)
# fig.savefig("time_savings.pdf")
