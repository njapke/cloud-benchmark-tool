#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Feb  2 11:46:59 2023

@author: njapke
"""

#%%
import numpy as np
#import pandas as pd
import stat_functions as st
import time
from scipy.stats.mstats import mjci

# Initialize RNG
rng = np.random.default_rng(42)

data = rng.normal(5, 2, 100)

print("Timing mean t")
start = time.time()
meant = st.ci_bootstrap_mean_t(data)
end = time.time()

time_meant = end - start
print("Finished after " + str(time_meant) + " seconds")

print("Timing median t")
start = time.time()
mediant = st.ci_bootstrap_median_t(data)
end = time.time()

time_mediant = end - start
print("Finished after " + str(time_mediant) + " seconds")


#%%
it = 10_000
orig_median = np.median(data)
# orig_std_dev = np.sqrt(se_bootstrap_median(data, 2000))
orig_std_dev = mjci(data, prob=[0.5])

samples = rng.choice(data, (it, len(data)))
# Bootstrap medians
bs_medians = np.median(samples, axis=1)


