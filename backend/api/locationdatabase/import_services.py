"""This module is used to populate the location services database automatically 
with given csv files.
"""
import csv
import glob
import logging
import re
import time
from typing import Optional

import requests
from requests.exceptions import RequestException
import geocoder

from api.locationdatabase import LocationDatabase, RegionAlreadyExistsException

CSV_PATTERN = r"([^/]+)\.csv$"  # used to extract service type from .csv file
DEFAULT_LAT_LONG = (60.000, -95.00)  # default lat, long coordinates for Canada

logger = logging.getLogger(__name__)
region_ids = {}  # A dictionary mapping from region names to its regionID


def populate_service_database(
    db: LocationDatabase,
    dir_path: str
) -> tuple[int, int]:
    """Populate the services database with the .csv files in the given 
    directory.
    
    dir_path is the file path to a directory containing .csv files. Each .csv 
    file is structured with a header line followed by entries. Each entry has 
    four attributes in the following order:
        1. url: The MyAutism webpage for more information about the service;
        2. organisation: The name of the service;
        3. address: The physical address of the service; and
        4. phone: The phone number of the service.

    Returns:
        A tuple (agg_processed, agg_failures).
        agg_processed: The total number of processed services.
        agg_failures: The total number of failures.

    Args:
        dir_path: The file path to the directory.
        db: The service database which is populated.
    """
    agg_processed, agg_failures = 0, 0

    with requests.Session() as session:
        for filepath in glob.glob(dir_path + "/*.csv"):
            logger.info("populate_service_database: importing from file %s",
                        filepath)
            match = re.search(CSV_PATTERN, filepath)
            processed, failures = _import_services(filepath,
                                                   match.group(1),
                                                   db,
                                                   session)
            agg_processed += processed
            agg_failures += failures

    return agg_processed, agg_failures



def _import_services(filepath: str,
                     service_type: str,
                     db: LocationDatabase,
                     session: requests.Session) -> tuple[int, int]:
    """Insert the services within the .csv file into the given database.

    The csv file is structured with a header line followed by entries. Each 
    entry has four attributes in the following order:
        1. url: The MyAutism webpage for more information about the service;
        2. organisation: The name of the service;
        3. address: The physical address of the service; and
        4. phone: The phone number of the service.

    Returns:
        A tuple (processed, failures).
        failures: The number of services that failed to process for any reason.
        processed: The total number of services processed, failed or not.

    Args:
        filepath: The file path of the .csv file containing services.
        service_type: The type of services contained within the csv file.
        db: The service database which is populated.
    """
    processed, failures = 0, 0

    with open(filepath, mode="r", encoding="UTF-8") as csvfile:
        reader = csv.reader(csvfile)
        next(reader)  # skip header line
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
                        logger.warning("_import_services: could not insert "
                                       "region based on address, skipping "
                                       "service")
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
                        logger.warning("_import_services: failed to insert"
                                       "address %s from csv file %s.",
                                       geocode.address, filepath)
                else:
                    logger.warning("_import_services: geocoder: %s, "
                                   "skipping service", geocode.status)
                    failures += 1
                processed += 1
            except RequestException as e:
                logger.error("_import_services: %s", e)

    return processed, failures


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
        county: The name of the greater adminstrative area that the city is 
                located within.
        province: The name of the greater administrative area that the county 
                  is located within.
        country: The name of the country that the city is in.
    Returns:
        int: The regionID of the inserted city if successful. 
             If not, then -1 is returned instead.
    """
    region_order = [(country, "Country"),
                    (province, "Province"),
                    (county, "County"),
                    (city, "City")]
    prev_id, parent_id = -1, None

    for region, region_type in region_order:
        if region is None:
            continue
        elif region in region_ids:
            prev_id = region_ids[region]
        else:
            prev_id = _insert_region(db, region, region_type, parent_id)

        if prev_id != -1:
            parent_id = prev_id

    return prev_id


def _insert_region(db: LocationDatabase,
                   name: str,
                   region_type: str,
                   parent_id: Optional[int]) -> int:
    """Insert the given regions into the database.
    
    Args:
        db: The service database which is populated.
        name: The name of the region.
        type: The region type, e.g. city, county, province, or country.
        parent_id: The regionID of the greater administrative area that 
                   the region is part of.

    Returns:
        int: The id of the inserted region, or -1 if the insertion failed.
    """
    geocode = geocoder.google(name, maxRows=1, components="country:CA")
    if geocode.ok and geocode.lat is not None and geocode.lng is not None:
        lat, lng = geocode.lat, geocode.lng
    else:
        logger.error("_insert_regions: Couldn't determine latitude "
                     "and longitude of region %s.", name)
        lat, lng = DEFAULT_LAT_LONG

    try:
        if db.insert_region(name, region_type, parent_id, lat, lng):
            region_ids[name] = db.region_id(name, region_type)
            return region_ids[name]
        else:
            logger.error("_insert_regions: Couldn't insert region %s as a %s.",
                         name,
                         region_type)
            return -1
    except RegionAlreadyExistsException:
        region_ids[name] = db.region_id(name, region_type)
        return region_ids[name]


if __name__ == "__main__":
    # Example usage. To execute, run the command
    # python -m api.locationdatabase.import_services
    # in the backend/ directory.
    from dotenv import load_dotenv
    from pprint import pprint

    from api.locationdatabase.sqlitelocationdatabase import SQLiteLocationDatabase

    load_dotenv()
    database = SQLiteLocationDatabase()
    database.initialize_database()
    database.clear_database()

    start = time.time()
    processed_services, failed = populate_service_database(database,
                                                            "./tests/csv")
    database.create_snapshot()
    end = time.time()
    pprint(database.find_region_by_path("CA,ON,Toronto"))
    print(f"Time taken for {processed_services} entries: {(end - start)}")
    print(f"Number of failures was {failed} with a "
          f"total failure rate of {(failed / processed_services) * 100}%")
