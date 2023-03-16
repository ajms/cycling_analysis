from pathlib import Path

import folium
import gpxpy
from tqdm import tqdm

gpx_data_dir = Path("data/raw")

map = folium.Map(location=[53, 13], tiles="openstreetmap", zoom_start=10)

for gpx_file in tqdm(gpx_data_dir.glob("*.gpx")):
    with open(gpx_file) as f:
        gpx = gpxpy.parse(f)
        route = [(p.point.latitude, p.point.longitude) for p in gpx.get_points_data()]
        folium.PolyLine(route, weight=3, opacity=0.5, color="black").add_to(map)

target_path = Path.cwd() / "data/processed/map.html"
map.save(target_path)
print(f"Open map: \x1b]8;;{target_path}\x1b\\Ctrl+Click here\x1b]8;;\x1b\\")
