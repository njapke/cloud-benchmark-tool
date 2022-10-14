#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Oct 10 13:47:43 2022

@author: njapke
"""

import numpy as np
import pandas as pd

# quality data
min_setup = pd.read_csv("toml_results/rciw_median_t/optimizer_results/min_config_res.csv")
quality = pd.read_csv("toml_results/rciw_median_t/optimizer_results/quality_df.csv")

# Only for RCIW median t: filter out invalid benchmarks
filter_invalid = (min_setup["Average"] != min_setup["CI Upper"]) | (min_setup["Average"] != min_setup["CI Lower"])
min_setup = min_setup[filter_invalid]
quality = quality[quality["Benchmark"].isin(min_setup["Benchmark"])]

# filter for reduction
actual_reduction = min_setup[min_setup["Config"] != "(3, 5, 5)"]

# apply filter
q_filt = quality[quality["Benchmark"].isin(actual_reduction["Benchmark"])]

# time saving
max_time = 3*5*5*35
time_saved = np.sum(np.array(quality["Time Saved"]))
min_time = max_time - time_saved

# avg diff
avg_diff = np.abs(np.array(q_filt["Average Difference"]))
perc_avg = np.percentile(avg_diff, [84], method="closest_observation")
worst_avg = max(avg_diff)

# ci diff
ci_up_diff = np.abs(np.array(q_filt["CI Upper Difference"]))
worst_ci_u = max(ci_up_diff)
ci_lo_diff = np.abs(np.array(q_filt["CI Lower Difference"]))
worst_ci_lo = max(ci_lo_diff)







