from presidio_analyzer import Pattern, PatternRecognizer


def create_travel_specific_recognizers() -> list[PatternRecognizer]:
    recognizers = []

    # PNR Recognizer
    pnr_pattern = Pattern(
        name="pnr_pattern", regex=r"[A-Z0-9]{5}\d{1}", score=1
    )  # Adjusted score
    recognizers.append(
        PatternRecognizer(
            supported_entity="PNR",
            patterns=[pnr_pattern],
            context=["PNR", "PNRs", "PNR codes"],
        )
    )

    # E-TICKET Recognizer
    ticket_pattern = Pattern(
        name="e-ticket_pattern", regex="[0-9]{3}(-)?[0-9]{10}", score=1
    )  # Adjusted score
    recognizers.append(
        PatternRecognizer(
            supported_entity="E-TICKET",
            patterns=[ticket_pattern],
            context=["e-ticket", "ticket number"],
        )
    )

    # Aircraft Registrations
    registration_pattern = Pattern(
        name="registration_pattern",
        regex="^[A-Z]-[A-Z]{4}|[A-Z]{2}-[A-Z]{3}|N[0-9]{1,5}[A-Z]{0,2}$",
        score=1,
    )  # Adjusted score
    recognizers.append(
        PatternRecognizer(
            supported_entity="REGISTRATION",
            patterns=[registration_pattern],
            context=["registration", "registration number"],
        )
    )

    # IATA Aircraft Type
    iata_aircraft_pattern = Pattern(
        name="iata_aircraft_pattern", regex="^[A-Z0-9]{3}$", score=1
    )  # Adjusted score
    recognizers.append(
        PatternRecognizer(
            supported_entity="IATA_AIRCRAFT",
            patterns=[iata_aircraft_pattern],
            context=["IATA aircraft type", "aircraft type"],
        )
    )

    # ICAO Aircraft Type
    icao_aircraft_pattern = Pattern(
        name="icao_aircraft_pattern", regex="^[A-Z]{1}[A-Z0-9]{1,3}$", score=1
    )  # Adjusted score
    recognizers.append(
        PatternRecognizer(
            supported_entity="ICAO_AIRCRAFT",
            patterns=[icao_aircraft_pattern],
            context=["ICAO aircraft type"],
        )
    )

    icao_airline_pattern = Pattern(
        name="icao_airline_pattern", regex="^[A-Z]{3}$", score=1
    )  # Adjusted score
    recognizers.append(
        PatternRecognizer(
            supported_entity="ICAO_AIRLINE",
            patterns=[icao_airline_pattern],
            context=["ICAO airline code", "operational code"],
        )
    )

    # Ticketing Prefix
    ticketing_prefix_pattern = Pattern(
        name="ticketing_prefix_pattern", regex="^[0-9]{3}$", score=1
    )  # Adjusted score
    recognizers.append(
        PatternRecognizer(
            supported_entity="TICKETING_PREFIX",
            patterns=[ticketing_prefix_pattern],
            context=["ticketing prefix", "eTicket operator code"],
        )
    )

    # Airport Codes
    iata_airport_pattern = Pattern(
        name="iata_airport_pattern", regex="^[A-Z]{3}$", score=1
    )  # Adjusted score
    recognizers.append(
        PatternRecognizer(
            supported_entity="IATA_AIRPORT",
            patterns=[iata_airport_pattern],
            context=["IATA airport code", "airport code"],
        )
    )

    icao_airport_pattern = Pattern(
        name="icao_airport_pattern", regex="^[A-Z]{4}$", score=1
    )  # Adjusted score
    recognizers.append(
        PatternRecognizer(
            supported_entity="ICAO_AIRPORT",
            patterns=[icao_airport_pattern],
            context=["ICAO airport code"],
        )
    )

    faa_airport_pattern = Pattern(
        name="faa_airport_pattern", regex="^[A-Z0-9]{3,4}$", score=1
    )  # Adjusted score
    recognizers.append(
        PatternRecognizer(
            supported_entity="FAA_AIRPORT",
            patterns=[faa_airport_pattern],
            context=["FAA airport code", "US FAA-specific locator"],
        )
    )

    return recognizers
