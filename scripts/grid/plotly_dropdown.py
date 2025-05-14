import pandas as pd
import geopandas as gpd
import plotly.express as px
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from functools import reduce

wards = gpd.read_file("Sheffield_Wards.geojson").to_crs("EPSG:4326")

features = [
    "tree_count", "library_count", "camera_count", "grit_bin_count",
    "crossing_count", "waste_access", "drain_density", "flood_risk"
]
dfs = [pd.read_csv(f"data/ward/{feat}_per_ward.csv") for feat in features]
merged = reduce(lambda left, right: pd.merge(left, right, on="admin_name", how="left"), [wards] + dfs).fillna(0)

merged["flood_safety"] = 1 - merged["flood_risk"]

feature_cols_raw = [
    "tree_count", "library_count", "camera_count", "grit_bin_count",
    "crossing_count", "waste_access", "drain_density", "flood_safety"
]
weights = [2, 1, 2, 1, 1, 1, 1, 2]
X_scaled = StandardScaler().fit_transform(merged[feature_cols_raw])
X_scaled *= weights

kmeans = KMeans(n_clusters=3, random_state=42)
merged["cluster"] = kmeans.fit_predict(X_scaled)

cluster_means = merged.groupby("cluster")[feature_cols_raw].mean()
rank_order = cluster_means.mean(axis=1).sort_values(ascending=False).index
label_map = {rank_order[0]: "Extensive", rank_order[1]: "Mid", rank_order[2]: "Low"}
merged["Category"] = merged["cluster"].map(label_map)

merged = merged.rename(columns={
    "tree_count": "Trees",
    "library_count": "Libraries",
    "camera_count": "Cameras",
    "grit_bin_count": "Grit Bins",
    "crossing_count": "Crossings",
    "waste_access": "Waste Access Points",
    "drain_density": "Drain Nodes",
    "flood_safety": "Flood Safety"
})

merged["Tooltip"] = (
    "Ward: " + merged["admin_name"] + "<br>" +
    "Category: " + merged["Category"] + "<br>" +
    "Trees: " + merged["Trees"].astype(str) + "<br>" +
    "Libraries: " + merged["Libraries"].astype(str) + "<br>" +
    "Cameras: " + merged["Cameras"].astype(str) + "<br>" +
    "Grit Bins: " + merged["Grit Bins"].astype(str) + "<br>" +
    "Crossings: " + merged["Crossings"].astype(str) + "<br>" +
    "Waste Access Points: " + merged["Waste Access Points"].astype(str) + "<br>" +
    "Drain Nodes: " + merged["Drain Nodes"].astype(str) + "<br>" +
    "Flood Safety: " + merged["Flood Safety"].astype(str)
)

geojson_dict = merged.set_index("admin_name").__geo_interface__

fig = px.choropleth_mapbox(
    merged,
    geojson=geojson_dict,
    locations="admin_name",
    color="Category",
    color_discrete_map={
        "Extensive": "green",
        "Mid": "orange",
        "Low": "red"
    },
    mapbox_style="carto-positron",
    center={"lat": 53.38, "lon": -1.47},
    zoom=10.5,
    opacity=0.45,
    hover_name="Tooltip",
    hover_data=None
)

fig.update_traces(marker_line_width=0.5, marker_line_color="gray")
fig.update_layout(
    title="Sheffield Ward-Level Clusters & Features",
    margin={"r": 0, "t": 40, "l": 0, "b": 0}
)

feature_display_names = [
    "Trees", "Libraries", "Cameras", "Grit Bins",
    "Crossings", "Waste Access Points", "Drain Nodes", "Flood Safety"
]

feature_scales = {label: "Reds" for label in feature_display_names}

dropdown_buttons = [
    dict(
        label=label,
        method="restyle",
        args=[{
               "color": [merged[label]],
               "colorscale": feature_scales[label],
               "colorbar.title": label
             }, [0]]
    )
    for label in feature_display_names
]

dropdown_buttons.insert(
    0,
    dict(
        label="Cluster (Extensive / Mid / Low)",
        method="restyle",
        args=[{
               "color": [merged["Category"]],
               "colorscale": None,
               "showscale": False
             }, [0]]
    )
)

fig.update_layout(
    updatemenus=[dict(
        buttons=dropdown_buttons,
        direction="down",
        x=0.01, xanchor="left",
        y=1.03, yanchor="top",
        showactive=True)]
)

fig.show()
