from pathlib import Path

import folium
import gpxpy
import pandas as pd
from tqdm import tqdm

gpx_data_dir = Path("data/raw")

map = folium.Map(location=[53, 13], tiles="stamenterrain", zoom_start=10)

for gpx_file in tqdm(gpx_data_dir.glob("*.gpx")):
    with open(gpx_file) as f:
        gpx = gpxpy.parse(f)
        route = [(p.point.latitude, p.point.longitude) for p in gpx.get_points_data()]
        folium.PolyLine(route, weight=3, opacity=0.5, color="black").add_to(map)

trainlines = pd.read_csv(Path.cwd() / "data/processed/trainlines.csv")

for train in trainlines["route_short_name"].unique():
    print(f"{train=}")
    line = trainlines[trainlines["route_short_name"] == train]
    print(f"{len(line)=}")
    colour = list(line["Hex"])[0]
    print(f"{colour=}")
    line_coords = [(v["stop_lat"], v["stop_lon"]) for _, v in line.iterrows()]
    for x, y in line_coords:
        folium.CircleMarker(
            location=(x, y),
            radius=3,
            fill=True,
            color=colour,
            fill_color=colour,
        ).add_to(map)

target_path = Path.cwd() / "data/processed/map.html"
map.save(target_path)
print(f"Open map: \x1b]8;;{target_path}\x1b\\Ctrl+Click here\x1b]8;;\x1b\\")
