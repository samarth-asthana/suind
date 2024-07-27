from fastapi import APIRouter, HTTPException
from .models import QueryRequest
from .services import get_sentinel2_data
import numpy as np
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/query")
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
