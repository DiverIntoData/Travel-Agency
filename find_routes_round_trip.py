def find_routes_round_trip(cities_to_visit, road_trip, origin, final_destination, trip_mode, transit_mode, API_KEY):
    import pandas as pd
    import requests
    import itertools

    """
    This function find the best route by car, rail... using Google Maps service.
    It returns all the possible itineraries as a dataframe

    Variables:
        - cities_to_visit: touple
        - road_trip: if the trip is a road_trip from your residency
        - origin: if the user knows where to start the trip??
        - final_destination: if user wants to return to the starting point or not.
        - trip_mode: driving, bicycing, public transit
        - transit_mode: rail, bus
    """

    # Generate all itinerary permutations
    potential_routes = list(itertools.permutations(cities_to_visit))

    # Adjust the routes based on user inputs
    if road_trip in ['yes', 'y']:
        potential_routes = [origin + perm + final_destination for perm in potential_routes]
    elif origin:  # Add origin only if it exists
        potential_routes = [origin + perm for perm in potential_routes]


    ##################
    # Function to remove duplicates from a tuple while preserving the final destination
    def remove_duplicates_keep_final(itinerary):
        seen = set()
        # Process all elements except the last one (final_destination)
        main_route = tuple(x for x in itinerary[:-1] if not (x in seen or seen.add(x)))
        # Add the final destination back
        return main_route + (itinerary[-1],)

    # Modify potential_routes directly
    potential_routes = [remove_duplicates_keep_final(route) for route in potential_routes]

    ##################


    # Define your API key and endpoint
    base_url = "https://maps.googleapis.com/maps/api/distancematrix/json"

    # Initialize a cache dictionary
    cache = {}

    # Initialize an empty list to store results
    results = []

    # Iterate over each itinerary
    for route in potential_routes:
        route_times = []
        for i in range(len(route) - 1):  # Iterate through each leg of the route
            origin = route[i]
            destination = route[i + 1]
            leg_key = (origin, destination)  # Create a unique key for this leg
            
            # Check if the leg has already been queried
            if leg_key in cache:
                # Use the cached result
                time_in_hours = cache[leg_key]
            else:
                # Set up API parameters
                params = {
                    "origins": origin,
                    "destinations": destination,
                    "units": "metric",      # metric or imperial
                    "key": API_KEY,
                    "mode": trip_mode,      # driving, walking, bicycling, transit
                    "transit_mode": transit_mode,       # bus, rail (train|tram|subway)
                    "transit_routing_preference": "less_walking"  # less_walking, fewer_transfers
                }

                # API request
                response = requests.get(base_url, params=params)
                info = response.json()

                try:
                    # Extract time in hours
                    time_to_destination = info["rows"][0]["elements"][0]["duration"]["value"]  # Time in seconds
                    time_in_hours = time_to_destination / 3600
                except:
                    time_in_hours = None  # If API fails, record None
                
                # Cache the result
                cache[leg_key] = time_in_hours
            
            # Append time for this leg
            route_times.append(time_in_hours)
        
        # Append this route's data to the results
        results.append(route_times)

    # Dynamically determine the maximum number of legs
    max_legs = max(len(route) - 1 for route in potential_routes)

    # Create dynamic column names
    columns = [f'Leg {i + 1}' for i in range(max_legs)]

    # Fill missing values for routes with fewer legs
    padded_results = [route_times + [None] * (max_legs - len(route_times)) for route_times in results]

    # Convert results into a DataFrame
    travel_times_df = pd.DataFrame(padded_results, columns=columns)

    # Add itineraries as a column for reference
    travel_times_df['Itinerary'] = potential_routes

    # Identify columns that start with "Leg "
    leg_columns = [col for col in travel_times_df.columns if col.startswith("Leg ")]

    # Sum the "Leg " columns row-wise and create a new column
    travel_times_df['Total Travel Time (hrs)'] = travel_times_df[leg_columns].sum(axis=1)

    # If we are asking for a round trip, it will create multiple additional itineraries without the final destination.
    # In practial efects, it doesn't matter because when we calculate the sum of times the column with NaN will not be computed.
    # However, it is best to clean the table and drop rows with NaN
    if road_trip in ['yes', 'y']:
    # If it's a round trip, remove rows with NaN values
        travel_times_df_cleaned = travel_times_df.dropna()
    else:
        # If it's not a round trip, remove rows without NaN values
        travel_times_df_cleaned = travel_times_df[travel_times_df.isna().any(axis=1)]

    # Display the dataframe
    return travel_times_df


def find_sortest_route(travel_times_df):
    shortest_route = travel_times_df[travel_times_df["Total Travel Time (hrs)"] == travel_times_df["Total Travel Time (hrs)"].min()]
    return shortest_route
