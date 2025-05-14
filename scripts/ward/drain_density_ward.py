import pandas as pd
import geopandas as gpd

wards = gpd.read_file("Sheffield_Wards.geojson").to_crs("EPSG:4326")
df = pd.read_csv("raw/Highway_Drain_Nodes.csv")
gdf = gpd.GeoDataFrame(df, geometry=gpd.points_from_xy(df["map_east"], df["map_north"]), crs="EPSG:27700")
gdf = gdf.to_crs("EPSG:4326")
joined = gpd.sjoin(gdf, wards, how="inner", predicate="within")
counts = joined.groupby("admin_name").size().reset_index(name="drain_density")
wards = wards.merge(counts, on="admin_name", how="left")
wards["drain_density"] = wards["drain_density"].fillna(0).astype(int)
wards[["admin_name", "drain_density"]].to_csv("data/ward/drain_density_per_ward.csv", index=False)
