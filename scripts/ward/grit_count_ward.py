import pandas as pd
import geopandas as gpd

wards = gpd.read_file("Sheffield_Wards.geojson").to_crs("EPSG:4326")
df = pd.read_csv("raw/Grit_bins.csv")
gdf = gpd.GeoDataFrame(df, geometry=gpd.points_from_xy(df["X"], df["Y"]), crs="EPSG:27700")
gdf = gdf.to_crs("EPSG:4326")
joined = gpd.sjoin(gdf, wards, how="inner", predicate="within")
counts = joined.groupby("admin_name").size().reset_index(name="grit_bin_count")
wards = wards.merge(counts, on="admin_name", how="left")
wards["grit_bin_count"] = wards["grit_bin_count"].fillna(0).astype(int)
wards[["admin_name", "grit_bin_count"]].to_csv("data/ward/grit_bin_count_per_ward.csv", index=False)
