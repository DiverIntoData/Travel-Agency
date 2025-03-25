def generate_itinerary_summary(residency, best_itinerary, round_trip):
    """Generates a concise summary of the trip itinerary with proper formatting."""

    if not best_itinerary or len(best_itinerary) < 1:
        return "Itinerary data is missing or incomplete."

    arrival_city = best_itinerary[0].title()  # First city visited
    return_city = best_itinerary[-1].title()  # Last city before returning home

    # Extract land trip cities correctly (excluding first arrival and last return)
    land_routes = [city.title() for city in best_itinerary[1:-1]]

    # Properly format the road trip section
    if land_routes:
        road_trip_part = f"{arrival_city} → " + " → ".join(land_routes) + f" → {return_city}"
    else:
        road_trip_part = f"{arrival_city} → {return_city}"  # Direct travel

    if round_trip.strip().lower() == "one way":
        if len(best_itinerary) == 1:  # Only one destination, no land trip
            summary = (
                f"✈️ **Departure from** {residency.title()} → **Flight to** {arrival_city}.  \n"
                "🚗 **Road trip**: You are only visiting one city.  \n"
                f"🏁 **Return flight from** {return_city} → **Flight to** {residency}."
            )
        else:
            summary = (
                f"✈️ **Departure from** {residency.title()} → **Flight to** {arrival_city}.  \n"
                f"🚗 **Road trip**: {road_trip_part}.  \n"
                f"🏁 **Return flight from** {return_city} → **Flight to** {residency}."
            )

    elif round_trip.strip().lower() == "round trip":
        if not land_routes:  # No land trip, direct return flight
            summary = (
                f"✈️ **Departure from** {residency.title()} → **Flight to** {arrival_city}.  \n"
                "🚗 **Road trip**: You are only visiting one city.  \n"
                f"🏁 **Return flight from** {return_city} → **Flight to** {residency.title()}."
            )
        else:
            summary = (
                f"✈️ **Departure from** {residency.title()} → **Flight to** {arrival_city}.  \n"
                f"🚗 **Road trip**: {road_trip_part}.  \n"
                f"🏁 **Return flight from** {return_city} → **Flight to** {residency.title()}."
            )

    else:
        summary = "Invalid trip type detected."

    return summary
