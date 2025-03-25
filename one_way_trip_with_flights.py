def one_way_trip_with_flights(residency, destination_city_arrival, destination_city_departure, earliest_departure_date, latest_departure_date, earliest_return_date, latest_return_date, minimum_days, maximum_days):
    from find_kayak_airports import find_kayak_airports
    from find_flight_price import find_flight_price

    import pandas as pd
    from datetime import datetime, timedelta


    residency_city_code,_,_,_ = find_kayak_airports(residency)
    destination_city_arrival_code,_,_,_ = find_kayak_airports(destination_city_arrival)
    destination_city_departure_code, _,_,_ = find_kayak_airports(destination_city_departure)


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


    flight_prices["price_departure"]=None
    flight_prices["price_return"]=None


    # Cache for storing flight prices
    price_cache = {}

    # Function to get cached flight price or compute it
    def get_price_with_cache(origin, destination, date, cache):
        key = (origin, destination, date)
        if key not in cache:
            cache[key] = find_flight_price(origin, destination, date, return_date=None)
        return cache[key]

    # Fill prices using cache
    for index, row in flight_prices.iterrows():
        # Departure price
        flight_prices.loc[index, "price_departure"] = get_price_with_cache(
            residency_city_code,
            destination_city_arrival_code,
            row["date_departure"],
            price_cache
        )
        
        # Return price
        flight_prices.loc[index, "price_return"] = get_price_with_cache(
            destination_city_departure_code,
            residency_city_code,
            row["date_return"],
            price_cache
        )

        # find the best dates to fly
    flight_prices["total_price"] = flight_prices["price_departure"] + flight_prices["price_return"]
    best_flight_dates = flight_prices.sort_values(by="total_price", ascending=True).head(5)

    return best_flight_dates