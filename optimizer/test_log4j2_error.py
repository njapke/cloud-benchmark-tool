#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Mar 13 15:46:09 2023

@author: njapke
"""

import pandas as pd
import numpy as np

df = pd.read_csv("laaber_preprocessed/laaber_log4j2.csv", index_col="m_id")

benchmarks = np.array(df["b_name"].drop_duplicates())

broken_benchmarks = []
for b in benchmarks:
    df_b = df[df["b_name"] == b]
    if len(df_b) != 500:
        print(b)
        print(str(len(df_b)))
        broken_benchmarks.append(b)

broken_df = pd.DataFrame(broken_benchmarks, columns=["b_name"])

broken_df.to_csv("laaber_preprocessed/laaber_log4j2_list_of_broken_benchmarks.csv", index=False)

# broken_filter = df["b_name"].isin(broken_benchmarks)

# df_f = df[~broken_filter]

# df_f.to_csv("laaber_preprocessed/laaber_log4j2_filtered.csv")