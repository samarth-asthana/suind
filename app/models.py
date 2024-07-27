from pydantic import BaseModel, Field
from typing import List
from datetime import datetime
from typing_extensions import Literal

class GeoJSONPolygon(BaseModel):
    type: Literal["Polygon"]
    coordinates: List[List[List[float]]]

class QueryRequest(BaseModel):
    timestamp: datetime
    polygon: GeoJSONPolygon
