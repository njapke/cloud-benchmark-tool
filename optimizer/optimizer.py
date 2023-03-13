#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Aug 31 14:42:38 2022

@author: njapke
"""

import numpy as np
import pandas as pd
import stat_functions as st

class ConfigCounter:
    def __init__(self, sr, it, bed):
        self.sr = sr
        self.it = it
        self.bed = bed
        self.max = sr*it*bed
        self.current = -1

    def __iter__(self):
        return self

    def __next__(self):
        self.current += 1
        if self.current < self.max:
            bed = self.current % self.bed
            r = self.current // self.bed
            it = r % self.it
            r = r // self.it
            sr = r % self.sr
            return (sr+1,it+1,bed+1)
        raise StopIteration

# read data
df = pd.read_csv("zap.csv", index_col="m_id")

# get all benchmarks
benchmarks = np.array(df["b_name"].drop_duplicates())

# get setup variables
bed_setup = df["bed_setup"][1]
it_setup = df["it_setup"][1]
sr_setup = df["sr_setup"][1]
ir_setup = df["ir_setup"][1]
df.drop(columns=["bed_setup", "it_setup", "sr_setup", "ir_setup"], inplace=True)

# Select instability measure and CI method
calc_inst = st.cv
calc_ci = st.ci_bootstrap_mean_p
# calc_avg = np.median
calc_avg = np.mean

# Select threshold to mark benchmarks as unstable
ts = 0.01

res = []
# ir is always 3
for b in range(len(benchmarks)):
    bench = benchmarks[b]
    for c in ConfigCounter(sr_setup, it_setup, bed_setup): # sr, it, bed
        if c[0]*c[1] < 3:
            continue
        dft = df[(df["b_name"] == bench)
                 & (df["ir_pos"] <= 1)
                 & (df["sr_pos"] <= c[0])
                 & (df["it_pos"] <= c[1])
                 & (df["bed_pos"] <= c[2])]
        data = np.array(dft["ns_per_op"])
        
        inst = calc_inst(data, it=10000) # instability
        
        time = c[0]*c[1]*c[2] # time per instance in seconds
        
        avg = calc_avg(data)
        
        ci = calc_ci(data, it=10000)
        
        res.append([bench, c, inst, time, avg, min(ci), max(ci)])

result_df = pd.DataFrame(res, columns=["Benchmark","Config","Instability","Time","Average","CI Lower","CI Upper"])

reduced_res = result_df[result_df["Instability"] < ts]

min_config_idx = []
for b in range(len(benchmarks)):
    bench = benchmarks[b]
    b_res = reduced_res[reduced_res["Benchmark"] == bench]
    if b_res.empty:
        b_full = result_df[result_df["Benchmark"] == bench]
        min_config_idx.append(b_full.iloc[-1].name)
        continue
    
    min_time = b_res["Time"].min()
    
    # tie-breaker: min instability
    b_min_time = b_res[b_res["Time"] == min_time]
    min_inst_idx = b_min_time["Instability"].idxmin()
    
    min_config_idx.append(min_inst_idx)

min_config_res = result_df.iloc[min_config_idx]
full_config_res = result_df[result_df["Config"] == (sr_setup, it_setup, bed_setup)]

quality_diff = []
for bench in benchmarks:
    bench_min = min_config_res[min_config_res["Benchmark"] == bench].iloc[0]
    bench_full = full_config_res[full_config_res["Benchmark"] == bench].iloc[0]
    
    time_saved = bench_full["Time"] - bench_min["Time"]
    avg_diff = (bench_min["Average"] - bench_full["Average"]) / bench_full["Average"]
    
    ci_l_min = bench_min["CI Lower"]
    ci_u_min = bench_min["CI Upper"]
    ci_l_full = bench_full["CI Lower"]
    ci_u_full = bench_full["CI Upper"]
    
    ci_u_diff = (ci_u_min - ci_u_full) / ci_u_full
    ci_l_diff = (ci_l_min - ci_l_full) / ci_l_full
    
    quality_diff.append([bench, time_saved, avg_diff, ci_u_diff, ci_l_diff])

quality_df = pd.DataFrame(quality_diff, columns=["Benchmark","Time Saved","Average Difference","CI Upper Difference","CI Lower Difference"])

min_config_res.to_csv("optimizer_results/min_config_res.csv",index=False)
full_config_res.to_csv("optimizer_results/full_config_res.csv",index=False)
quality_df.to_csv("optimizer_results/quality_df.csv",index=False)




