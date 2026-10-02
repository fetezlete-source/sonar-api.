-- Activation de l'extension spatiale (indispensable)
CREATE EXTENSION IF NOT EXISTS postgis;

-- --------------------------------------------------------
-- 1. Table des segments de rues (Notre référentiel statique)
-- --------------------------------------------------------
CREATE TABLE segments_rues (
    id SERIAL PRIMARY KEY,
    nom_rue VARCHAR(255),
    -- Ligne représentant la rue. SRID 4326 = format standard GPS WGS84
    geom GEOMETRY(LineString, 4326),
    capacite_estimee INT DEFAULT 0
);

-- Index spatial : fondamental pour que les requêtes de proximité soient instantanées
CREATE INDEX idx_segments_rues_geom ON segments_rues USING GIST (geom);


-- --------------------------------------------------------
-- 2. Table des places libérées (Notre flux temps réel)
-- --------------------------------------------------------
CREATE TABLE places_liberees (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    -- Point exact où le téléphone a détecté le départ
    geom GEOMETRY(Point, 4326),
    horodatage TIMESTAMPTZ DEFAULT NOW(),
    source VARCHAR(50) DEFAULT 'passive', -- 'passive' (Bluetooth/Activité) ou 'active' (Bouton manuel)
    fiabilite_score INT DEFAULT 100 -- Pour le futur système anti-triche
);

-- Index spatial pour trouver rapidement les places autour du conducteur
CREATE INDEX idx_places_liberees_geom ON places_liberees USING GIST (geom);

-- Index temporel pour filtrer ultra-rapidement les places périmées (ex: > 5 min)
CREATE INDEX idx_places_liberees_horodatage ON places_liberees (horodatage);


-- --------------------------------------------------------
-- 3. Données de test (Optionnel)
-- --------------------------------------------------------
-- Insertion d'une fausse place libérée à l'instant, disons près de la Plaza Mayor pour nos futurs tests
INSERT INTO places_liberees (geom) 
VALUES (ST_SetSRID(ST_MakePoint(-3.7074, 40.4154), 4326));