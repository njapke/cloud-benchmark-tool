#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Aug 15 14:11:12 2022

@author: njapke
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# prevent figures from showing (as they are saved)
plt.ioff()

# variables
output_folder = "plots_var/"

# read data
df = pd.read_csv("experiment.csv", index_col="m_id")

# get all benchmarks
benchmarks = set(df["b_name"])


# for bench in benchmarks:
#     print("Processing "+bench)
#     dft = df[df["b_name"] == bench]
#     # calc var
#     std = np.zeros((3,3,4))
#     #ir
#     for i in range(1,4):
#         #sr
#         for j in range(1,4):
#             tmp = dft[(dft["ir_pos"] == i) & (dft["sr_pos"] == j)]
#             data = np.array(tmp["ns_per_op"])
#             for k in range(2,6):
#                 std[i-1,j-1,k-2] = np.sqrt(1/(k-1) * ((data[:k] - data[:k].mean())**2).sum() )
         
bench = "BenchmarkParseLiteralStringValid/10ValidUtf8"       
dft = df[df["b_name"] == bench]
# calc var
std = np.zeros((3,3,4))
#ir
for i in range(1,4):
    #sr
    for j in range(1,4):
        tmp = dft[(dft["ir_pos"] == i) & (dft["sr_pos"] == j)]
        data = np.array(tmp["ns_per_op"])
        for k in range(2,6):
            std[i-1,j-1,k-2] = np.sqrt(1/(k-1) * ((data[:k] - data[:k].mean())**2).sum() )
    
    # plot
    fig = plt.figure(figsize=(14,4))
    ax = plt.axes()
    ax.set_xticks([0,1,2,3], [2,3,4,5])

    for i in range(3):
        if i == 1:
            continue
        for j in range(3):
            ax.plot(std[i,j,:], alpha=1.0)

    ax.set_title('Std of ns per op for different it for benchmark ' + bench)
    ax.set_xlabel('iterations')
    ax.set_ylabel('Std ns per op')

    fig.savefig(output_folder+"test.png")
    plt.close(fig)




