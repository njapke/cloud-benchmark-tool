#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Aug 29 13:13:19 2022

@author: njapke
"""

import numpy as np
import scipy as sp
from scipy.interpolate import interp1d

# Initialize RNG
rng = np.random.default_rng(42)

# Estimator based on paper "Kullback-Leibler divergence estimation of continuous distributions"
def better_kl(d1, d2):
    n1 = len(d1)
    knots1 = (np.arange(0,n1,1) + 0.5) / n1
    P = interp1d(d1, knots1, fill_value=(0,1), bounds_error=False)
    
    n2 = len(d2)
    knots2 = (np.arange(0,n2,1) + 0.5) / n2
    Q = interp1d(d2, knots2, fill_value=(0,1), bounds_error=False)
    
    diff1 = np.diff(d1).min()
    diff2 = np.diff(d2).min()
    e = min(diff1, diff2) / 2
    
    return np.log( (P(d2) - P(d2 - e)) / (Q(d2) - Q(d2 - e)) ).sum() / n2

# Kullback-Leibler divergence
def kl_divergence(de1, de2):
    return sp.special.rel_entr(de1, de2).sum()

# Coefficient of Variation
def cv(data):
    m = data.mean()
    return np.sqrt(1/(len(data)) * ((data - m)**2).sum() ) / m

# Relative Median Absolute Deviation
def rmad(data):
    m = np.median(data)
    return np.median(np.absolute(data - m)) / m

# Relative Confidence Interval Width (mean, bootstrap)
def rciw(data, it = 10000, cl = 99):
    p = ci_bootstrap(data, it, cl)
    return np.absolute(p[1] - p[0]) / data.mean()

# CI bounds of mean with bootstrap
def ci_bootstrap(data, it = 10000, cl = 99):
    bs_dist = np.mean(rng.choice(data, (it, len(data))), axis=1)
    
    lower = (100 - cl) / 2
    upper = cl + lower
    return np.percentile(bs_dist, [lower, upper]) # CI bounds

# Intersection over Union for intervals
def iou(i1, i2):
    min1 = min(i1)
    max1 = max(i1)
    min2 = min(i2)
    max2 = max(i2)
    
    lower_min = min(min1, min2)
    higher_min = max(min1, min2)
    lower_max = min(max1, max2)
    higher_max = max(max1, max2)
    
    length_inner = abs(lower_max - higher_min) if higher_min < lower_max else 0
    length_outer = abs(higher_max - lower_min)
    
    return length_inner / length_outer








