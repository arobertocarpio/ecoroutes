from pathlib import Path
import folium
import osmnx as ox

OUTPUT_DIR = Path("outputs")


def route_coordinates(graph, nodes):
    return [[float(graph.nodes[node]["y"]), float(graph.nodes[node]["x"])] for node in nodes]


def route_metrics(graph, nodes):
    distance_m = 0.0
    duration_s = 0.0
    for u, v in zip(nodes[:-1], nodes[1:]):
        edge_bundle = graph.get_edge_data(u, v) or {}
        if not edge_bundle:
            continue
        edge = min(edge_bundle.values(), key=lambda data: float(data.get("length", float("inf"))))
        distance_m += float(edge.get("length", 0.0))
        duration_s += float(edge.get("travel_time", 0.0))
    return round(distance_m / 1000, 3), round(duration_s / 60, 2)


def save_route_map(graph, coordinates, filename="route.html", traffic_point=None):
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    center = coordinates[len(coordinates) // 2]
    fmap = folium.Map(location=center, zoom_start=14, control_scale=True, tiles="OpenStreetMap")
    folium.PolyLine(coordinates, color="blue", weight=6, opacity=0.85, tooltip="Ruta EcoRoute").add_to(fmap)
    folium.Marker(coordinates[0], tooltip="Origen", icon=folium.Icon(color="green", icon="play")).add_to(fmap)
    folium.Marker(coordinates[-1], tooltip="Destino", icon=folium.Icon(color="red", icon="stop")).add_to(fmap)
    if traffic_point:
        folium.CircleMarker(
            location=[traffic_point.lat, traffic_point.lon], radius=9, color="orange",
            fill=True, fill_opacity=0.8, tooltip="Punto de congestión simulada",
        ).add_to(fmap)
    path = OUTPUT_DIR / filename
    fmap.save(str(path))
    return str(path.resolve())
