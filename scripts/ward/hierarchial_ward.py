import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from sklearn.preprocessing import StandardScaler
from scipy.cluster.hierarchy import linkage, dendrogram, fcluster
from sklearn.decomposition import PCA

features = [
    "tree_count", "library_count", "camera_count", "grit_bin_count",
    "crossing_count", "waste_access", "drain_density", "flood_risk"
]

dfs = [pd.read_csv(f"data/ward/{f}_per_ward.csv") for f in features]
for i, name in enumerate(features):
    dfs[i].columns = ["admin_name", name]

merged_df = pd.concat(dfs, axis=1).loc[:, ~pd.concat(dfs, axis=1).columns.duplicated()]
merged_df["flood_safety"] = 1 - merged_df["flood_risk"]

feature_cols = [
    "tree_count", "library_count", "camera_count", "grit_bin_count",
    "crossing_count", "waste_access", "drain_density", "flood_safety"
]
weights = [2, 1, 2, 1, 1, 1, 1, 2]

X_scaled = StandardScaler().fit_transform(merged_df[feature_cols])
X_scaled *= weights

linkage_matrix = linkage(X_scaled, method="ward")
merged_df["cluster"] = fcluster(linkage_matrix, t=3, criterion="maxclust")

plt.figure(figsize=(12, 6))
dendrogram(linkage_matrix, labels=merged_df["admin_name"].values, leaf_rotation=90, leaf_font_size=8)
plt.title("Hierarchical Clustering Dendrogram")
plt.xlabel("Wards")
plt.ylabel("Distance")
plt.tight_layout()
plt.show()

means = merged_df.groupby("cluster")[feature_cols].mean()
plt.figure(figsize=(10, 5))
sns.heatmap(means, annot=True, cmap="YlGnBu", fmt=".1f")
plt.title("Feature Averages per Cluster")
plt.ylabel("Cluster")
plt.tight_layout()
plt.show()

pca = PCA(n_components=2)
coords = pca.fit_transform(X_scaled)
plt.figure(figsize=(8, 6))
sns.scatterplot(x=coords[:, 0], y=coords[:, 1], hue=merged_df["cluster"], palette="Set1", s=80)
plt.title("PCA Projection of Wards")
plt.xlabel("PCA Component 1")
plt.ylabel("PCA Component 2")
plt.legend(title="Cluster")
plt.tight_layout()
plt.show()
