# %%
from pathlib import Path

import pandas as pd

# %%
routes = pd.read_csv(Path("../data/public_transport/routes.txt"))
trips = pd.read_csv(Path("../data/public_transport/trips.txt"))
stop_times = pd.read_csv(Path("../data/public_transport/stop_times.txt"))
stops = pd.read_csv(Path("../data/public_transport/stops.txt"))
colours = pd.read_csv(
    Path("../data/public_transport/2022-12-Linienfarben.csv"), sep=";"
)
# %%
trains = routes[routes["route_short_name"].str.match(r"(R|S|U).*")][
    ["route_id", "route_short_name"]
]
train_trips = trains.merge(
    trips[["route_id", "trip_id"]].drop_duplicates(),
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
