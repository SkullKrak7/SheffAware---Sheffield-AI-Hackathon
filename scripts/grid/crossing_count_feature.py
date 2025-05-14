import pandas as pd
import geopandas as gpd
import numpy as np
from shapely.geometry import box

minx, miny = -1.60, 53.32
maxx, maxy = -1.40, 53.45
grid_size = 0.02
x_coords = np.arange(minx, maxx, grid_size)
y_coords = np.arange(miny, maxy, grid_size)
grid_cells = [box(x, y, x + grid_size, y + grid_size) for x in x_coords for y in y_coords]
grid = gpd.GeoDataFrame({"grid_id": [f"G{i:04d}" for i in range(len(grid_cells))]}, geometry=grid_cells, crs="EPSG:4326")

df = pd.read_csv("raw/School_Crossings.csv")
gdf = gpd.GeoDataFrame(df, geometry=gpd.points_from_xy(df["X"], df["Y"]), crs="EPSG:27700")
gdf = gdf.to_crs("EPSG:4326")
joined = gpd.sjoin(gdf, grid, how="inner", predicate="within")
counts = joined.groupby("grid_id").size().reset_index(name="crossing_count")
grid = grid.merge(counts, on="grid_id", how="left").fillna({"crossing_count": 0})
grid["crossing_count"] = grid["crossing_count"].astype(int)
grid[["grid_id", "crossing_count"]].to_csv("crossing_count_per_grid.csv", index=False)
