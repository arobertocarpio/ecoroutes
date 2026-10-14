from pathlib import Path
from threading import Lock

import networkx as nx
import osmnx as ox

GRAPH_DIR = Path("data")
GRAPH_PATH = GRAPH_DIR / "cuauhtemoc_drive.graphml"
_graph = None
_graph_lock = Lock()

# Delimitación inicial para el MVP. Se puede ajustar cuando se defina la zona exacta.
PLACE = "Cuauhtémoc, Ciudad de México, México"


def get_graph():
    """Carga el grafo local o lo descarga de OpenStreetMap la primera vez."""
    global _graph
    if _graph is not None:
        return _graph

    with _graph_lock:
        if _graph is not None:
            return _graph

        ox.settings.use_cache = True
        ox.settings.log_console = False
        GRAPH_DIR.mkdir(parents=True, exist_ok=True)

        if GRAPH_PATH.exists():
            graph = ox.load_graphml(GRAPH_PATH)
        else:
            graph = ox.graph_from_place(PLACE, network_type="drive", simplify=True)
            graph = ox.add_edge_speeds(graph)
            graph = ox.add_edge_travel_times(graph)
            ox.save_graphml(graph, GRAPH_PATH)

        # Asegurar que los pesos estén presentes también en grafos locales antiguos.
        if not all("travel_time" in data for _, _, _, data in graph.edges(keys=True, data=True)):
            graph = ox.add_edge_speeds(graph)
            graph = ox.add_edge_travel_times(graph)
        _graph = graph
        return _graph


def nearest_node(graph, lat: float, lon: float):
    try:
        print("Coordenada solicitada:", lat, lon)

        if not (-90 <= lat <= 90 and -180 <= lon <= 180):
            raise ValueError("Latitud o longitud fuera de rango.")

        if not (
            19.20 <= lat <= 19.60
            and -99.35 <= lon <= -98.95
        ):
            raise ValueError(
                "Las coordenadas están fuera del área de estudio de EcoRoute."
            )

        node = ox.distance.nearest_nodes(
            graph, X=lon, Y=lat
        )

        print("Nodo encontrado:", node)
        return node

    except Exception as exc:
        print("ERROR ORIGINAL:", repr(exc))
        raise ValueError(
            f"No se pudo encontrar el nodo cercano: {exc}"
        ) from exc


def shortest_route(graph, origin_node, destination_node, weight: str = "length", edge_costs=None):
    """Calcula un camino mínimo mediante Dijkstra; admite costos temporales simulados."""
    if weight not in {"length", "travel_time"}:
        raise ValueError("El peso debe ser 'length' o 'travel_time'.")

    if edge_costs is None:
        path = nx.shortest_path(graph, origin_node, destination_node, weight=weight, method="dijkstra")
        cost = nx.shortest_path_length(graph, origin_node, destination_node, weight=weight, method="dijkstra")
        return path, float(cost)

    def cost(u, v, data):
        # En grafos MultiDiGraph, NetworkX entrega un diccionario de claves de aristas.
        if isinstance(data, dict) and data and all(isinstance(value, dict) for value in data.values()):
            values = []
            for key, attrs in data.items():
                base = float(attrs.get(weight, float("inf")))
                values.append(base * edge_costs.get((u, v, key), 1.0))
            return min(values, default=float("inf"))
        return float(data.get(weight, float("inf"))) * edge_costs.get((u, v, 0), 1.0)

    path = nx.shortest_path(graph, origin_node, destination_node, weight=cost, method="dijkstra")
    total = nx.shortest_path_length(graph, origin_node, destination_node, weight=cost, method="dijkstra")
    return path, float(total)
