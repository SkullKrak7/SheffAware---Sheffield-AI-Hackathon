# SheffAware: Sheffield AI Hackathon Project

## Overview

SheffAware addresses how public infrastructure and environmental services are spatially distributed across Sheffield, aiming to identify inequities and clusters using unsupervised learning techniques.

**SheffAware** is a spatial clustering and visualization project analyzing public infrastructure and environmental risk across the wards of Sheffield. Using open geospatial datasets from the Sheffield City Council, it engineers ward-level features, applies hierarchical clustering, and presents interactive Plotly-based visualizations through a Streamlit web app.

> Originally built with a grid-level prototype, the final solution consolidates all functionality at the **ward level** for actionable, interpretable insights.

---

## Project Structure

While grid-level granularity was initially explored, ward-level clustering was ultimately favored due to administrative relevance and clearer interpretability.

```
SheffAware/
├── app.py
├── requirements.txt
├── Sheffield_Wards.geojson
├── README.md
│
├── data/
│   ├── ward/
│   └── grid/
│
├── scripts/
│   ├── ward/
│   └── grid/
```

---

## Features Engineered

| Feature          | Description                  |
| ---------------- | ---------------------------- |
| `tree_count`     | Tree preservation orders     |
| `library_count`  | Libraries                    |
| `camera_count`   | CCTV and traffic cameras     |
| `grit_bin_count` | Grit/salt bins               |
| `crossing_count` | School crossings             |
| `waste_access`   | Waste recycling centres      |
| `drain_density`  | Highway drain nodes          |
| `flood_risk`     | Binary flood risk zone       |
| `flood_safety`   | Computed as `1 - flood_risk` |

---

## Final Ward-Level Pipeline

- Loads and merges all 8 features per ward
- Adds `flood_safety` as a derived variable
- Applies **Ward's hierarchical clustering** with custom weights
- Assigns each ward into 3 clusters: `Low`, `Mid`, `Extensive`

### Visualizations

All visualizations are embedded in the final Streamlit app:

- Dendrogram (cluster tree)
- Cluster-wise feature heatmap
- PCA scatter plot
- **Interactive Plotly Choropleth** with:
  - Cluster labels
  - Normalized views of each individual feature
  - Hover tooltips showing ward name and value/label

---

## Grid-Level Pipeline (Legacy Prototype)

- Constructed 0.02-degree spatial grid over Sheffield
- Feature extraction per grid tile using point-in-polygon joins
- KMeans clustering and basic EDA (Plotly maps, scatter plots)
- Not used in the final pipeline, included for transparency

Grid-level analysis was conducted by **Naveena Vasireddy** and **Sri Ranga Sai Tulasi** as part of the exploratory phase. However, this was not carried forward into the final project or GitHub deployment, as the ward-level model offered clearer interpretability, stronger policy alignment, and consistency with administrative boundaries.

---

## How to Run

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Launch the Dashboard

```bash
streamlit run app.py
```

You can optionally deploy the dashboard to [Streamlit Cloud](https://streamlit.io/cloud) by pushing this repo to GitHub and linking your account.

---

## Tech Stack

- Python: `pandas`, `geopandas`, `scikit-learn`, `seaborn`, `matplotlib`
- Mapping & UI: `plotly`, `Streamlit`
- Clustering: Hierarchical (Ward’s method)
- Mapping: GeoJSON + Plotly Choropleth
- Data Preprocessing: GeoPandas spatial joins and aggregation

---

## Credits

- **Sai Karthik Kagolanu** — End-to-end lead:

  - Preprocessed and engineered all spatial features (ward & grid)
  - Merged data, implemented hierarchical clustering
  - Designed and built the full Streamlit app with Plotly visuals
  - Reframed problem from grid-based to ward-level for actionable insights

- **Sri Ranga Sai Tulasi** — Supported in:

  - Dataset alignment with Sheffield council goals
  - Ideation, concept refinement, and challenge framing
  - Also performed grid-level preprocessing and implementations (not retained in the final project or GitHub deployment)

- **Naveena Vasireddy** — Exploratory grid work:

  - Conducted KMeans clustering and EDA on synthetic grids
  - Created early Plotly visualizations (non-retained in final app)

- **Rajita Ghosh** — Collaborative input and planning

---

## Limitations and Future Work

- Current clusters are fixed at 3; dynamic cluster selection could be explored.
- Grid-level clustering was excluded from the final deployment for administrative clarity.
- Additional demographic or socioeconomic features could improve context.

## License

MIT License © 2025 Sai Karthik Kagolanu
