#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Aug 30 19:49:22 2022

@author: njapke
"""

import numpy as np
from scipy.interpolate import interp1d
import matplotlib.pyplot as plt

# Initialize RNG
rng = np.random.default_rng(42)

n = 100
x = np.sort(rng.normal(0, 1, n))

knots = (np.arange(0,n,1) + 0.5) / n
P_c = interp1d(x, knots, fill_value=(0,1), bounds_error=False)

x_new = np.linspace(-3,3,1000)

plt.plot(x_new, P_c(x_new), '-')
plt.show()



# x = np.linspace(0, 10, num=11, endpoint=True)
# y = np.cos(-x**2/9.0)
# f = interp1d(x, y)
# f2 = interp1d(x, y, kind='cubic')

# xnew = np.linspace(0, 10, num=41, endpoint=True)
# plt.plot(x, y, 'o', xnew, f(xnew), '-', xnew, f2(xnew), '--')
# plt.legend(['data', 'linear', 'cubic'], loc='best')
# plt.show()






