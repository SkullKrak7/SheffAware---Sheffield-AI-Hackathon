import geopandas as gpd
import numpy as np
from shapely.geometry import box

minx, miny = -1.60, 53.32
maxx, maxy = -1.40, 53.45
grid_size = 0.02

x_coords = np.arange(minx, maxx, grid_size)
y_coords = np.arange(miny, maxy, grid_size)
grid_cells = [box(x, y, x + grid_size, y + grid_size) for x in x_coords for y in y_coords]

grid = gpd.GeoDataFrame(
    {"grid_id": [f"G{i:04d}" for i in range(len(grid_cells))]},
    geometry=grid_cells,
    crs="EPSG:4326"
)

grid.to_file("sheffield_grid.geojson", driver="GeoJSON")
