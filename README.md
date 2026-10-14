# EcoRoute — MVP con OpenStreetMap, OSMnx, NetworkX y Folium

Backend inicial para experimentar con rutas de menor costo sobre la red vial de Cuauhtémoc, Ciudad de México.

## Requisitos
- Python 3.11 o 3.12 recomendado.
- Conexión a internet durante la primera descarga del grafo vial.
- No necesita una clave de Google Maps.

## Instalación en Windows PowerShell

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python -m uvicorn app:app --reload
```

Abrir `http://127.0.0.1:8000/docs` y probar los endpoints.

## Endpoints
- `GET /` información de la API.
- `GET /health` comprobación de salud sin descargar el grafo.
- `POST /route` calcula una ruta mediante Dijkstra.
- `POST /route/simulate-traffic` compara la ruta base con una simulación de congestión.

### Ejemplo de `POST /route`

```json
{
  "origin": {"lat": 19.4326, "lon": -99.1332},
  "destination": {"lat": 19.4250, "lon": -99.1450},
  "weight": "travel_time",
  "map_html": true
}
```

### Ejemplo de `POST /route/simulate-traffic`

```json
{
  "origin": {"lat": 19.4326, "lon": -99.1332},
  "destination": {"lat": 19.4250, "lon": -99.1450},
  "traffic_point": {"lat": 19.4290, "lon": -99.1390},
  "radius_m": 250,
  "factor": 3,
  "weight": "travel_time",
  "map_html": true
}
```

## Notas importantes
- La primera llamada a `/route` descarga el grafo de conducción del área configurada y puede tardar. Se guarda en `data/` para reutilizarlo.
- El punto y factor de congestión del endpoint de simulación son datos artificiales para probar el recálculo. No son información de tráfico en tiempo real.
- `travel_time` es una estimación derivada de atributos viales (velocidades disponibles o estimadas), no tráfico actual.
- Folium genera HTML en `outputs/`. La respuesta da una ruta local al archivo; no publica el mapa automáticamente en el frontend.
- Para producción, deben revisarse las políticas de uso de los servidores de OpenStreetMap, la atribución visible, el almacenamiento en caché y la carga de consultas. Los datos OSM se distribuyen bajo ODbL.
- Este MVP calcula una ruta entre un origen y un destino. La asignación óptima de puntos a múltiples camiones todavía no está implementada.
- Si el grafo ya existe y cambia el área, elimina el archivo GraphML local para forzar una descarga nueva.
