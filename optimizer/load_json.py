#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Mar 14 22:46:38 2023

@author: njapke
"""

import json

path = "/home/njapke/TU_Berlin/Doktor/Paper Projects/uoptime/replication_package_laaber_tcp/data/executions/RxJava/results/json/rxjava-1_3_8-jmh121-3.json"

with open(path) as f:
    j = json.load(f)
    # try:
    #     j = json.load(f)
    # except json.JSONDecodeError:
    #     print("Encountered JSONDecodeError")