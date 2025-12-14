import requests

def fetch_static_map(lat, lon, out_path, config):
    url = (
        "https://maps.googleapis.com/maps/api/staticmap"
        f"?center={lat},{lon}"
        f"&zoom={config.ZOOM}"
        f"&size={config.IMG_SIZE}x{config.IMG_SIZE}"
        f"&scale={config.SCALE}"
        f"&maptype=satellite"
        f"&key={config.GOOGLE_MAPS_API_KEY}"
    )
    r = requests.get(url)
    r.raise_for_status()
    with open(out_path, "wb") as f:
        f.write(r.content)
