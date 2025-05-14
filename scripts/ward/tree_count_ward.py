import pandas as pd
import geopandas as gpd

wards = gpd.read_file("Sheffield_Wards.geojson").to_crs("EPSG:4326")
df = pd.read_csv("raw/Tree_Preservation_Order_Points.csv")
gdf = gpd.GeoDataFrame(df, geometry=gpd.points_from_xy(df["X"], df["Y"]), crs="EPSG:27700")
gdf = gdf.to_crs("EPSG:4326")
joined = gpd.sjoin(gdf, wards, how="inner", predicate="within")
counts = joined.groupby("admin_name").size().reset_index(name="tree_count")
wards = wards.merge(counts, on="admin_name", how="left")
wards["tree_count"] = wards["tree_count"].fillna(0).astype(int)
wards[["admin_name", "tree_count"]].to_csv("data/ward/tree_count_per_ward.csv", index=False)
