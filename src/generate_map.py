from pathlib import Path

import folium
import gpxpy
import pandas as pd
from tqdm import tqdm

gpx_data_dir = Path("data/raw")

map = folium.Map(location=[53, 13], tiles="stamenterrain", zoom_start=10)

# load gpx data to map
for gpx_file in tqdm(gpx_data_dir.glob("*.gpx")):
    with open(gpx_file) as f:
        gpx = gpxpy.parse(f)
        route = [(p.point.latitude, p.point.longitude) for p in gpx.get_points_data()]
        folium.PolyLine(route, weight=3, opacity=0.5, color="black").add_to(map)

trainlines = pd.read_csv(Path.cwd() / "data/processed/trainlines.csv")
trainshapes = pd.read_csv(Path.cwd() / "data/processed/trainshapes.csv")

# load train data to map
for train in trainlines["route_short_name"].unique():
    line = trainlines[trainlines["route_short_name"] == train]
    colour = list(line["Hex"])[0]
    folium.PolyLine(
        trainshapes.loc[
            trainshapes["route_short_name"] == train, ["shape_pt_lat", "shape_pt_lon"]
        ],
        popup=train,
        weight=1,
        opacity=0.5,
        color=colour,
    ).add_to(map)
    for _, v in line.iterrows():
        folium.CircleMarker(
            location=(v["stop_lat"], v["stop_lon"]),
            popup=v["stop_name"],
            radius=3,
            color=colour,
        ).add_to(map)

target_path = Path.cwd() / "data/processed/map.html"
map.save(target_path)
print(f"Open map: \x1b]8;;{target_path}\x1b\\Ctrl+Click here\x1b]8;;\x1b\\")
