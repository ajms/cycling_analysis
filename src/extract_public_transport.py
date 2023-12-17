# %%
from pathlib import Path

import pandas as pd
from pandasql import sqldf

pysqldf = lambda q: sqldf(q, globals())  # noqa: E731

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
    trips[["route_id", "trip_id", "shape_id", "trip_headsign"]].drop_duplicates(),
    how="inner",
    on="route_id",
)
stop_trip = train_trips.merge(
    stop_times[["trip_id", "stop_id", "stop_sequence"]],
    how="inner",
    on="trip_id",
)
stop_trains = stop_trip.merge(
    stops[["stop_name", "stop_lat", "stop_lon", "stop_id"]],
    how="inner",
    on="stop_id",
)

# %%
q_max_sequence = """
    select route_short_name, trip_id, count(stop_sequence)-1 AS count_stop_sequence, min(stop_sequence) AS min_stop_sequence, max(stop_sequence) AS max_stop_sequence
    from stop_trains
    where route_short_name = 'R931'
    group by route_short_name, trip_id
    """
max_sequence = pysqldf(q_max_sequence)
max_sequence
# %%
q_max_sequence_route = """
select max(count_stop_sequence)
    from max_sequence b
    where b.route_short_name = "R931"
"""
max_sequence_route = pysqldf(q_max_sequence_route)
max_sequence_route
# %%
q_select_trip = """
select route_short_name, trip_id, count_stop_sequence
from max_sequence a
group by route_short_name
having count_stop_sequence = (select max(b.max_stop_sequence) as c from max_sequence b where a.route_short_name = b.route_short_name)
"""
pysqldf(q_select_trip)
# %%
q_max_trips = """
    select a.route_short_name, max(trip_id) as trip_id
    from
    stop_trains a
    inner join
    max_sequence b
    on a.route_short_name = b.route_short_name
    group by a.route_short_name;
    """
max_trips = pysqldf(q_max_trips)
max_trips
# %%
q_endstation = """
    select a.route_short_name, stop_name
    from
        stop_trains a
        inner join
        max_sequence b
        on a.route_short_name = b.route_short_name
        inner join
        max_trips c
        on a.trip_id = c.trip_id
    group by a.route_short_name, stop_name
    having stop_sequence = 0 or stop_sequence = b.max_stop_sequence
    order by a.route_short_name, stop_sequence asc;
"""
endstation = pysqldf(q_endstation)
# %%
endstation["route_short_name"].value_counts()
# %%
# %%
max_stops = (
    stop_trains.groupby(["route_short_name"])["stop_sequence"].max().reset_index()
)
longest_trips = stop_trains.merge(
    max_stops, how="inner", on=["route_short_name", "stop_sequence"]
)[["trip_id"]]
longest_trips_per_line = stop_trains.merge(longest_trips, how="inner", on=["trip_id"])

longest_trips_per_line.loc[
    longest_trips_per_line["stop_sequence"] == 0, ["route_short_name", "stop_name"]
].drop_duplicates().sort_values(by=["route_short_name", "stop_name"])
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
trainshapes.loc[trainshapes["route_short_name"] == "RB10"].groupby("trip_headsign").agg(
    ["min", "max"]
).reset_index().value_counts()
# %%
trips.groupby("route_id").agg(["min", "max"]).reset_index()
# %%
# reduce to the longest trip for each train
max_ids = (
    trainshapes.groupby(["route_short_name"])["shape_pt_sequence"].max().reset_index()
)
shape_ids = trainshapes.merge(
    max_ids, on=["route_short_name", "shape_pt_sequence"], how="inner"
)
# %%
trainshapes = trainshapes.merge(shape_ids, on="shape_id", how="inner").sort_values(
    ["route_short_name", "shape_id"]
)
trainshapes.to_csv(Path.cwd() / "../data/processed/trainshapes.csv")
# %%
