from datetime import datetime, timedelta
from .models import GeoJSONPolygon
import pystac_client
import planetary_computer
import rasterio
from rasterio import windows
from rasterio import features
from rasterio import warp
import logging

logger = logging.getLogger(__name__)

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
