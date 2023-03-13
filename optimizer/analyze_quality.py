#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Oct 10 13:47:43 2022

@author: njapke
"""

import os
import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import scipy.stats as sta
import scikit_posthocs as sp
from cliffs_delta import cliffs_delta

# prevent showing of figures
plt.ioff()
sns.set(rc={'figure.figsize':(12,8)})

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

# input data
path_of_projects = "go_optimization"
full_config_time = 3*5*5 # go
full_config_string = "(3, 5, 5)"
# path_of_projects = "laaber_optimization_warmup"
# full_config_time = 5*50 # java warmup
# full_config_string = "(5, 50)"
# path_of_projects = "laaber_optimization_nowarmup"
# full_config_time = 5*100 # java no warmup
# full_config_string = "(5, 100)"

# get sorted list of all files
projects = list(os.walk(path_of_projects))[0][1]
projects.sort()


#project = "laaber_jmh-jdk-microbenchmarks"
h_test = []
for project in projects:

    data_path = path_of_projects+"/"+project
    
    # get sorted list of all files
    folders = list(os.walk(data_path))[0][1]
    folders.sort()
    
    print("Begin analyzing "+project)
    res = []
    avg_dev_col = []
    method_col = []
    # loop over all subfolders
    for folder in folders:
        print("Processing "+folder)
        
        # quality data
        min_setup = pd.read_csv(data_path+"/"+folder+"/min_config_res.csv")
        quality = pd.read_csv(data_path+"/"+folder+"/quality_df.csv")
        N = len(min_setup)
        
        # only for RCIW median t: filter out invalid benchmarks
        # filter_invalid = (min_setup["Average"] != min_setup["CI Upper"]) | (min_setup["Average"] != min_setup["CI Lower"])
        # min_setup = min_setup[filter_invalid]
        # quality = quality[quality["Benchmark"].isin(min_setup["Benchmark"])]
        
        # filter for reduction
        # actual_reduction = min_setup[min_setup["Config"] != full_config_string]
        
        # apply filter
        # q_filt = quality[quality["Benchmark"].isin(actual_reduction["Benchmark"])]
        
        # time saving
        max_time_s = full_config_time*N
        max_time_h = max_time_s / 60 / 60
        time_saved = np.sum(np.array(quality["Time Saved"]))
        time_saved_p = time_saved / max_time_s
        min_time_s = max_time_s - time_saved
        min_time_h = min_time_s / 60 / 60
        
        # avg diff
        abs_avg_diff = np.abs(np.array(quality["Average Difference"]))
        leq001 = len(abs_avg_diff[abs_avg_diff <= 0.01]) / len(abs_avg_diff)
        leq003 = len(abs_avg_diff[abs_avg_diff <= 0.03]) / len(abs_avg_diff)
        # perc_avg = np.percentile(abs_avg_diff, [1,10,25,50,75,90,99], method="closest_observation")
        
        # ci diff
        ci_up_diff = np.abs(np.array(quality["CI Upper Difference"]))
        worst_ci_u = max(ci_up_diff)
        ci_lo_diff = np.abs(np.array(quality["CI Lower Difference"]))
        worst_ci_lo = max(ci_lo_diff)
        
        avg_diff = np.array(quality["Average Difference"])
        N = len(avg_diff)
        if len(avg_dev_col) == 0:
            avg_dev_col = avg_diff
            method_col = np.repeat([method_map[folder]],N)
        else:
            avg_dev_col = np.concatenate((avg_dev_col, avg_diff))
            method_col = np.concatenate((method_col, np.repeat([method_map[folder]],N)))
        
        
        res.append([project, folder, max_time_s, max_time_h, min_time_s, min_time_h, time_saved, time_saved_p, leq001, leq003, worst_ci_u, worst_ci_lo])
    
    result_df = pd.DataFrame(res, columns=["Project","Method","Max Time in s","Max Time in h","Min Time in s","Min Time in h","Time Saved","Time Saved %","Fraction of leq 0.01 change","Fraction of leq 0.03 change","CI Lower Dev","CI Upper Dev"])
    avg_dev_df = pd.DataFrame({"Average Difference":avg_dev_col, "Method":method_col})
    result_df.to_csv(data_path+"/quality_analysis.csv",index=False)
    
    # kruskal-wallis h test
    methods = avg_dev_df["Method"].drop_duplicates()
    samp = [avg_dev_df[avg_dev_df["Method"] == x]["Average Difference"] for x in methods]
    h_test_res = sta.kruskal(*samp)
    h_test.append([project, h_test_res.statistic, h_test_res.pvalue])
    
    # dunn's post-hoc test
    dunns_test_df = sp.posthoc_dunn(samp)
    dunns_test_df.index = list(methods)
    dunns_test_df.columns = list(methods)
    dunns_test_df.to_csv(data_path+"/dunns_test.csv")
    
    # cliff's delta
    n_samp = len(samp)
    delta_res = np.zeros((n_samp,n_samp))
    for i in range(n_samp):
        for j in range(n_samp):
            delta_res[i,j] = cliffs_delta(samp[i], samp[j])[0]
    delta_df = pd.DataFrame(delta_res, index=list(methods), columns=list(methods))
    delta_df.to_csv(data_path+"/cliffs_delta.csv")
    
    plot = sns.boxplot(data=avg_dev_df, x="Average Difference", y="Method")
    fig = plot.get_figure()
    fig.savefig(path_of_projects+"/"+project+"_boxplot.png",bbox_inches="tight")
    plt.close(fig)

h_test_df = pd.DataFrame(h_test, columns=["Project","Statistic","p-Value"])
h_test_df.to_csv(path_of_projects+"/kruskal.csv",index=False)




