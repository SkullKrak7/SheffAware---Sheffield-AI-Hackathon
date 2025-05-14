import pandas as pd
from functools import reduce

feature_files = [
    "tree_count_per_grid.csv",
    "library_count_per_grid.csv",
    "camera_count_per_grid.csv",
    "grit_bin_count_per_grid.csv",
    "crossing_count_per_grid.csv",
    "waste_access_per_grid.csv",
    "drain_density_per_grid.csv",
    "flood_risk_per_grid.csv"
]

dfs = [pd.read_csv(f) for f in feature_files]
merged = reduce(lambda left, right: pd.merge(left, right, on="grid_id", how="outer"), dfs)
merged.fillna(0, inplace=True)

for col in merged.columns:
    if col != "grid_id":
        merged[col] = merged[col].astype(int)

merged.to_csv("grid_features.csv", index=False)
