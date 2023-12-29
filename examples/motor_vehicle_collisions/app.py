import h3
import pandas as pd
import shapely
from pymaplibregl import (
    Layer,
    LayerType,
    Map,
    MapContext,
    output_maplibregl,
    render_maplibregl,
)
from pymaplibregl.basemaps import Carto
from pymaplibregl.utils import GeometryType, df_to_geojson, get_bounds
from shiny import App, reactive, ui

LAYER_ID = "motor_vehicle_collisions"

motor_vehicle_collisions_data = pd.read_csv(
    "https://github.com/crazycapivara/mapboxer/raw/master/data-raw/motor_vehicle_collisions.csv",
    sep=";",
)
motor_vehicle_collisions_source = {
    "type": "geojson",
    "data": df_to_geojson(
        motor_vehicle_collisions_data,
        properties=["date", "time", "injured", "killed"],
    ),
}


"""
bbox = shapely.bounds(
    shapely.from_geojson(json.dumps(motor_vehicle_collisions_source["data"]))
)
"""
bbox = get_bounds(motor_vehicle_collisions_source["data"])
print(bbox)


motor_vehicle_collisions_layer = Layer(
    LayerType.CIRCLE,
    id_=LAYER_ID,
    source=motor_vehicle_collisions_source,
    paint={
        "circle-color": [
            "match",
            ["get", "injured"],
            0,
            "yellow",
            1,
            "orange",
            "darkred",
        ]
    },
)

app_ui = ui.page_fluid(
    ui.panel_title("Motor Vehicle Collisions NYC"),
    output_maplibregl("maplibre", height=600),
    # ui.input_slider("radius", "Radius", value=CIRCLE_RADIUS, min=1, max=5),
)


def server(input, output, session):
    @render_maplibregl
    async def maplibre():
        m = Map(
            style=Carto.POSITRON,
            bounds=list(bbox),
            fitBoundsOptions={"padding": 20},
        )
        # m.add_layer(flights_layer)
        m.add_layer(motor_vehicle_collisions_layer)
        m.add_popup(LAYER_ID, "injured")
        return m

    """
    @reactive.Effect
    @reactive.event(input.radius, ignore_init=True)
    async def radius():
        async with MapContext("maplibre") as m:
            m.set_paint_property(LAYER_ID, "circle-radius", input.radius())
    """


app = App(app_ui, server)

if __name__ == "__main__":
    app.run()
