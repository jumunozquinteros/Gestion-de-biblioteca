import requests
import urllib.parse

geocode_url = "https://graphhopper.com/api/1/geocode?"
route_url = "https://graphhopper.com/api/1/route?"
API_KEY = "c9c9a768-0f84-4744-b4a6-8dd502b121c9"


def normalize_location(hit, fallback):
    name = hit.get("name", fallback)
    country = hit.get("country", "")
    state = hit.get("state", "")

    if state and country:
        return f"{name}, {state}, {country}"
    if country:
        return f"{name}, {country}"
    return name


def geocoding(location, key):
    while location is None or location.strip() == "":
        location = input("Por favor, ingrese una ubicación válida: ").strip()

    params = {
        "q": location,
        "limit": 1,
        "key": key
    }
    url = geocode_url + urllib.parse.urlencode(params)

    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
    except requests.RequestException as e:
        print(f"Error de conexión al geocodificar: {e}")
        return None

    hits = data.get("hits", [])
    if not hits:
        print(f"No se encontraron resultados para: {location}")
        return None

    hit = hits[0]
    point = hit.get("point", {})
    lat = point.get("lat")
    lng = point.get("lng")

    if lat is None or lng is None:
        print(f"No se pudo obtener coordenadas para: {location}")
        return None

    formatted_location = normalize_location(hit, location)
    print(f"Coordenadas obtenidas correctamente para: {formatted_location}")
    print(f"Tipo de ubicación: {hit.get('osm_value', 'desconocido')}")
    print(f"URL de geocodificación: {url}")

    return {
        "lat": lat,
        "lng": lng,
        "name": formatted_location
    }


def get_route(origin_coords, destination_coords, key):
    params = {
        "point": [
            f"{origin_coords['lat']},{origin_coords['lng']}",
            f"{destination_coords['lat']},{destination_coords['lng']}"
        ],
        "vehicle": "car",
        "locale": "es",
        "key": key
    }

    url = route_url + urllib.parse.urlencode(params, doseq=True)

    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
    except requests.RequestException as e:
        print(f"Error de conexión al calcular la ruta: {e}")
        return None

    if response.status_code != 200:
        print("Error al solicitar la ruta.")
        print(f"Código de estado: {response.status_code}")
        print(f"Mensaje: {data.get('message', 'Error desconocido')}")
        return None

    paths = data.get("paths", [])
    if not paths:
        print("La API no devolvió una ruta válida.")
        return None

    return data


def print_route_summary(route_data, origen, destino):
    path = route_data["paths"][0]
    distancia_km = round(path["distance"] / 1000, 2)
    duracion_min = round(path["time"] / 60000, 2)

    print(f"\n🛣️ Ruta desde {origen} hasta {destino}:")
    print(f"📏 Distancia total: {distancia_km} km")
    print(f"⏱️ Duración estimada: {duracion_min} minutos")

    instructions = path.get("instructions", [])
    if not instructions:
        print("No se encontraron instrucciones para esta ruta.")
        return

    print("\n📌 Instrucciones del viaje:")
    for paso in instructions:
        texto = paso.get("text", "Instrucción sin texto")
        distancia = round(paso.get("distance", 0) / 1000, 2)
        duracion = round(paso.get("time", 0) / 60000, 2)
        print(f"- {texto} ({distancia} km, {duracion} min)")


def main():
    while True:
        loc1 = input("Ingrese la ubicación de origen (o 's' para salir): ").strip()
        if loc1.lower() in ["s", "salir"]:
            print("Programa finalizado por el usuario.")
            break

        coords1 = geocoding(loc1, API_KEY)
        if coords1 is None:
            continue

        loc2 = input("Ingrese la ubicación de destino (o 's' para salir): ").strip()
        if loc2.lower() in ["s", "salir"]:
            print("Programa finalizado por el usuario.")
            break

        coords2 = geocoding(loc2, API_KEY)
        if coords2 is None:
            continue

        route_data = get_route(coords1, coords2, API_KEY)
        if route_data is not None:
            print_route_summary(route_data, coords1["name"], coords2["name"])


if __name__ == "__main__":
    main()
