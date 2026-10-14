from pydantic import BaseModel, Field


class Coordinates(BaseModel):
    lat: float = Field(..., ge=-90, le=90, description="Latitud WGS84")
    lon: float = Field(..., ge=-180, le=180, description="Longitud WGS84")


class RouteRequest(BaseModel):
    origin: Coordinates
    destination: Coordinates
    weight: str = Field(default="length", pattern="^(length|travel_time)$")
    map_html: bool = Field(default=False, description="Si es true, guarda un mapa Folium en outputs/")


class TrafficSimulationRequest(BaseModel):
    origin: Coordinates
    destination: Coordinates
    # Factor multiplicador aplicado a los costos de las aristas cercanas al punto.
    traffic_point: Coordinates
    radius_m: float = Field(default=250, gt=0, le=2000)
    factor: float = Field(default=3.0, ge=1.0, le=20.0)
    weight: str = Field(default="travel_time", pattern="^(length|travel_time)$")
    map_html: bool = True
