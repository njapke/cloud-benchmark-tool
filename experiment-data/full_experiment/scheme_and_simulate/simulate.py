#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Aug 29 13:25:24 2022

@author: njapke
"""

import numpy as np
import pandas as pd
import json
import instability as inst
import scipy as sp

def kl_divergence(de1, de2):
    return sp.special.rel_entr(de1, de2).sum()

# read data
df = pd.read_csv("experiment.csv", index_col="m_id")

# load results
inst_data = np.load("arrays.npz")
with open("min_config.json","r") as f:
    min_conf = json.load(f)

# get all benchmarks
benchmarks = list(set(df["b_name"]))

# get setup variables
bed_setup = df["bed_setup"][1]
it_setup = df["it_setup"][1]
sr_setup = df["sr_setup"][1]
ir_setup = df["ir_setup"][1]
df.drop(columns=["bed_setup", "it_setup", "sr_setup", "ir_setup"], inplace=True)

# get density of full and min conf, calculate kl divergence, transform into accuracy
bench = benchmarks[1]
bench_min_conf = min_conf[bench]

full_data = df[df["b_name"] == bench]
min_data = df[(df["b_name"] == bench)
              & (df["ir_pos"] <= bench_min_conf[0])
              & (df["sr_pos"] <= bench_min_conf[1])
              & (df["it_pos"] <= bench_min_conf[2])
              & (df["bed_pos"] <= bench_min_conf[3])]

dens_full = np.histogram(np.array(full_data["ns_per_op"]), bins=10, range=(200.0,350.0), density=True)
dens_min = np.histogram(np.array(min_data["ns_per_op"]), bins=10, range=(200.0,350.0), density=True)
bin_width = dens_full[1][1] - dens_full[1][0]

kl = kl_divergence(dens_full[0]*bin_width, dens_min[0]*bin_width)

accuracy = 2**(-kl)






