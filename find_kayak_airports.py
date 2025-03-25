def find_kayak_airports(city_name):
    import requests

    try:
        # Send the POST request
        response = requests.post(f"https://www.kayak.es/mvm/smartyv2/search?s=58&where={city_name}")
        
        # Raise an exception if the request failed
        response.raise_for_status()

        # Attempt to get the first item from the JSON response
        kayak_airport_city = response.json()[0]

        # Extract the necessary data
        id = kayak_airport_city.get("id", None)
        displayname = kayak_airport_city.get("displayname", None)
        lat = kayak_airport_city.get("lat", None)
        lng = kayak_airport_city.get("lng", None)

        return id, displayname, lat, lng

    except (requests.exceptions.RequestException, ValueError, IndexError) as e:
        # If there's any error (request, JSON parsing, etc.), return None values
        return None, None, None, None