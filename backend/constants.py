"""Contains the constant values used by various parts of the code"""

MAIN_MODEL_USE = "gpt-4o"
SERVICE_MODEL_USE = "gpt-4o-mini"
LOCATION_MODEL_USE = "gpt-4o"

MAX_SERVICES = 5

REGION_TYPE_PRIORITY = {
    "Country": 1,
    "Province": 2,
    "State": 2,
    "City": 3,
}