# Function to find the best rute from a road trip starting and ending at residency

def road_trip_function(cities_to_visit, road_trip, origin, final_destination, trip_mode, transit_mode, API_KEY):
    from find_routes import find_routes
    from find_routes import find_sortest_route

    potential_routes = find_routes(cities_to_visit, road_trip, origin, final_destination, trip_mode, transit_mode, API_KEY)
    shortest_route = find_sortest_route(potential_routes)

    # Create a map of the trip
    import urllib.parse
    from IPython.display import display, HTML

    # Extract the best itinerary from your data
    best_itinerary = list(shortest_route["Itinerary"][shortest_route.index[0]])  # From the table shortest_route, get the information in Itinerary, and extract the information in the first index
    print(f"Best Itinerary: {best_itinerary}")


    # Generate the Embed URL for Google Maps Directions
    base_url = "https://www.google.com/maps/embed/v1/directions"
    origin = urllib.parse.quote(best_itinerary[0])  # Start location
    destination = urllib.parse.quote(best_itinerary[-1])  # End location
    waypoints = '|'.join(urllib.parse.quote(city) for city in best_itinerary[1:-1])  # Intermediate cities

    embed_url = f"{base_url}?key={API_KEY}&origin={origin}&destination={destination}"
    if waypoints:
        embed_url += f"&waypoints={waypoints}"

    # Create the iframe HTML
    iframe_html = f"""
    <iframe
        src="{embed_url}"
        width="1000px"
        height="700px"
        style="border:0;"
        allowfullscreen=""
        loading="lazy">
    </iframe>
    """

    # Display the iframe in the notebook
    html_map_route = HTML(iframe_html)
    
    
    return potential_routes, shortest_route, best_itinerary, html_map_route
