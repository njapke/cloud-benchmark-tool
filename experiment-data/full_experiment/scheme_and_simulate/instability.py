#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Aug 29 13:13:19 2022

@author: njapke
"""

import numpy as np

# Initialize RNG
rng = np.random.default_rng()

# Coefficient of Variation
def cv(data):
    m = data.mean()
    return np.sqrt(1/(len(data)) * ((data - m)**2).sum() ) / m

# Relative Median Absolute Deviation
def rmad(data):
    m = np.median(data)
    return np.median(np.absolute(data - m)) / m

# Resample mean estimates for bootstrap
def simulate_mean(data):
    res = np.array([])
    for _ in range(len(data)):
        idx = rng.integers(0,len(data))
        res = np.append(res, data[idx])
    return res.mean()

# Calculate bootstrap distribution of simulated means
def bootstrap_distribution(data, it = 1000): # TODO optimize
    res = np.array([])
    for i in range(it):
        res = np.append(res, simulate_mean(data))
    res.sort()
    return res

# Relative Confidence Interval Width
def rciw(data, it = 1000): # 10_000 is better, but takes ages
    bs_dist = bootstrap_distribution(data, it) # TODO optimize
    p = np.percentile(bs_dist, [2.5, 97.5]) # 95% CI bounds
    return np.absolute(p[1] - p[0]) / data.mean()

