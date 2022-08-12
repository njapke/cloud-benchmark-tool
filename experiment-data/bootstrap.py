#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Aug  9 23:57:58 2022

@author: njapke
"""

import numpy as np

rng = np.random.default_rng()

# simulate mean
def simulate_mean(data):
    res = np.array([])
    for _ in range(len(data)):
        idx = rng.integers(0,len(data))
        res = np.append(res, data[idx])
    return res.mean()

def bootstrap_distribution(data, it = 1000):
    res = np.array([])
    for i in range(it):
        res = np.append(res, simulate_mean(data))
    res.sort()
    return res