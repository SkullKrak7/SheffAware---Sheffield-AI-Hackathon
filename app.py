import streamlit as st
import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.graph_objects as go
from sklearn.preprocessing import StandardScaler, MinMaxScaler
from scipy.cluster.hierarchy import linkage, dendrogram, fcluster
from sklearn.decomposition import PCA
import json
from functools import reduce

# Streamlit setup
st.set_page_config(page_title="SheffAware Ward-Level Clustering", layout="wide")
st.title("SheffAware Ward-Level Clustering Analysis")

# Data load
base_path = "data/ward"
feature_files = {
    "tree_count": f"{base_path}/tree_count_per_ward.csv",
    "library_count": f"{base_path}/library_count_per_ward.csv",
    "camera_count": f"{base_path}/camera_count_per_ward.csv",
    "grit_bin_count": f"{base_path}/grit_bin_count_per_ward.csv",
    "crossing_count": f"{base_path}/crossing_count_per_ward.csv",
    "waste_access": f"{base_path}/waste_access_per_ward.csv",
    "drain_density": f"{base_path}/drain_density_per_ward.csv",
    "flood_risk": f"{base_path}/flood_risk_per_ward.csv"
}

dfs = [pd.read_csv(path) for path in feature_files.values()]
for df, name in zip(dfs, feature_files.keys()):
    df.columns = ["admin_name", name]
merged = reduce(lambda left, right: pd.merge(left, right, on="admin_name", how="left"), dfs)
merged["flood_safety"] = 1 - merged["flood_risk"]

# Clustering
features = list(feature_files.keys())
features[-1] = "flood_safety"
weights = [2, 1, 2, 1, 1, 1, 1, 2]
X_scaled = StandardScaler().fit_transform(merged[features])
X_scaled *= weights
linkage_matrix = linkage(X_scaled, method="ward")
merged["cluster"] = fcluster(linkage_matrix, t=3, criterion="maxclust")

# Assign labels
means = merged.groupby("cluster")[features].mean()
order = means.mean(axis=1).sort_values(ascending=False).index
label_map = {order[0]: "Extensive", order[1]: "Mid", order[2]: "Low"}
merged["Category"] = merged["cluster"].map(label_map)

# Sidebar
st.sidebar.header("Info")
st.sidebar.write("Clustering based on hierarchical Ward’s method.")
st.sidebar.write("Choropleth uses fixed 3-cluster result (Low, Mid, Extensive).")

# Dendrogram
st.header("Hierarchical Clustering Dendrogram")
fig1, ax1 = plt.subplots(figsize=(12, 6))
dendrogram(linkage_matrix, labels=merged["admin_name"].values, leaf_rotation=90, leaf_font_size=8, ax=ax1)
ax1.set_xlabel("Wards")
ax1.set_ylabel("Distance")
st.pyplot(fig1)

# Heatmap
st.header("Cluster Feature Heatmap")
fig2, ax2 = plt.subplots(figsize=(10, 5))
sns.heatmap(means, annot=True, cmap="YlGnBu", fmt=".1f", ax=ax2)
ax2.set_ylabel("Cluster")
st.pyplot(fig2)

# PCA
st.header("PCA Projection of Wards")
pca = PCA(n_components=2)
coords = pca.fit_transform(X_scaled)
fig3, ax3 = plt.subplots(figsize=(8, 6))
sns.scatterplot(x=coords[:, 0], y=coords[:, 1], hue=merged["Category"], palette="Set1", s=80, ax=ax3)
ax3.set_xlabel("PCA Component 1")
ax3.set_ylabel("PCA Component 2")
st.pyplot(fig3)

# Choropleth
st.header("Interactive Choropleth Map")

with open("Sheffield_Wards.geojson") as f:
    geojson_dict = json.load(f)

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
    locations=merged["admin_name"],
    z=merged["Category"].map(level_map),
    featureidkey="properties.admin_name",
    colorscale=[[0, "red"], [0.5, "orange"], [1, "green"]],
    zmin=0,
    zmax=2,
    marker_line_color="black",
    marker_line_width=1,
    hovertext=merged.apply(lambda row: f"{row['admin_name']}<br>Cluster: {row['Category']}<br>(0=Low, 1=Mid, 2=Extensive)", axis=1),
    hoverinfo="text",
    visible=True,
    name="Cluster Labels"
))

scaler = MinMaxScaler()
for feat, label in display_names.items():
    try:
        z = scaler.fit_transform(merged[[feat]]).flatten()
        merged[f"{feat}_norm"] = z
        hover = merged.apply(lambda row: f"{row['admin_name']}<br>{label}: {int(row[feat])}", axis=1)
        colorscale = [[0, "green"], [0.5, "orange"], [1, "red"]] if feat == "flood_risk" else [[0, "red"], [0.5, "orange"], [1, "green"]]
        traces.append(go.Choroplethmap(
            geojson=geojson_dict,
            locations=merged["admin_name"],
            z=merged[f"{feat}_norm"],
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

fig_map = go.Figure(data=traces)
fig_map.update_layout(
    map=dict(style="carto-positron", center={"lat": 53.38, "lon": -1.47}, zoom=10.5),
    updatemenus=[dict(buttons=buttons, direction="right", showactive=True, type="buttons", x=0.5, xanchor="center", y=1.05, yanchor="bottom")],
    margin={"r": 0, "t": 40, "l": 0, "b": 0},
    title="Sheffield Ward-Level Feature-Based Cluster Map"
)

st.plotly_chart(fig_map, use_container_width=True)

# Data table
st.header("Ward Data with Cluster Labels")
st.dataframe(merged[["admin_name", "Category"]].sort_values("Category"))