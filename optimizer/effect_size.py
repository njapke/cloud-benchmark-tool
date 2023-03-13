#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Feb 22 13:43:34 2023

@author: njapke
"""

import os
import numpy as np
import pandas as pd
import scipy.stats as sta
import scikit_posthocs as sp
from cliffs_delta import cliffs_delta

# prevent showing of figures
# plt.ioff()
# sns.set(rc={'figure.figsize':(12,8)})

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
# path_of_projects = "go_optimization"
# full_config_time = 3*5*5 # go
# full_config_string = "(3, 5, 5)"
# path_of_projects = "laaber_optimization_warmup"
# full_config_time = 5*50 # java warmup
# full_config_string = "(5, 50)"
path_of_projects = "laaber_optimization_nowarmup"
full_config_time = 5*100 # java no warmup
full_config_string = "(5, 100)"

# get sorted list of all files
projects = list(os.walk(path_of_projects))[0][1]
projects.sort()

h_test = []
for project in projects:

    data_path = path_of_projects+"/"+project
    
    # get sorted list of all files
    folders = list(os.walk(data_path))[0][1]
    folders.sort()
    
    print("Begin analyzing "+project)
    res = {}
    # loop over all subfolders
    # full_setup = pd.read_csv(data_path+"/cv_mean_p/full_config_res.csv")
    full_setup = pd.read_csv(data_path+"/cv__mean__ci_bootstrap_mean_p/full_config_res.csv")
    for folder in folders:
        if folder == "rciw_median_t":
            continue # skip rciw_median_t
        print("Processing "+folder)
        
        # quality data
        min_setup = pd.read_csv(data_path+"/"+folder+"/min_config_res.csv")
        quality = pd.read_csv(data_path+"/"+folder+"/quality_df.csv")
        N = len(min_setup)
        
        res[folder] = min_setup["Average"]
    
    # kruskal-wallis h test
    methods = [method_map[x] for x in res.keys()]
    samp = list(res.values())
    h_test_res = sta.kruskal(*samp)
    h_test.append([project, h_test_res.statistic, h_test_res.pvalue])
    
    # dunn's post-hoc test
    dunns_test_df = sp.posthoc_dunn(samp)
    dunns_test_df.index = methods
    dunns_test_df.columns = methods
    dunns_test_df.to_csv(data_path+"/dunns_test2.csv")
    
    # cliff's delta
    n_samp = len(samp)
    delta_res = np.zeros((n_samp,n_samp))
    for i in range(n_samp):
        for j in range(n_samp):
            delta_res[i,j] = cliffs_delta(samp[i], samp[j])[0]
    delta_df = pd.DataFrame(delta_res, index=methods, columns=methods)
    delta_df.to_csv(data_path+"/cliffs_delta2.csv")
    

h_test_df = pd.DataFrame(h_test, columns=["Project","Statistic","p-Value"])
h_test_df.to_csv(path_of_projects+"/kruskal2.csv",index=False)

