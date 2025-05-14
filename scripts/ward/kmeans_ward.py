import pandas as pd
import geopandas as gpd
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
import plotly.express as px
from functools import reduce

wards = gpd.read_file("Sheffield_Wards.geojson").to_crs("EPSG:4326")

features = [
    "tree_count", "library_count", "camera_count", "grit_bin_count",
    "crossing_count", "waste_access", "drain_density", "flood_risk"
]

dfs = [pd.read_csv(f"data/ward/{feat}_per_ward.csv") for feat in features]
merged = reduce(lambda left, right: pd.merge(left, right, on="admin_name", how="left"), [wards] + dfs)
merged.fillna(0, inplace=True)
merged["flood_safety"] = 1 - merged["flood_risk"]

feature_cols = [
    "tree_count", "library_count", "camera_count", "grit_bin_count",
    "crossing_count", "waste_access", "drain_density", "flood_safety"
]

scaler = StandardScaler()
X_scaled = scaler.fit_transform(merged[feature_cols])
weights = [2, 1, 2, 1, 1, 1, 1, 2]
X_scaled *= weights

kmeans = KMeans(n_clusters=3, random_state=42)
merged["cluster"] = kmeans.fit_predict(X_scaled)

means = merged.groupby("cluster")[feature_cols].mean()
order = means.mean(axis=1).sort_values(ascending=False).index
label_map = {order[0]: "Extensive", order[1]: "Mid", order[2]: "Low"}
merged["cluster_label"] = merged["cluster"].map(label_map)

geojson_dict = merged.set_index("admin_name").__geo_interface__

fig = px.choropleth_mapbox(
    merged,
    geojson=geojson_dict,
    locations="admin_name",
    color="cluster_label",
    color_discrete_map={"Extensive": "green", "Mid": "orange", "Low": "red"},
    mapbox_style="carto-positron",
    center={"lat": 53.38, "lon": -1.47},
    zoom=10.5,
    opacity=0.4,
    hover_name="admin_name",
    hover_data={col: True for col in feature_cols}
)

fig.update_traces(marker_line_width=0.4, marker_line_color="gray")
fig.update_layout(title="Ward-Level Urban Resource Clustering", margin={"r": 0, "t": 40, "l": 0, "b": 0})
fig.show()
