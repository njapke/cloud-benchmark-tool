#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Aug 29 13:25:24 2022

@author: njapke
"""

import numpy as np
import pandas as pd
import json
import stat_functions as st

# read data
df = pd.read_csv("experiment.csv", index_col="m_id")

# load results
inst_data = np.load("arrays.npz")
with open("min_config.json","r") as f:
    min_conf = json.load(f)

# get all benchmarks
benchmarks = np.array(df["b_name"].drop_duplicates())

# get setup variables
bed_setup = df["bed_setup"][1]
it_setup = df["it_setup"][1]
sr_setup = df["sr_setup"][1]
ir_setup = df["ir_setup"][1]
df.drop(columns=["bed_setup", "it_setup", "sr_setup", "ir_setup"], inplace=True)

# get density of full and min conf, calculate kl divergence, transform into accuracy
dens_full = {}
dens_min = {}
kl = np.zeros(len(benchmarks))
accuracy = np.zeros(len(benchmarks))
for b in range(len(benchmarks)):
    bench = benchmarks[b]
    bench_min_conf = min_conf[bench]
    
    full_data = df[df["b_name"] == bench]
    min_data = df[(df["b_name"] == bench)
                  & (df["ir_pos"] <= bench_min_conf[0])
                  & (df["sr_pos"] <= bench_min_conf[1])
                  & (df["it_pos"] <= bench_min_conf[2])
                  & (df["bed_pos"] <= bench_min_conf[3])]
    
    upper = full_data["ns_per_op"].max()
    lower = full_data["ns_per_op"].min()
    
    # histograms are kinda bad for kl estimation (sensitive to bin size, can produce almost any result)
    # replace with different technique to estimate kl
    dens_full[bench] = np.histogram(np.array(full_data["ns_per_op"]), bins=10, range=(lower,upper), density=True)
    dens_min[bench] = np.histogram(np.array(min_data["ns_per_op"]), bins=10, range=(lower,upper), density=True)
    bin_width = dens_full[bench][1][1] - dens_full[bench][1][0]
    
    kl[b] = st.kl_divergence(dens_full[bench][0]*bin_width, dens_min[bench][0]*bin_width)
    # kl[b] = st.better_kl(np.array(full_data["ns_per_op"]), np.array(min_data["ns_per_op"]))
    
    accuracy[b] = 2**(-kl[b])






