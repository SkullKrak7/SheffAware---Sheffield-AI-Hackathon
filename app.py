import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from sklearn.preprocessing import StandardScaler
from scipy.cluster.hierarchy import linkage, dendrogram, fcluster
from sklearn.decomposition import PCA

# Page config
st.set_page_config(page_title="Ward-Level Clustering", layout="wide")

# Title
st.title("SheffAware Ward-Level Clustering Analysis")

# Sidebar inputs
st.sidebar.header("Data Settings")
base_path = st.sidebar.text_input(
    "Base path for ward CSV files", "./data"
)
cluster_count = st.sidebar.number_input(
    "Number of Clusters", min_value=2, max_value=10, value=3, step=1
)

# Load data
features = [
    "tree_count", "library_count", "camera_count", "grit_bin_count",
    "crossing_count", "waste_access", "drain_density", "flood_risk"
]

dfs = []
for f in features:
    path = f"{base_path}/{f}_per_ward.csv"
    df = pd.read_csv(path)
    df.columns = ["admin_name", f]
    dfs.append(df)

# Merge dataframes on admin_name
merged = dfs[0]
for df in dfs[1:]:
    merged = merged.merge(df, on="admin_name")

# Calculate flood safety
merged["flood_safety"] = 1 - merged["flood_risk"]

# Feature matrix and weighting
feature_cols = [
    "tree_count", "library_count", "camera_count", "grit_bin_count",
    "crossing_count", "waste_access", "drain_density", "flood_safety"
]
weights = [2, 1, 2, 1, 1, 1, 1, 2]
X = merged[feature_cols]
X_scaled = StandardScaler().fit_transform(X)
X_weighted = X_scaled * weights

# Hierarchical clustering
linkage_matrix = linkage(X_weighted, method='ward')
merged["cluster"] = fcluster(linkage_matrix, t=cluster_count, criterion='maxclust')

# Dendrogram
st.header("Hierarchical Clustering Dendrogram")
fig1, ax1 = plt.subplots(figsize=(12, 6))
dendrogram(
    linkage_matrix,
    labels=merged["admin_name"].values,
    leaf_rotation=90,
    leaf_font_size=8,
    ax=ax1
)
ax1.set_xlabel("Wards")
ax1.set_ylabel("Distance")
st.pyplot(fig1)

# Feature Heatmap
st.header("Cluster Feature Heatmap")
cluster_means = merged.groupby("cluster")[feature_cols].mean()
fig2, ax2 = plt.subplots(figsize=(10, 5))
sns.heatmap(
    cluster_means,
    annot=True,
    cmap="YlGnBu",
    fmt=".1f",
    ax=ax2
)
ax2.set_ylabel("Cluster")
st.pyplot(fig2)

# PCA Projection
st.header("PCA Projection of Wards")
pca = PCA(n_components=2)
coords = pca.fit_transform(X_weighted)
fig3, ax3 = plt.subplots(figsize=(8, 6))
sns.scatterplot(
    x=coords[:, 0], y=coords[:, 1], hue=merged["cluster"],
    palette="Set1", s=80, ax=ax3
)
ax3.set_xlabel("PCA Component 1")
ax3.set_ylabel("PCA Component 2")
st.pyplot(fig3)

# Display data table
st.header("Ward Data with Cluster Labels")
st.dataframe(merged["admin_name cluster".split()].sort_values("cluster"))