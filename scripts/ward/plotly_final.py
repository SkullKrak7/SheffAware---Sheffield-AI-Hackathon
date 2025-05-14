import pandas as pd
import geopandas as gpd
import plotly.graph_objects as go
from sklearn.preprocessing import StandardScaler, MinMaxScaler
from scipy.cluster.hierarchy import linkage, fcluster
from functools import reduce
import json

feature_files = {
    "tree_count": "data/ward/tree_count_per_ward.csv",
    "library_count": "data/ward/library_count_per_ward.csv",
    "camera_count": "data/ward/camera_count_per_ward.csv",
    "grit_bin_count": "data/ward/grit_bin_count_per_ward.csv",
    "crossing_count": "data/ward/crossing_count_per_ward.csv",
    "waste_access": "data/ward/waste_access_per_ward.csv",
    "drain_density": "data/ward/drain_density_per_ward.csv",
    "flood_risk": "data/ward/flood_risk_per_ward.csv"
}

dfs = [pd.read_csv(fname) for fname in feature_files.values()]
for i, name in enumerate(feature_files.keys()):
    dfs[i].columns = ["admin_name", name]
merged_df = reduce(lambda left, right: pd.merge(left, right, on="admin_name", how="left"), dfs)
merged_df["flood_safety"] = 1 - merged_df["flood_risk"]

with open("Sheffield_Wards.geojson") as f:
    geojson_dict = json.load(f)

features = list(feature_files.keys())
features[-1] = "flood_safety"
weights = [2, 1, 2, 1, 1, 1, 1, 2]
X_scaled = StandardScaler().fit_transform(merged_df[features])
X_scaled *= weights
linkage_matrix = linkage(X_scaled, method='ward')
merged_df["cluster"] = fcluster(linkage_matrix, t=3, criterion='maxclust')

means = merged_df.groupby("cluster")[features].mean()
order = means.mean(axis=1).sort_values(ascending=False).index
label_map = {order[0]: "Extensive", order[1]: "Mid", order[2]: "Low"}
merged_df["Category"] = merged_df["cluster"].map(label_map)

level_map = {"Low": 0, "Mid": 1, "Extensive": 2}
display_names = {
    "tree_count": "Trees",
    "library_count": "Libraries",
    "camera_count": "Cameras",
    "grit_bin_count": "Grit Bins",
    "crossing_count": "Crossings",
    "waste_access": "Waste Access Points",
    "drain_density": "Drain Nodes",
    "flood_risk": "Flood Risk"
}

traces = []
traces.append(go.Choroplethmap(
    geojson=geojson_dict,
    locations=merged_df["admin_name"],
    z=merged_df["Category"].map(level_map),
    featureidkey="properties.admin_name",
    colorscale=[[0, "red"], [0.5, "orange"], [1, "green"]],
    zmin=0,
    zmax=2,
    marker_line_color="black",
    marker_line_width=1,
    hovertext=merged_df.apply(lambda row: f"{row['admin_name']}<br>Cluster: {row['Category']}<br>(0=Low, 1=Mid, 2=Extensive)", axis=1),
    hoverinfo="text",
    visible=True,
    name="Hierarchical Clusters"
))

scaler = MinMaxScaler()
for feat, label in display_names.items():
    try:
        z = scaler.fit_transform(merged_df[[feat]]).flatten()
        merged_df[f"{feat}_norm"] = z
        hover = merged_df.apply(lambda row: f"{row['admin_name']}<br>{label}: {int(row[feat])}", axis=1)
        colorscale = [[0, "green"], [0.5, "orange"], [1, "red"]] if feat == "flood_risk" else [[0, "red"], [0.5, "orange"], [1, "green"]]
        traces.append(go.Choroplethmap(
            geojson=geojson_dict,
            locations=merged_df["admin_name"],
            z=merged_df[f"{feat}_norm"],
            featureidkey="properties.admin_name",
            colorscale=colorscale,
            zmin=0,
            zmax=1,
            marker_line_color="black",
            marker_line_width=1,
            hovertext=hover,
            hoverinfo="text",
            visible=False,
            name=label
        ))
    except:
        continue

buttons = []
for i in range(len(traces)):
    vis = [False] * len(traces)
    vis[i] = True
    buttons.append(dict(label=traces[i].name, method="update", args=[{"visible": vis}]))

fig = go.Figure(data=traces)
fig.update_layout(
    map=dict(style="carto-positron", center={"lat": 53.38, "lon": -1.47}, zoom=10.5),
    updatemenus=[dict(buttons=buttons, direction="right", showactive=True, type="buttons", x=0.5, xanchor="center", y=1.05, yanchor="bottom")],
    margin={"r": 0, "t": 40, "l": 0, "b": 0},
    title="Sheffield Ward-Level Feature-Based Cluster Map"
)

fig.show()
