from faker import Faker
from presidio_anonymizer.entities import OperatorConfig

fake = Faker()


def fake_pnr(_=None):
    return fake.bothify(text="?#?###").upper()


def fake_e_ticket(_=None):
    return fake.bothify(text="###-#########").upper()


def fake_registration(_=None):
    return fake.bothify(text="######").upper()


def fake_iata_aircraft(_=None):
    return fake.bothify(text="###").upper()


def fake_icao_aircraft(_=None):
    return fake.bothify(text="####").upper()


def fake_iata_airline(_=None):
    return fake.bothify(text="##").upper()


def fake_icao_airline(_=None):
    return fake.bothify(text="###").upper()


def fake_ticketing_prefix(_=None):
    return fake.bothify(text="#####").upper()


def fake_iata_airport(_=None):
    return fake.bothify(text="#####").upper()


def fake_icao_airport(_=None):
    return fake.bothify(text="#####").upper()


def fake_faa_airport(_=None):
    return fake.bothify(text="#####").upper()


def fake_us_driver_license(_=None):
    return fake.bothify(
        text="D#?###-###"
    ).upper()  # Example format for US driver's license


def fake_date_time(_=None):
    return fake.date_time_this_decade().strftime("%Y-%m-%d %H:%M:%S")


def fake_person(_=None):
    return fake.name()


def fake_email(_=None):
    return fake.email()


def fake_phone_number(_=None):
    return fake.phone_number()


def create_fake_data_operators():
    return {
        "PNR": OperatorConfig("custom", {"lambda": fake_pnr}),
        "E-TICKET": OperatorConfig("custom", {"lambda": fake_e_ticket}),
        "REGISTRATION": OperatorConfig("custom", {"lambda": fake_registration}),
        "IATA_AIRCRAFT": OperatorConfig("custom", {"lambda": fake_iata_aircraft}),
        "ICAO_AIRCRAFT": OperatorConfig("custom", {"lambda": fake_icao_aircraft}),
        "IATA_AIRLINE": OperatorConfig("custom", {"lambda": fake_iata_airline}),
        "ICAO_AIRLINE": OperatorConfig("custom", {"lambda": fake_icao_airline}),
        "TICKETING_PREFIX": OperatorConfig("custom", {"lambda": fake_ticketing_prefix}),
        "IATA_AIRPORT": OperatorConfig("custom", {"lambda": fake_iata_airport}),
        "ICAO_AIRPORT": OperatorConfig("custom", {"lambda": fake_icao_airport}),
        "FAA_AIRPORT": OperatorConfig("custom", {"lambda": fake_faa_airport}),
        "US_DRIVER_LICENSE": OperatorConfig(
            "custom", {"lambda": fake_us_driver_license}
        ),
        "DATE_TIME": OperatorConfig("custom", {"lambda": fake_date_time}),
        "PERSON": OperatorConfig("custom", {"lambda": fake_person}),
        "EMAIL_ADDRESS": OperatorConfig("custom", {"lambda": fake_email}),
        "PHONE_NUMBER": OperatorConfig("custom", {"lambda": fake_phone_number}),
    }
