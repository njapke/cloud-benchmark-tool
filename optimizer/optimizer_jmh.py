#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Aug 31 14:42:38 2022

@author: njapke
"""

import os
from pathlib import Path
import numpy as np
import pandas as pd
import stat_functions as st
import time

class ConfigCounter:
    def __init__(self, fork, it):
        self.fork = fork
        self.it = it
        self.max = fork*it
        self.current = -1

    def __iter__(self):
        return self

    def __next__(self):
        self.current += 1
        if self.current < self.max:
            it = self.current % self.it
            r = self.current // self.it
            fork = r % self.fork
            return (fork+1,it+1)
        raise StopIteration

data_path = "/home/njapke/TU_Berlin/Doktor/Paper Projects/uoptime/git/cloud-benchmark-tool/optimizer/laaber_preprocessed"

# get sorted list of all files
files = list(os.walk(data_path))[0][2]
files.sort()

list_of_instability_funcs = [(st.cv, np.mean, st.ci_bootstrap_mean_p),
                             (st.cv, np.median, st.ci_bootstrap_median_p),
                             (st.rmad, np.mean, st.ci_bootstrap_mean_p),
                             (st.rmad, np.median, st.ci_bootstrap_median_p),
                             (st.rciw_mean_p, np.mean, st.ci_bootstrap_mean_p),
                             (st.rciw_mean_t, np.mean, st.ci_bootstrap_mean_t),
                             (st.rciw_median_p, np.median, st.ci_bootstrap_median_p),]
                             # (st.rciw_median_t, np.median, st.ci_bootstrap_median_t),]

exec_times = []
for file in files:
    print("Processing "+file)
    # read data
    df = pd.read_csv(data_path+"/"+file, index_col="m_id")
    
    # get all benchmarks
    benchmarks = np.array(df["b_name"].drop_duplicates())
    
    # get setup variables
    it_setup = df["it_setup"][1]
    fork_setup = df["fork_setup"][1]
    df.drop(columns=["it_setup", "fork_setup"], inplace=True)
    
    for inst_funcs in list_of_instability_funcs:
        print("Using instability function setup "+str(inst_funcs))
        # Select instability measure and CI method
        calc_inst = inst_funcs[0]
        calc_avg = inst_funcs[1]
        calc_ci = inst_funcs[2]
        
        # Select threshold to mark benchmarks as unstable
        ts = 0.01
        
        # Time execution for min setup
        start = time.time()
        
        res = []
        # ir is always 3
        for b in range(len(benchmarks)):
            bench = benchmarks[b]
            for c in ConfigCounter(fork_setup,it_setup): # fork, it
                if c[0]*c[1] < 3:
                    continue
                dft = df[(df["b_name"] == bench)
                          & (df["fork_pos"] <= c[0])
                          & (df["it_pos"] <= c[1])]
                data = np.array(dft["ns_per_op"])
                
                inst = calc_inst(data, it=10000) # instability
                
                time_bound = c[0]*c[1] # time per instance in seconds
                
                avg = calc_avg(data)
                
                ci = calc_ci(data, it=10000)
                
                res.append([bench, c, inst, time_bound, avg, min(ci), max(ci)])
        
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
        full_config_res = result_df[result_df["Config"] == (fork_setup,it_setup)]
        
        # Print execution time
        end = time.time()
        curr_exec_time = end - start
        print("Finished after "+str(curr_exec_time)+" seconds")
        exec_times.append([file, inst_funcs, curr_exec_time])
        
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
        
        # create result folder
        proj_name = file[:-4]
        method_name = calc_inst.__name__+"__"+calc_avg.__name__+"__"+calc_ci.__name__
        full_result_path = "optimizer_results/"+proj_name+"/"+method_name
        Path(full_result_path).mkdir(parents=True, exist_ok=True)
        
        # write results
        min_config_res.to_csv(full_result_path+"/min_config_res.csv",index=False)
        full_config_res.to_csv(full_result_path+"/full_config_res.csv",index=False)
        quality_df.to_csv(full_result_path+"/quality_df.csv",index=False)

exec_times_df = pd.DataFrame(exec_times, columns=["File","Instability Functions","Execution Time"])
exec_times_df.to_csv("optimizer_results/exec_times_df.csv",index=False)
print("Finished")
