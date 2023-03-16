# %%
from pathlib import Path

import pandas as pd

# %%
# gtfs data from https://daten.berlin.de/datensaetze/vbb-fahrplandaten-gtfs
routes = pd.read_csv(Path("../data/public_transport/routes.txt"))
trips = pd.read_csv(Path("../data/public_transport/trips.txt"))
stop_times = pd.read_csv(Path("../data/public_transport/stop_times.txt"))
stops = pd.read_csv(Path("../data/public_transport/stops.txt"))
shapes = pd.read_csv(Path("../data/public_transport/shapes.txt"))
# colour data from https://daten.berlin.de/datensaetze/vbb-linienfarben
colours = pd.read_csv(
    Path("../data/public_transport/2022-12-Linienfarben.csv"), sep=";"
)
# %%
# select only regional and s trains
trains = routes[routes["route_short_name"].str.match(r"(R|S).*")][
    ["route_id", "route_short_name"]
]
# link trains to stations
train_trips = trains.merge(
    trips[["route_id", "trip_id", "shape_id"]].drop_duplicates(),
    how="inner",
    on="route_id",
)
stop_trip = train_trips.merge(
    stop_times[["trip_id", "stop_id"]],
    how="inner",
    on="trip_id",
)
stop_trains = stop_trip.merge(
    stops[["stop_name", "stop_lat", "stop_lon", "stop_id"]],
    how="inner",
    on="stop_id",
)

# %%
# add colours to trains
trainlines = (
    stop_trains.sort_values("trip_id")
    .drop(["trip_id", "stop_id", "route_id"], axis=1)
    .merge(
        colours[["Linie", "Hex"]],
        how="left",
        left_on="route_short_name",
        right_on="Linie",
    )
    .drop_duplicates()
)
trainlines.loc[trainlines["Hex"].isnull(), "Hex"] = "#808080"
trainlines.drop(["Linie"], axis=1, inplace=True)
trainlines.to_csv(Path.cwd() / "../data/processed/trainlines.csv")
# %%
# get shapes of lines
trainshapes = (
    train_trips.merge(shapes, how="inner", on="shape_id")
    .drop(["trip_id", "route_id"], axis=1)
    .drop_duplicates()
    .sort_values(["route_short_name", "shape_pt_sequence"])
)
# %%
# reduce to the longest trip for each train
max_ids = (
    trainshapes.groupby(["route_short_name"])["shape_pt_sequence"].max().reset_index()
)
shape_ids = trainshapes.merge(
    max_ids, on=["route_short_name", "shape_pt_sequence"], how="inner"
)[["shape_id"]]
# %%
trainshapes = trainshapes.merge(shape_ids, on="shape_id", how="inner").sort_values(
    ["route_short_name", "shape_id"]
)
trainshapes.to_csv(Path.cwd() / "../data/processed/trainshapes.csv")
# %%
