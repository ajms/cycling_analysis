from pathlib import Path

import folium
import gpxpy
import pandas as pd
from folium import plugins
from tqdm import tqdm


def gpx_to_map(
    maps: folium.Map, gpx_data_dir: str | Path, map_type: str = "polyline"
) -> folium.Map:
    # load gpx data to map
    for gpx_file in tqdm(gpx_data_dir.glob("*.gpx")):
        with open(gpx_file) as f:
            gpx = gpxpy.parse(f)
            route = [
                (p.point.latitude, p.point.longitude) for p in gpx.get_points_data()
            ]
            match map_type:
                case "polyline":
                    maps.add_child(
                        folium.PolyLine(route, weight=3, opacity=0.5, color="black")
                    )
                case "heatmap":
                    maps.add_child(plugins.HeatMap(route, radius=5, blur=3))
    return maps


def public_transport_to_map(
    maps: folium.Map, lines: str | Path, shapes: str | Path
) -> folium.Map:
    # load train data to map
    for train in tqdm(lines["route_short_name"].unique()):
        line = lines[lines["route_short_name"] == train]
        colour = list(line["Hex"])[0]
        maps.add_child(
            folium.PolyLine(
                shapes.loc[
                    shapes["route_short_name"] == train,
                    ["shape_pt_lat", "shape_pt_lon"],
                ],
                tooltip=train,
                weight=1,
                opacity=0.5,
                color=colour,
            )
        )
        for _, v in line.iterrows():
            maps.add_child(
                folium.CircleMarker(
                    location=(v["stop_lat"], v["stop_lon"]),
                    tooltip=v["stop_name"],
                    radius=3,
                    color=colour,
                )
            )
    return maps


def tracking_map():
    gpx_data_dir = Path("data/raw/tracking")
    maps = folium.Map(location=[53, 13], tiles="stamenterrain", zoom_start=10)
    maps = gpx_to_map(maps=maps, gpx_data_dir=gpx_data_dir)

    trainlines = pd.read_csv(Path.cwd() / "data/processed/trainlines.csv")
    trainshapes = pd.read_csv(Path.cwd() / "data/processed/trainshapes.csv")

    maps = public_transport_to_map(maps=maps, lines=trainlines, shapes=trainshapes)

    target_path = Path.cwd() / "data/processed/map_tracking.html"
    maps.save(target_path)
    print(f"Open map: \x1b]8;;{target_path}\x1b\\Ctrl+Click here\x1b]8;;\x1b\\")


def races_map():
    gpx_data_dir = Path("data/raw/races")
    map_type = "heatmap"
    tiles = "cartodbdark_matter"
    maps = folium.Map(location=[53, 13], tiles=tiles, zoom_start=5)
    maps = gpx_to_map(maps=maps, gpx_data_dir=gpx_data_dir, map_type="heatmap")

    target_path = Path.cwd() / f"data/processed/map_races_{tiles}_{map_type}.html"
    maps.save(target_path)
    print(f"Open map: \x1b]8;;{target_path}\x1b\\Ctrl+Click here\x1b]8;;\x1b\\")


if __name__ == "__main__":
    tracking_map()
    # races_map()
