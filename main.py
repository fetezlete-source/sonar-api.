from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy import create_engine, text

# 1. Connexion à la base de données (SUPABASE CLOUD)
DATABASE_URL = "postgresql://postgres.gwtjutpowtfmwevivrvz:Ltt?u3R5AkyVbR6@aws-1-eu-central-1.pooler.supabase.com:6543/postgres"
engine = create_engine(DATABASE_URL)

# 2. Initialisation de l'API
app = FastAPI(title="API Stationnement MVP")

# 3. NOUVEAU : Configuration CORS pour autoriser le navigateur Chrome
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 4. Modèle de données attendu
class PlaceLiberee(BaseModel):
    latitude: float
    longitude: float
    source: str = "passive"

# 5. Route pour ajouter une place (POST)
@app.post("/parking/liberation")
def declarer_place_libre(place: PlaceLiberee):
    try:
        with engine.connect() as conn:
            query = text("""
                INSERT INTO places_liberees (geom, source)
                VALUES (
                    ST_SetSRID(ST_MakePoint(:lon, :lat), 4326),
                    :source
                )
                RETURNING id;
            """)
            result = conn.execute(query, {
                "lon": place.longitude, 
                "lat": place.latitude,
                "source": place.source
            })
            conn.commit()
            id_place = result.fetchone()[0]
            
        return {"statut": "succès", "message": "Place enregistrée !", "id": str(id_place)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# 6. Route pour chercher les places proches (GET)
@app.get("/parking/proximite")
def trouver_places_proches(latitude: float, longitude: float, rayon: int = 500):
    try:
        with engine.connect() as conn:
            query = text("""
                SELECT 
                    id,
                    ST_Y(geom) AS lat,
                    ST_X(geom) AS lon,
                    source,
                    horodatage,
                    ST_Distance(
                        geom::geography, 
                        ST_SetSRID(ST_MakePoint(:lon, :lat), 4326)::geography
                    ) AS distance_metres
                FROM places_liberees
                WHERE 
                    ST_DWithin(
                        geom::geography, 
                        ST_SetSRID(ST_MakePoint(:lon, :lat), 4326)::geography, 
                        :rayon
                    )
                    AND horodatage > NOW() - INTERVAL '30 minutes'
                ORDER BY distance_metres ASC;
            """)
            result = conn.execute(query, {
                "lat": latitude,
                "lon": longitude,
                "rayon": rayon
            })
            
            places = []
            for row in result:
                places.append({
                    "id": str(row.id),
                    "latitude": row.lat,
                    "longitude": row.lon,
                    "source": row.source,
                    "distance_metres": round(row.distance_metres),
                    "horodatage": row.horodatage.isoformat()
                })
                
        return {
            "statut": "succès", 
            "places_trouvees": len(places), 
            "rayon_recherche": f"{rayon}m",
            "resultats": places
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))