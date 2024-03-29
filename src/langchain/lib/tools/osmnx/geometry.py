"""
Borrowed from Development Seed.

https://github.com/developmentseed/llllm/blob/main/tools/osmnx/geometry.py
"""


from typing import Type, Dict

import osmnx as ox
import geopandas as gpd
from pydantic import BaseModel, Field
from langchain.tools import BaseTool


class PlaceWithTags(BaseModel):
    "Name of a place on the map and tags in OSM."

    place: str = Field(..., description="name of a place on the map.")
    # tags: Dict[str, str] = Field(..., description="open street maps tags.")


class OSMnxGeometryTool(BaseTool):
    """Tool to query geometries from Open Street Map (OSM)."""

    name: str = "geometry"
    args_schema: Type[BaseModel] = PlaceWithTags
    description: str = (
        "Use this tool to get geometry of different features of the place like building footprints, parks, lakes, hospitals, schools etc. "
        "Pass the name of the place & tags of OSM as args."
    )
    # return_direct = True
    should_use = False

    def _run(self, place: str, tags: Dict[str, str] = {}) -> gpd.GeoDataFrame:
        gdf = ox.geometries_from_place(place, tags)
        gdf = gdf[gdf["geometry"].type.isin({"Polygon", "MultiPolygon"})]
        gdf = gdf[["name", "geometry"]].reset_index(drop=True)
        return ("geometry", gdf)

    async def _arun(self, place: str, tags: Dict[str, str] = {}):
        return self._run(place, tags)
