import pandas as pd
import geopandas as gpd
import numpy as np
from shapely.geometry import box

# Step 1: Regenerate the 500m grid
minx, miny = -1.60, 53.32
maxx, maxy = -1.40, 53.45
grid_size = 0.02
x_coords = np.arange(minx, maxx, grid_size)
y_coords = np.arange(miny, maxy, grid_size)

grid_cells = [box(x, y, x + grid_size, y + grid_size) for x in x_coords for y in y_coords]
grid = gpd.GeoDataFrame({'grid_id': [f'G{i:04d}' for i in range(len(grid_cells))]}, geometry=grid_cells, crs="EPSG:4326")

# Step 2: Load flood risk CSV and merge
flood_risk = pd.read_csv(r"C:\Users\saika\Downloads\AI Hackathon\flood_risk_per_grid.csv")
grid = grid.merge(flood_risk, on="grid_id", how="left")
grid["flood_risk"] = grid["flood_risk"].fillna(0).astype(int)

# Step 3: Load ward boundaries
wards = gpd.read_file(r"C:\Users\saika\Downloads\Sheffield_Wards.geojson").to_crs("EPSG:4326")

# Step 4: Spatial join: grid → ward
joined = gpd.sjoin(grid, wards, how="inner", predicate="intersects")

# Step 5: Ward-level flood risk = max across joined grid cells
flood_risk_per_ward = joined.groupby("admin_name")["flood_risk"].max().reset_index()

# Step 6: Save result
flood_risk_per_ward.to_csv("flood_risk_per_ward.csv", index=False)
print("✅ flood_risk_per_ward.csv saved.")
