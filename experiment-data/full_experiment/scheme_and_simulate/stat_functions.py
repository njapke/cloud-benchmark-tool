#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Aug 29 13:13:19 2022

@author: njapke
"""

import numpy as np
import scipy as sp
from scipy.interpolate import interp1d
from scipy.special import betainc
from scipy.special import beta
#from scipy.special import factorial

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

# Relative Confidence Interval Width (mean, percentile bootstrap)
def rciw_mean_p(data, it = 10000, cl = 99):
    p = ci_bootstrap_mean_p(data, it, cl)
    return np.absolute(p[1] - p[0]) / data.mean()

# CI bounds of mean with percentile bootstrap
def ci_bootstrap_mean_p(data, it = 10000, cl = 99):
    bs_dist = np.mean(rng.choice(data, (it, len(data))), axis=1)
    
    lower = (100 - cl) / 2
    upper = cl + lower
    return np.percentile(bs_dist, [lower, upper]) # CI bounds

# Relative Confidence Interval Width (median, percentile bootstrap)
def rciw_median_p(data, it = 10000, cl = 99):
    p = ci_bootstrap_mean_p(data, it, cl)
    return np.absolute(p[1] - p[0]) / np.median(data)

# CI bounds of median with percentile bootstrap
def ci_bootstrap_median_p(data, it = 10000, cl = 99):
    bs_dist = np.median(rng.choice(data, (it, len(data))), axis=1)
    
    lower = (100 - cl) / 2
    upper = cl + lower
    return np.percentile(bs_dist, [lower, upper]) # CI bounds

# Relative Confidence Interval Width (mean, studentized bootstrap)
def rciw_mean_t(data, it = 10000, cl = 99):
    p = ci_bootstrap_mean_t(data, it, cl)
    return np.absolute(p[1] - p[0]) / data.mean()

# CI bounds of mean with studentized bootstrap
def ci_bootstrap_mean_t(data, it = 10000, cl = 99):
    orig_mean = np.mean(data)
    orig_std_dev = np.sqrt(np.sum(np.power((data - orig_mean), 2)) / (len(data)-1))
    
    samples = rng.choice(data, (it, len(data)))
    # Bootstrap means
    bs_means = np.mean(samples, axis=1)
    # Bootstrap standard deviation
    bs_std_dev = np.sqrt(np.sum(np.power((samples.T - bs_means).T, 2), axis=1) / (len(data)-1))
    bs_std_dev[bs_std_dev == 0] = 1
    
    # Studentized bootstrap distribution
    t_star = (bs_means - orig_mean) / (bs_std_dev / np.sqrt(len(data)))
    #cond = np.logical_or(np.logical_or(t_star == np.inf, t_star == -np.inf), t_star == np.nan)
    cond = np.logical_not(np.isfinite(t_star))
    t_star[cond] = 0
    
    lower = (100 - cl) / 2
    upper = cl + lower
    p = np.percentile(t_star, [lower, upper])
    return (orig_mean - p[1]*orig_std_dev/np.sqrt(len(data)), orig_mean - p[0]*orig_std_dev/np.sqrt(len(data))) # CI bounds

# Relative Confidence Interval Width (mean, studentized bootstrap)
def rciw_median_t(data, it = 10000, cl = 99):
    p = ci_bootstrap_median_t(data, it, cl)
    return np.absolute(p[1] - p[0]) / data.mean()

# CI bounds of median with studentized bootstrap
def ci_bootstrap_median_t(data, it = 10000, cl = 99):
    orig_median = np.median(data)
    orig_std_dev = np.sqrt(var_median_maritz_jarrett(data))
    
    samples = rng.choice(data, (it, len(data)))
    # Bootstrap medians
    bs_medians = np.median(samples, axis=1)
    # Bootstrap standard deviation
    bs_std_dev = np.sqrt(np.array([var_median_maritz_jarrett(x) for x in samples]))
    bs_std_dev[bs_std_dev == 0] = 1
    
    # Studentized bootstrap distribution
    t_star = (bs_medians - orig_median) / bs_std_dev
    #cond = np.logical_or(np.logical_or(t_star == np.inf, t_star == -np.inf), t_star == np.nan)
    cond = np.logical_not(np.isfinite(t_star))
    t_star[cond] = 0
    
    lower = (100 - cl) / 2
    upper = cl + lower
    p = np.percentile(t_star, [lower, upper])
    return (orig_median - p[1]*orig_std_dev, orig_median - p[0]*orig_std_dev) # CI bounds

# Bootstrap standard error for the median
def se_bootstrap_median(data, it = 10000):
    bs_dist = np.median(rng.choice(data, (it, len(data))), axis=1)
    
    bs_mean = np.mean(bs_dist)
    
    return np.sqrt(np.sum(np.power((bs_dist - bs_mean), 2)) / (it-1))

# Variance of sample median by Maritz-Jarrett, can be used to get standard error
def var_median_maritz_jarrett(data):
    n = len(data)
    m = n//2
    if (n%2) == 0: # even
        i_array = np.array(range(n)) + 1
        Ui = betainc(m,m,i_array/n) - betainc(m,m,(i_array-1)/n)
        
        B1n = data @ Ui
        B2n = np.power(data,2) @ Ui
        
        # Calculate Cn
        left = np.power(i_array/n,m) - np.power((i_array-1)/n,m)
        right = np.flip(left).reshape((1,n))
        left = left.reshape((n,1))
        
        #factor = factorial(2*m)/(factorial(m)**2)
        factor = (2*m+1) * beta(m+1,m+1)
        if factor <= 0:
            factor = 1e-20 # small but non-zero factor for numerical stability
        
        Uij = factor * np.triu(left @ right, 1) # upper triangle, no diagonal
        diag = Ui - factor * ( np.power(i_array/n,m) * np.power((n-i_array)/n,m) + np.power((i_array-1)/n,m) * np.power((n+1-i_array)/n,m) - 2 * np.power((i_array-1)/n,m) * np.power((n-i_array)/n,m) )
        np.fill_diagonal(Uij, diag)
        
        Cn = data.reshape((1,n)) @ Uij @ data.reshape((n,1)) # Cn is (1,1) matrix
        
        res = (B2n + Cn[0,0]) / 2 - B1n**2
        
        if res < 0:
            res = 0
        
        return res
    else: # odd
        i_array = np.array(range(n)) + 1
        Wi = betainc(m+1,m+1,i_array/n) - betainc(m+1,m+1,(i_array-1)/n)
        
        A1n = data @ Wi
        A2n = np.power(data,2) @ Wi
        
        res = A2n - A1n**2
        
        if res < 0:
            res = 0
        
        return res

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








