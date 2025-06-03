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

st.set_page_config(page_title="SheffAware Ward-Level Clustering", layout="wide")
st.title("SheffAware Ward-Level Clustering Analysis")

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

@st.cache_data
def load_features():
    dfs = [pd.read_csv(path) for path in feature_files.values()]
    for df, name in zip(dfs, feature_files.keys()):
        df.columns = ["admin_name", name]
    merged = reduce(lambda left, right: pd.merge(left, right, on="admin_name", how="left"), dfs)
    merged["flood_safety"] = 1 - merged["flood_risk"]
    return merged

@st.cache_data
def load_geojson():
    with open("Sheffield_Wards.geojson") as f:
        return json.load(f)

@st.cache_data
def run_clustering(df):
    features = list(feature_files.keys())
    features[-1] = "flood_safety"
    weights = [2, 1, 2, 1, 1, 1, 1, 2]
    X_scaled = StandardScaler().fit_transform(df[features])
    X_scaled *= weights
    linkage_matrix = linkage(X_scaled, method="ward")
    df["cluster"] = fcluster(linkage_matrix, t=3, criterion="maxclust")
    means = df.groupby("cluster")[features].mean()
    order = means.mean(axis=1).sort_values(ascending=False).index
    label_map = {order[0]: "Extensive", order[1]: "Mid", order[2]: "Low"}
    df["Category"] = df["cluster"].map(label_map)
    return df, linkage_matrix, means, X_scaled

merged = load_features()
geojson_dict = load_geojson()
merged, linkage_matrix, means, X_scaled = run_clustering(merged)

st.sidebar.header("Info")
st.sidebar.write("Clustering based on hierarchical Ward’s method.")

st.header("Hierarchical Clustering Dendrogram")
fig1, ax1 = plt.subplots(figsize=(12, 6))
dendrogram(linkage_matrix, labels=merged["admin_name"].values, leaf_rotation=90, leaf_font_size=8, ax=ax1)
ax1.set_xlabel("Wards")
ax1.set_ylabel("Distance")
st.pyplot(fig1)

st.header("Cluster Feature Heatmap")
fig2, ax2 = plt.subplots(figsize=(10, 5))
sns.heatmap(means, annot=True, cmap="YlGnBu", fmt=".1f", ax=ax2)
ax2.set_ylabel("Cluster")
st.pyplot(fig2)

st.header("PCA Projection of Wards")
pca = PCA(n_components=2)
coords = pca.fit_transform(X_scaled)
fig3, ax3 = plt.subplots(figsize=(8, 6))
sns.scatterplot(x=coords[:, 0], y=coords[:, 1], hue=merged["Category"], palette="Set1", s=80, ax=ax3)
ax3.set_xlabel("PCA Component 1")
ax3.set_ylabel("PCA Component 2")
st.pyplot(fig3)

st.header("Interactive Choropleth Map")
layer_options = ["Cluster Labels"] + list(display_names.values())
selected_layer = st.selectbox("Choose map layer", layer_options)

scaler = MinMaxScaler()
level_map = {"Low": 0, "Mid": 1, "Extensive": 2}

if selected_layer == "Cluster Labels":
    hover = merged["admin_name"] + "<br>Cluster: " + merged["Category"] + "<br>(0=Low, 1=Mid, 2=Extensive)"
    z = merged["Category"].map(level_map)
    colorscale = [[0, "red"], [0.5, "orange"], [1, "green"]]
else:
    col_key = [k for k, v in display_names.items() if v == selected_layer][0]
    z = scaler.fit_transform(merged[[col_key]]).flatten()
    hover = merged["admin_name"] + f"<br>{selected_layer}: " + merged[col_key].astype(int).astype(str)
    colorscale = [[0, "green"], [0.5, "orange"], [1, "red"]] if col_key == "flood_risk" else [[0, "red"], [0.5, "orange"], [1, "green"]]

fig_map = go.Figure(go.Choroplethmap(
    geojson=geojson_dict,
    locations=merged["admin_name"],
    z=z,
    featureidkey="properties.admin_name",
    colorscale=colorscale,
    zmin=0,
    zmax=1 if selected_layer != "Cluster Labels" else 2,
    marker_line_color="black",
    marker_line_width=1,
    hovertext=hover,
    hoverinfo="text",
    name=selected_layer
))

fig_map.update_layout(
    map=dict(style="carto-positron", center={"lat": 53.38, "lon": -1.47}, zoom=10.5),
    margin={"r": 0, "t": 40, "l": 0, "b": 0},
    title=f"Sheffield Ward-Level Map: {selected_layer}"
)

st.plotly_chart(fig_map, use_container_width=True)

st.header("Ward Data with Cluster Labels")
st.dataframe(merged[["admin_name", "Category"]].sort_values("Category"))
