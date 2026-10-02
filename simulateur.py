import random
from sqlalchemy import create_engine, text

# Connexion à notre base
DATABASE_URL = "postgresql://admin:password123@localhost:5432/parking_app"
engine = create_engine(DATABASE_URL)

# Centre de Madrid
LAT_MADRID = 40.4168
LON_MADRID = -3.7038

print("🚗 Démarrage de la simulation...")

with engine.connect() as conn:
    # On va créer 100 fausses places
    for i in range(1, 101):
        # Génère des coordonnées aléatoires dans un rayon de ~5km
        lat = LAT_MADRID + random.uniform(-0.05, 0.05)
        lon = LON_MADRID + random.uniform(-0.05, 0.05)
        
        # Choix aléatoire de la source
        source = random.choice(["passive", "active"])
        
        # Requête d'insertion
        query = text("""
            INSERT INTO places_liberees (geom, source)
            VALUES (ST_SetSRID(ST_MakePoint(:lon, :lat), 4326), :source)
        """)
        
        conn.execute(query, {"lon": lon, "lat": lat, "source": source})
        
    conn.commit() # Sauvegarde globale

print("✅ 100 places libérées ont été injectées avec succès dans Madrid !")