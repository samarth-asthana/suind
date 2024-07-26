from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import List
from datetime import datetime, timedelta
from typing_extensions import Literal
import pystac_client
import planetary_computer
import rasterio
from rasterio import windows
from rasterio import features
from rasterio import warp
import numpy as np
import logging

app = FastAPI()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class GeoJSONPolygon(BaseModel):
    type: Literal["Polygon"]
    coordinates: List[List[List[float]]]

class QueryRequest(BaseModel):
    timestamp: datetime
    polygon: GeoJSONPolygon

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

def get_sentinel2_data(timestamp: datetime, polygon: GeoJSONPolygon):
    area_of_interest = {
        "type": "Polygon",
        "coordinates": polygon.coordinates
    }
    start_date = timestamp.strftime("%Y-%m-%dT%H:%M:%SZ")
    end_date = (timestamp + timedelta(days=5)).strftime("%Y-%m-%dT%H:%M:%SZ")

    logger.info(f"Searching for data between {start_date} and {end_date}")

    catalog = pystac_client.Client.open(
        "https://planetarycomputer.microsoft.com/api/stac/v1",
        modifier=planetary_computer.sign_inplace,
    )

    search = catalog.search(
        collections=["sentinel-2-l2a"],
        intersects=area_of_interest,
        datetime=f"{start_date}/{end_date}",
        query={"eo:cloud_cover": {"lt": 20}},
    )

    items = search.item_collection()
    if not items:
        logger.error("No suitable Sentinel-2 data found")
        raise HTTPException(status_code=404, detail="No suitable Sentinel-2 data found")

    least_cloudy_item = min(items, key=lambda item: item.properties["eo:cloud_cover"])
    red_href = least_cloudy_item.assets["B04"].href  # Red band
    nir_href = least_cloudy_item.assets["B08"].href  # NIR band

    logger.info(f"Selected item with cloud cover {least_cloudy_item.properties['eo:cloud_cover']}")

    with rasterio.open(red_href) as red_ds, rasterio.open(nir_href) as nir_ds:
        aoi_bounds = features.bounds(area_of_interest)
        warped_aoi_bounds = warp.transform_bounds("epsg:4326", red_ds.crs, *aoi_bounds)
        aoi_window = windows.from_bounds(*warped_aoi_bounds, transform=red_ds.transform)
        red_band = red_ds.read(1, window=aoi_window)
        nir_band = nir_ds.read(1, window=aoi_window)

    return red_band, nir_band

@app.post("/query")
async def query_sentinel2_data(request: QueryRequest):
    try:
        red_band, nir_band = get_sentinel2_data(request.timestamp, request.polygon)
        ndvi = (nir_band - red_band) / (nir_band + red_band)

        response = {
            "mean_ndvi": np.mean(ndvi),
            "std_ndvi": np.std(ndvi),
        }
        return response
    except Exception as e:
        logger.error(f"Error processing request: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)
