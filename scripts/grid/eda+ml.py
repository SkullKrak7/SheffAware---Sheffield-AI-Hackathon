import geopandas as gpd
import pandas as pd
import plotly.express as px

grid = gpd.read_file("sheffield_grid.geojson")
features = pd.read_csv("grid_features.csv")
grid = grid.merge(features, on="grid_id", how="left").fillna(0)
grid = grid.to_crs(epsg=4326)
geojson_dict = grid.set_index("grid_id").__geo_interface__
df = grid.drop(columns="geometry")

fig = px.choropleth_mapbox(
    df,
    geojson=geojson_dict,
    locations="grid_id",
    color="tree_count",
    color_continuous_scale="Greens",
    mapbox_style="open-street-map",
    center={"lat": 53.38, "lon": -1.48},
    zoom=12,
    opacity=0.4,
    hover_name="grid_id",
    hover_data={"tree_count": True}
)

fig.update_traces(marker_line_width=0.4, marker_line_color="lightgray")
fig.update_layout(title="Tree Count per Grid in Sheffield", margin={"r": 0, "t": 40, "l": 0, "b": 0})
fig.show()
