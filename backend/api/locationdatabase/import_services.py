"""This module is used to populate a database automatically with given csv files."""
import csv
import glob
import logging
import re
import requests
from typing import Optional

from dotenv import load_dotenv
import geocoder
from pprint import pprint

from api.locationdatabase import LocationDatabase


load_dotenv()
logger = logging.getLogger(__name__)
csv_pattern = r"([^/]+)\.csv$"

# A dictionary mapping from region names to its regionID
region_ids = {}

def populate_service_database(db: LocationDatabase, dir_path: str) -> None:
    """Populate the services database with the .csv files in the given directory.
    
    dir_path is the file path to a directory containing .csv files. Each .csv 
    file is structured with a header line followed by entries. Each entry has 
    four attributes in the following order:
        1. url: The MyAutism webpage for more information about the service;
        2. organisation: The name of the service;
        3. address: The physical address of the service; and
        4. phone: The phone number of the service.

    Args:
        dir_path: The file path to the directory.
        db: The service database which is populated.
    """
    for filepath in glob.glob(dir_path + "/*.csv"):
        logger.info(f"populate_service_database: importing from file {filepath}")
        match = re.search(csv_pattern, filepath)
        _import_services(filepath, match.group(1), db)


def _import_services(filepath: str, service_type: str, db: LocationDatabase) -> None:
    """Insert the services within the .csv file into the given database.

    The csv file is structured with a header line followed by entries. Each 
    entry has four attributes in the following order:
        1. url: The MyAutism webpage for more information about the service;
        2. organisation: The name of the service;
        3. address: The physical address of the service; and
        4. phone: The phone number of the service.

    Args:
        filepath: The file path of the .csv file containing services.
        service_type: The type of services contained within the csv file.
        db: The service database which is populated.
    """
    with open(filepath) as csvfile:
        reader = csv.reader(csvfile)
        next(reader)  # skip header line
        with requests.Session() as session:
            for row in reader:
                address = row[2]
                try:
                    geocode = geocoder.google(address, session=session)
                    if geocode.ok:
                        region_id = _insert_regions(db,
                                                    geocode.city,
                                                    geocode.county,
                                                    geocode.state,
                                                    geocode.country)
                        if region_id == -1:
                            logger.warning(f"_import_services: could not insert region based on address, skipping...")
                            continue
                        res = db.insert_service(row[1], 
                                                service_type, 
                                                region_id, 
                                                geocode.lat, 
                                                geocode.lng, 
                                                geocode.address, 
                                                row[3], 
                                                row[0])
                        if not res:
                            logger.warning(f"_import_services: failed to insert address {geocode.address} from csv file {filepath}.")
                except Exception as e:
                    logger.error(f"_import_services: {e}")


def _insert_regions(db: LocationDatabase,
                    city: str, 
                    county: str, 
                    province: str, 
                    country: str) -> int:
    """Insert the given city regions into the database.

    The four attributes (country, province, county, city) collectively
    describe a regional locality under several administrative areas, where
    city is in county, county is in province, etc.

    Args:
        db: The service database which is populated.
        city: The name of the city.
        county: The name of the greater adminstrative area that the city is located within.
        province: The name of the greater administrative area that the county is located within.
        country: The name of the country that the city is in.
    Returns:
        int: The regionID of the inserted city if successful. If not, then -1 is returned instead.
    """
    country_id = _insert_region(db, country, "Country", None)
    province_id = _insert_region(db, province, "Province", country_id)
    county_id = _insert_region(db, county, "County", province_id)
    city_id = _insert_region(db, city, "City", county_id)
    
    return city_id if city_id is not None else -1


def _insert_region(db: LocationDatabase, name: str, type: str, parent_id: Optional[int]):
    """Insert the given regions into the database.
    
    Args:
        db: The service database which is populated.
        name: The name of the region.
        type: The region type, e.g. city, county, province, or country.
        parent_id: The regionID of the greater administrative area that the region is part of.
    """
    if name == "None":
        logger.warning(f"_insert_regions: Using default latitude and longitude (0, 0) for region {name}.")
        lat, lng = 0, 0
    else:
        geocode = geocoder.google(name, maxRows=1, components="country:CA|country:US")
        if geocode.ok and geocode.lat is not None and geocode.lng is not None:
            lat, lng = geocode.lat, geocode.lng
        else:
            logger.error(f"_insert_regions: Couldn't determine latitude and longitude of region {name}.")
            lat, lng = 0, 0

    res = db.insert_region(name, type, parent_id, lat, lng)
    if not res:
        logger.error(f"_insert_regions: Couldn't insert region {name} as a {type}.")
        return None
    else:
        region_ids[name] = db.region_id(name, type)
        return region_ids[name]


if __name__ == "__main__":
    # example usage. To execute, run the command
    # python -m api.locationdatabase.import_services
    # in the backend/ directory.
    from api.locationdatabase.sqlitelocationdatabase import SQLiteLocationDatabase

    database = SQLiteLocationDatabase()
    database.initialize_database()

    populate_service_database(database, "./tests/csv")