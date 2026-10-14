from fastapi import APIRouter, HTTPException
import networkx as nx

from src.schemas.routes import RouteRequest, TrafficSimulationRequest
from src.services.graph_service import get_graph, nearest_node, shortest_route
from src.services.map_service import route_coordinates, route_metrics, save_route_map

router = APIRouter(tags=["Rutas"])


def _calculate(body, traffic_point=None, radius_m=250, factor=1.0):
    try:
        graph = get_graph()
        start = nearest_node(graph, body.origin.lat, body.origin.lon)
        end = nearest_node(graph, body.destination.lat, body.destination.lon)
        edge_costs = None

        if traffic_point is not None and factor > 1:
            # Simulación: penaliza aristas cuyos puntos medios estén cerca del punto elegido.
            # No representa datos de tráfico en tiempo real.
            import math
            edge_costs = {}
            for u, v, key, data in graph.edges(keys=True, data=True):
                udata, vdata = graph.nodes[u], graph.nodes[v]
                mid_lat = (float(udata["y"]) + float(vdata["y"])) / 2
                mid_lon = (float(udata["x"]) + float(vdata["x"])) / 2
                # Aproximación local en metros suficiente para una simulación acotada.
                dx = (mid_lon - traffic_point.lon) * 111_320 * math.cos(math.radians(traffic_point.lat))
                dy = (mid_lat - traffic_point.lat) * 110_540
                if math.hypot(dx, dy) <= radius_m:
                    edge_costs[(u, v, key)] = factor

        print(
            "Aristas penalizadas:",
            len(edge_costs) if edge_costs is not None else 0
        )
        print("Factor:", factor, "| Radio:", radius_m)

        path, weighted_cost = shortest_route(graph, start, end, body.weight, edge_costs)
        coords = route_coordinates(graph, path)
        distance_km, duration_min = route_metrics(graph, path)
        map_path = None
        if body.map_html:
            map_path = save_route_map(graph, coords, traffic_point=traffic_point)
        return {
            "origin_node": int(start),
            "destination_node": int(end),
            "algorithm": "Dijkstra (NetworkX)",
            "weight": body.weight,
            "weighted_cost": round(weighted_cost, 2),
            "distance_km": distance_km,
            "estimated_duration_min": duration_min,
            "node_count": len(path),
            "coordinates": coords,
            "map_html_path": map_path,
            "traffic_simulated": traffic_point is not None,
        }
    except (nx.NetworkXNoPath, nx.NodeNotFound):
        raise HTTPException(status_code=404, detail="No existe una ruta entre los puntos seleccionados en el grafo vial.")
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc))
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"No se pudo obtener o procesar la red vial: {exc}") from exc


@router.get("/health", tags=["Info"])
def health():
    return {"status": "ok", "map_source": "OpenStreetMap", "graph_provider": "OSMnx", "routing": "NetworkX Dijkstra"}


@router.post("/route")
def calculate_route(body: RouteRequest):
    """Calcula la ruta de menor costo por longitud o tiempo estimado de las calles."""
    return _calculate(body)


@router.post("/route/simulate-traffic")
def simulate_traffic(body: TrafficSimulationRequest):
    """Compara la ruta con una simulación local de congestión; no usa tráfico real."""
    from src.schemas.routes import RouteRequest
    normal_body = RouteRequest(
        origin=body.origin,
        destination=body.destination,
        weight=body.weight,
        map_html=False,
    )
    baseline = _calculate(normal_body)
    affected = _calculate(normal_body, traffic_point=body.traffic_point, radius_m=body.radius_m, factor=body.factor)
    if body.map_html:
        graph = get_graph()
        affected["map_html_path"] = save_route_map(
            graph, affected["coordinates"], filename="route_traffic_simulation.html", traffic_point=body.traffic_point
        )
    return {
        "simulation_notice": "Congestión simulada mediante penalización de costos; no son datos de tráfico en tiempo real.",
        "factor": body.factor,
        "radius_m": body.radius_m,
        "baseline": baseline,
        "after_simulation": affected,
        "route_changed": baseline["coordinates"] != affected["coordinates"],
    }
