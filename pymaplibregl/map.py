from __future__ import annotations

import json
import os.path
from typing import Union

from jinja2 import Template
from pydantic import ConfigDict, Field, field_validator

from ._templates import html_template, js_template
from ._utils import BaseModel, get_output_dir, read_internal_file
from .basemaps import Carto, construct_carto_basemap_url
from .controls import Control, ControlPosition, Marker
from .layer import Layer
from .sources import Source


class MapOptions(BaseModel):
    model_config = ConfigDict(
        validate_assignment=True, extra="forbid", use_enum_values=False
    )
    antialias: bool = None
    attribution_control: bool = Field(None, serialization_alias="attributionControl")
    bearing: int = None
    bearing_snap: int = Field(None, serialization_alias="bearingSnap")
    bounds: tuple = None
    box_zoom: bool = Field(None, serialization_alias="boxZoom")
    center: tuple = None
    click_tolerance: int = Field(None, serialization_alias="clickTolerance")
    custom_attribution: bool = Field(None, serialization_alias="customAttribution")
    double_click_zoom: bool = Field(None, serialization_alias="doubleClickZoom")
    fade_duration: int = Field(None, serialization_alias="fadeDuration")
    fit_bounds_options: dict = Field(None, serialization_alias="fitBoundsOptions")
    hash: Union[bool, str] = None
    interactive: bool = None
    keyword: bool = None
    max_bounds: tuple = Field(None, serialization_alias="maxBounds")
    max_pitch: int = Field(None, serialization_alias="maxPitch")
    max_zoom: int = Field(None, serialization_alias="maxZoom")
    min_pitch: int = Field(None, serialization_alias="minPitch")
    min_zoom: int = Field(None, serialization_alias="minZoom")
    pitch: int = None
    scroll_zoom: bool = Field(None, serialization_alias="scrollZoom")
    style: Union[str, Carto] = construct_carto_basemap_url(Carto.DARK_MATTER)
    zoom: int = None

    @field_validator("style")
    def validate_style(cls, v):
        if isinstance(v, Carto):
            return construct_carto_basemap_url(v)

        return v


class Map(object):
    MESSAGE = "not implemented yet"

    def __init__(self, map_options: MapOptions = MapOptions(), **kwargs):
        self._map_options = map_options.to_dict() | kwargs
        self._calls = []

    def to_dict(self) -> dict:
        return {"mapOptions": self._map_options, "calls": self._calls}

    @property
    def sources(self) -> list:
        return [item["data"] for item in self._calls if item["name"] == "addSource"]

    @property
    def layers(self) -> list:
        return [item["data"] for item in self._calls if item["name"] == "addLayer"]

    # TODO: Rename to add_map_call
    def add_call(self, func_name: str, params: list) -> None:
        self._calls.append(
            {"name": "applyFunc", "data": {"funcName": func_name, "params": params}}
        )

    def add_control(
        self,
        control: Control,
        position: [str | ControlPosition] = ControlPosition.TOP_RIGHT,
    ) -> None:
        data = {
            "type": control.type,
            "options": control.to_dict(),
            "position": ControlPosition(position).value,
        }
        self._calls.append({"name": "addControl", "data": data})

    def add_source(self, id: str, source: [Source | dict]) -> None:
        if isinstance(source, Source):
            source = source.to_dict()

        self._calls.append({"name": "addSource", "data": {"id": id, "source": source}})

    def add_layer(self, layer: [Layer | dict]) -> None:
        if isinstance(layer, Layer):
            layer = layer.to_dict()

        self._calls.append({"name": "addLayer", "data": layer})

    def add_marker(self, marker: Marker) -> None:
        self._calls.append({"name": "addMarker", "data": marker.to_dict()})

    def add_popup(self, layer_id: str, prop: str) -> None:
        self._calls.append(
            {"name": "addPopup", "data": {"layerId": layer_id, "property": prop}}
        )

    def set_filter(self, layer_id: str, filter_: list):
        self.add_call("setFilter", [layer_id, filter_])

    def set_paint_property(self, layer_id: str, prop: str, value: any) -> None:
        self.add_call("setPaintProperty", [layer_id, prop, value])

    def set_layout_property(self, layer_id: str, prop: str, value: any) -> None:
        self.add_call("setLayoutProperty", [layer_id, prop, value])

    def to_html(self, output_dir: str = None, **kwargs) -> str:
        js_lib = read_internal_file("srcjs", "index.js")
        js_snippet = Template(js_template).render(data=json.dumps(self.to_dict()))
        output = Template(html_template).render(
            js="\n".join([js_lib, js_snippet]), **kwargs
        )
        if output_dir == "skip":
            return output

        file_name = os.path.join(get_output_dir(output_dir), "index.html")
        with open(file_name, "w") as f:
            f.write(output)

        return file_name
