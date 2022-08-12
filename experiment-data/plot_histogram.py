#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Aug  9 14:12:24 2022

@author: njapke
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import bootstrap as bt

# variables
bench_name = "BenchmarkScanComments/1MValidUtf8"

# read file
df = pd.read_csv("ir2.csv", index_col="m_id")

# select setup
# df = df[(df["bed"] == "2s") & (df["iterations"] == 1) & (df["sr"] == 1) & (df["ir"] == 1)]
df = df[(df["bed"] == "5s") & (df["iterations"] == 5) & (df["sr"] == 3)]

# select benchmark
df = df[df["b_name"] == bench_name]

# bootstrap distribution
bs_dist = bt.bootstrap_distribution(np.array(df["ns_per_op"]))
mean = bs_dist.mean() # mean
p = np.percentile(bs_dist, [2.5, 97.5]) # 95% CI bounds

# plot
fig = plt.figure(figsize=(14,4))
ax = plt.axes(xlim=(bs_dist.min(), bs_dist.max()))

ax.hist(bs_dist, bins=30)
#ax.vlines(mean, 0, 50, colors=["red"])
#ax.vlines(p, 0, 50, colors=["orange", "orange"])
ax.axline((mean,0), (mean,1), color="red")
ax.axline((p[0],0), (p[0],1), color="orange")
ax.axline((p[1],0), (p[1],1), color="orange")

