#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Mar 14 11:24:33 2023

@author: njapke
"""

import os
import pandas as pd
import numpy as np

path_of_log4j2_nowarmup = "laaber_optimization_nowarmup/laaber_log4j2"

broken_df = pd.read_csv("laaber_preprocessed/laaber_log4j2_list_of_broken_benchmarks.csv")

broken_benchmarks = np.array(broken_df["b_name"])

# get sorted list of all files
folders = list(os.walk(path_of_log4j2_nowarmup))[0][1]
folders.sort()

for fldr in folders:
    full_df = pd.read_csv(path_of_log4j2_nowarmup + "/" + fldr + "/full_config_res.csv")
    min_df = pd.read_csv(path_of_log4j2_nowarmup + "/" + fldr + "/min_config_res.csv")
    q_df = pd.read_csv(path_of_log4j2_nowarmup + "/" + fldr + "/quality_df.csv")
    
    full_df_filter = full_df["Benchmark"].isin(broken_benchmarks)
    min_df_filter = min_df["Benchmark"].isin(broken_benchmarks)
    q_df_filter = q_df["Benchmark"].isin(broken_benchmarks)
    
    full_df = full_df[~full_df_filter]
    min_df = min_df[~min_df_filter]
    q_df = q_df[~q_df_filter]
    
    full_df.to_csv(path_of_log4j2_nowarmup + "/" + fldr + "/full_config_res.csv", index=False)
    min_df.to_csv(path_of_log4j2_nowarmup + "/" + fldr + "/min_config_res.csv", index=False)
    q_df.to_csv(path_of_log4j2_nowarmup + "/" + fldr + "/quality_df.csv", index=False)
    
    