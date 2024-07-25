from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import List
from datetime import datetime
import pystac_client
import planetary_computer
import rasterio
from rasterio import windows
from rasterio import features
from rasterio import warp
import numpy as np

app = FastAPI()

class GeoJSONPolygon(BaseModel):
    type: str = "Polygon"
    coordinates: List[List[List[float]]]

class QueryRequest(BaseModel):
    timestamp: datetime
    polygon: GeoJSONPolygon

def get_sentinel2_data(timestamp: datetime, polygon: GeoJSONPolygon):
    area_of_interest = {
        "type": "Polygon",
        "coordinates": polygon.coordinates
    }
    time_of_interest = timestamp.strftime("%Y-%m-%dT%H:%M:%SZ")

    catalog = pystac_client.Client.open(
        "https://planetarycomputer.microsoft.com/api/stac/v1",
        modifier=planetary_computer.sign_inplace,
    )

    search = catalog.search(
        collections=["sentinel-2-l2a"],
        intersects=area_of_interest,
        datetime=time_of_interest,
        query={"eo:cloud_cover": {"lt": 10}},
    )

    items = search.item_collection()
    if not items:
        raise HTTPException(status_code=404, detail="No suitable Sentinel-2 data found")

    least_cloudy_item = min(items, key=lambda item: item.properties["eo:cloud_cover"])
    asset_href = least_cloudy_item.assets["visual"].href

    with rasterio.open(asset_href) as ds:
        aoi_bounds = features.bounds(area_of_interest)
        warped_aoi_bounds = warp.transform_bounds("epsg:4326", ds.crs, *aoi_bounds)
        aoi_window = windows.from_bounds(transform=ds.transform, *warped_aoi_bounds)
        band_data = ds.read(window=aoi_window)

    return band_data

@app.post("/query")
async def query_sentinel2_data(request: QueryRequest):
    try:
        band_data = get_sentinel2_data(request.timestamp, request.polygon)
        ndvi = (band_data[3] - band_data[2]) / (band_data[3] + band_data[2])

        response = {
            "mean_ndvi": np.mean(ndvi),
            "std_ndvi": np.std(ndvi),
        }
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
