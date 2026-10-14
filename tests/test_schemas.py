from src.schemas.routes import RouteRequest, TrafficSimulationRequest


def test_route_request_accepts_coordinates():
    body = RouteRequest(
        origin={"lat": 19.43, "lon": -99.13},
        destination={"lat": 19.42, "lon": -99.14},
        weight="length",
    )
    assert body.weight == "length"


def test_traffic_factor_bounds():
    body = TrafficSimulationRequest(
        origin={"lat": 19.43, "lon": -99.13},
        destination={"lat": 19.42, "lon": -99.14},
        traffic_point={"lat": 19.425, "lon": -99.135},
        factor=3,
    )
    assert body.factor == 3
