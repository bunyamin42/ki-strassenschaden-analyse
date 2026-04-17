import requests
import osmnx as ox
import geopandas as gpd
import numpy as np
from shapely.geometry import Point
import json
from datetime import datetime

ACCESS_TOKEN = "MLY|26116954324650683|bbdd71ab86ec2c5de959160c33c934d7"

# --- Konfiguration ---
STADT = "Hamburg, Germany"
STRASSENNAME = "Fuhlsbüttler Straße"
ABSTAND_M = 100        # Abstand zwischen den Punkten in Metern
EPSG_UTM = 25832      # UTM Zone 32N (für Deutschland)

def get_coords(stadt,straße,abstand,utm):
    # 1. Straßennetz laden
    print("Lade Straßennetz...")
    G = ox.graph_from_place(stadt, network_type="drive")

    # 2. Alle Kanten als GeoDataFrame
    edges = ox.graph_to_gdfs(G, nodes=False)

    # 3. Gewünschte Straße filtern
    strasse = edges[edges["name"] == straße].copy()

    if strasse.empty:
        raise ValueError(f"Straße '{straße}' nicht gefunden. Verfügbare Namen prüfen mit: print(edges['name'].unique())")

    print(f"Gefunden: {len(strasse)} Segmente für '{straße}'")

    # 4. In metrisches CRS projizieren (für genaue Abstände)
    strasse_utm = strasse.to_crs(epsg=utm)
    geom_utm = strasse_utm.geometry.unary_union

    print(f"Gesamtlänge: {geom_utm.length:.0f} m")

    # 5. Punkte gleichmäßig entlang der Geometrie interpolieren
    abstände = np.arange(0, geom_utm.length, abstand)
    punkte_utm = [geom_utm.interpolate(d) for d in abstände]

    print(f"Anzahl interpolierter Punkte: {len(punkte_utm)}")

    # 6. Zurück nach WGS84 transformieren
    punkte_gdf = gpd.GeoDataFrame(geometry=punkte_utm, crs=utm)
    punkte_wgs84 = punkte_gdf.to_crs(epsg=4326)

    # 7. Ergebnis ausgeben
    #print("\n--- Koordinaten ---")
    #for i, punkt in enumerate(punkte_wgs84.geometry):
    #    print(f"Punkt {i+1:3d}: lat={punkt.y:.6f}, lon={punkt.x:.6f}")
        
    # 8. Ergebnisse in Liste speichern
    liste_coords=[]
    for i,punkt in enumerate(punkte_wgs84.geometry):
        liste_coords.append([i+1,punkt.y,punkt.x])
    print(liste_coords)
    return liste_coords

def get_mapillary_images(lat, lon, access_token, radius=3):  # radius als Parameter
    url = "https://graph.mapillary.com/images"
    
    params = {
        "access_token": access_token,
        "fields": "id,geometry,thumb_1024_url,captured_at",
        "lat": lat,
        "lng": lon,
        "radius": radius
    }

    response = requests.get(url, params=params)
    data = response.json()
    
    bilder = data.get("data", [])
    
    if not bilder:
        return None
    
    aktuellstes = max(bilder, key=lambda b: b.get("captured_at", 0))
    return aktuellstes


# Hauptschleife (unchanged above...)
liste = get_coords(STADT, STRASSENNAME, ABSTAND_M, EPSG_UTM)
images = []
RADIEN = [1, 3, 5]

for coord in liste:
    bild = None
    verwendeter_radius = None

    for radius in RADIEN:
        bild = get_mapillary_images(coord[1], coord[2], ACCESS_TOKEN, radius=radius)
        if bild:
            verwendeter_radius = radius
            break

    if bild:
        # Convert millisecond timestamp to ISO 8601
        timestamp_ms = bild["captured_at"]
        timestamp_iso = datetime.utcfromtimestamp(timestamp_ms / 1000).strftime("%Y-%m-%dT%H:%M:%SZ")

        images.append({
            "type": "Feature",
            "geometry": {
                "type": "Point",
                "coordinates": [coord[2], coord[1]]  # GeoJSON uses [lon, lat]
            },
            "properties": {
                "image_id": bild["id"],
                "image_url": bild["thumb_1024_url"],
                "timestamp": timestamp_iso,
                "overall_severity": None,   # to be filled later
                "detections": []            # to be filled later
            }
        })
    else:
        print(f"Punkt {coord[0]}: Kein Bild gefunden (auch nicht bei {max(RADIEN)}m)")

# Build GeoJSON FeatureCollection
geojson_output = {
    "type": "FeatureCollection",
    "features": images
}

print(f"\n{len(images)} Bilder gefunden")
print(json.dumps(geojson_output, indent=2, ensure_ascii=False))

# Optional: save to file
with open("output.geojson", "w", encoding="utf-8") as f:
    json.dump(geojson_output, f, indent=2, ensure_ascii=False)
    print("GeoJSON gespeichert: output.geojson")
    