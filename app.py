from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.routers.routes import router as routes_router

app = FastAPI(
    title="EcoRoute API",
    description="Prototipo de optimización de rutas de recolección con OpenStreetMap, OSMnx y NetworkX.",
    version="0.2.0",
)

# En producción, limita allow_origins a la URL real del frontend.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)

app.include_router(routes_router)


@app.get("/", tags=["Info"])
def root():
    return {
        "name": "EcoRoute API",
        "status": "ok",
        "docs": "/docs",
        "routing_engine": "NetworkX Dijkstra",
        "map_data": "OpenStreetMap via OSMnx",
    }
