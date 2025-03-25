# Function to find the best rute from a road trip starting and ending at residency

def road_trip_round_trip_function(residency, cities_to_visit, trip_mode, transit_mode, road_trip, API_KEY, earliest_departure_date, latest_departure_date, earliest_return_date, latest_return_date, minimum_days, maximum_days):

    import pandas as pd
    from datetime import datetime, timedelta
    import requests
    from find_routes_round_trip import find_sortest_route, find_routes_round_trip
    #########   Create all the possible combinations of flight dates


    # # Parse date strings into datetime objects
    # earliest_departure_date = datetime.strptime(earliest_departure_date, "%Y-%m-%d")
    # latest_departure_date = datetime.strptime(latest_departure_date, "%Y-%m-%d")

    # earliest_return_date = datetime.strptime(earliest_return_date, "%Y-%m-%d")
    # latest_return_date = datetime.strptime(latest_return_date, "%Y-%m-%d")

    # Create a list to hold all valid departure and return date combinations
    trip_dates = []

    # Generate all possible departure dates
    current_departure_date = earliest_departure_date
    while current_departure_date <= latest_departure_date:
        # For each departure date, generate return dates within the allowed window
        min_return_date = current_departure_date + timedelta(days=minimum_days)
        max_return_date = current_departure_date + timedelta(days=maximum_days)
        
        # Ensure return dates are within the valid return date range
        valid_return_date_start = max(min_return_date, earliest_return_date)
        valid_return_date_end = min(max_return_date, latest_return_date)
        
        # If valid return date range exists, add to the list
        if valid_return_date_start <= valid_return_date_end:
            current_return_date = valid_return_date_start
            while current_return_date <= valid_return_date_end:
                # Add the combination of departure and return date
                trip_dates.append((current_departure_date.strftime("%Y-%m-%d"), current_return_date.strftime("%Y-%m-%d")))
                current_return_date += timedelta(days=1)
        
        # Move to the next departure date
        current_departure_date += timedelta(days=1)

    # Create a DataFrame from the routes list
    flight_prices = pd.DataFrame(trip_dates, columns=["date_departure", "date_return"])


    # Add columns to the DataFrame dynamically for each city
    for city in cities_to_visit:
        column_name = f"price_round_ticket_{city}"
        flight_prices[column_name] = None  # Initialize with None or a default value
        
    ############### 


    from find_kayak_airports import find_kayak_airports
    from find_flight_price import find_flight_price


    # Get residency city airport code
    residency_city_code, _, _, _ = find_kayak_airports(residency)

    # Add columns dynamically for each city
    for city in cities_to_visit:
        column_name = f"price_round_ticket_{city}"
        flight_prices[column_name] = None  # Initialize with None

        # Get destination city airport code
        destination_city_arrival_code, _, _, _ = find_kayak_airports(city)

        # Populate the column with round-trip prices
        for index, row in flight_prices.iterrows():
            # Extract departure and return dates
            flight_departure_date = row["date_departure"]
            flight_return_date = row["date_return"]

            # Calculate flight price
            departure_price = find_flight_price(
                residency_city_code,
                destination_city_arrival_code,
                flight_departure_date,
                flight_return_date,
            )

            # Update the column for the specific city
            flight_prices.loc[index, column_name] = departure_price

    ##################     Find the best flights to take     #######################

    # Create a new list with the required format for column names
    cities_to_visit_prices = ["price_round_ticket_" + city for city in cities_to_visit]

    # Handle missing values by replacing NaN with a large value for proper comparison
    flight_prices[cities_to_visit_prices] = flight_prices[cities_to_visit_prices].fillna(float('inf'))

    # Find the minimum price for each row across the cities
    flight_prices['min_price'] = flight_prices[cities_to_visit_prices].min(axis=1)

    # Ensure 'min_price' column is numeric and handle errors or invalid values
    flight_prices['min_price'] = pd.to_numeric(flight_prices['min_price'], errors='coerce')

    # Replace NaN values (if any) with a large value (e.g., inf)
    flight_prices['min_price'] = flight_prices['min_price'].fillna(float('inf'))

    # Now you can safely use nsmallest
    top_5_cheapest_flights = flight_prices.nsmallest(5, 'min_price')



    # Extract relevant details: origin (residency), destination (city name), dates, and price
    top_5_cheapest_flights_info = []

    for index, row in top_5_cheapest_flights.iterrows():
        # Find the city with the minimum price by referencing the price columns
        min_price_city_column = row[cities_to_visit_prices].idxmin()  # Get the column name with the min price
        
        # Extract the city name from the column name (last word after 'price_round_ticket_')
        min_price_city = min_price_city_column.split('_')[-1]
        
        departure_date = row['date_departure']
        return_date = row['date_return']
        price = row[min_price_city_column]
        
        # Convert the departure and return dates from string to datetime
        departure_date_dt = pd.to_datetime(departure_date)
        return_date_dt = pd.to_datetime(return_date)
        
        # Calculate total trip days
        total_trip_days = (return_date_dt - departure_date_dt).days
        
        # Create a dictionary with the desired information
        top_5_cheapest_flights_info.append({
            "origin": residency,  # Assuming 'residency' is defined somewhere
            "destination": min_price_city,
            "date_departure": departure_date,
            "date_return": return_date,
            "price": price,
            "total trip days": total_trip_days
        })

    # Display the results
    top_5_cheapest_flights_info_df = pd.DataFrame(top_5_cheapest_flights_info)

    ############# Find out the origin and final_destination of your round trip      ###############3
    origin = top_5_cheapest_flights_info_df["destination"][0]       # Get the city for the round tip by car
    final_destination = top_5_cheapest_flights_info_df["destination"][0]       # Get the city for the round tip by car 


    cities_to_visit_list = list(cities_to_visit)
    cities_to_visit_list.remove(origin)     # Remove the origin and final_destination, in order to compute the permutations, and then add them at the begining or end

    import itertools

    potential_routes = list(itertools.permutations(cities_to_visit_list))

    potential_routes = [(origin,) + perm + (final_destination,) for perm in potential_routes]       # Need to add origin and final_destination ad tuples, as potential routes are in tuples

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
            origin_trip = route[i]
            destination = route[i + 1]
            leg_key = (origin_trip, destination)  # Create a unique key for this leg
            
            # Check if the leg has already been queried
            if leg_key in cache:
                # Use the cached result
                time_in_hours = cache[leg_key]
            else:
                # Set up API parameters
                params = {
                    "origins": origin_trip,
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


    shortest_route = find_sortest_route(travel_times_df)


    ####################    Create a map        ###################
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
    
    
    return flight_prices, travel_times_df, shortest_route, top_5_cheapest_flights_info_df, best_itinerary, html_map_route