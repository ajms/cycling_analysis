# Install dependencies
Install python 3.10, poetry >= 3, make

Run
```bash
make prj-init
```
to install dependencies.

# Generate map
Place your gpx-files in a directory `data/raw/tracking`.

Download public transport data for Berlin from
[gtfs data](https://daten.berlin.de/datensaetze/vbb-fahrplandaten-gtfs), [colour data](https://daten.berlin.de/datensaetze/vbb-linienfarben), licensed as [CC BY 3.0 DE](https://creativecommons.org/licenses/by/3.0/de/).

Unzip, place files in `data/public_transport`, execute
```bash
make generate-public-trans
```
Then run
```bash
make generate-map
```
to generate the route map.
