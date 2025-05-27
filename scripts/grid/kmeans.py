import pandas as pd
import geopandas as gpd
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
import plotly.express as px

grid = gpd.read_file("sheffield_grid.geojson")
features = pd.read_csv("grid_features.csv")
grid = grid.merge(features, on="grid_id", how="left").fillna(0)
grid["flood_safety"] = 1 - grid["flood_risk"]

feature_cols = [
    "tree_count", "library_count", "camera_count", "grit_bin_count",
    "crossing_count", "waste_access", "drain_density", "flood_safety"
]

scaler = StandardScaler()
scaled_features = scaler.fit_transform(grid[feature_cols])
weights = [2, 1, 2, 1, 1, 1, 1, 2]
scaled_features *= weights

kmeans = KMeans(n_clusters=3, random_state=42)
grid["cluster"] = kmeans.fit_predict(scaled_features)

means = grid.groupby("cluster")[feature_cols].mean()
ranking = means.mean(axis=1).sort_values(ascending=False)
name_map = {ranking.index[0]: "Extensive", ranking.index[1]: "Mid", ranking.index[2]: "Low"}
grid["cluster_label"] = grid["cluster"].map(name_map)

grid = grid.to_crs(epsg=4326)
geojson_dict = grid.set_index("grid_id").__geo_interface__

fig = px.choropleth_mapbox(
    grid,
    geojson=geojson_dict,
    locations="grid_id",
    color="cluster_label",
    color_discrete_map={
        "Extensive": "green",
        "Mid": "orange",
        "Low": "red"
    },
    mapbox_style="open-street-map",
    center={"lat": 53.38, "lon": -1.48},
    zoom=12,
    opacity=0.35,
    hover_name="grid_id",
    hover_data={col: True for col in feature_cols}
)

fig.update_traces(marker_line_width=0.4, marker_line_color="lightgray")
fig.update_layout(
    title="Grid Service Level Clustering in Sheffield (KMeans)",
    margin={"r": 0, "t": 40, "l": 0, "b": 0}
)

fig.show()
