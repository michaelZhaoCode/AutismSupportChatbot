"""This module is used to populate a database automatically with given csv files."""
import csv
import glob
import logging
import requests
from typing import Optional

from dotenv import load_dotenv
import geocoder
from pprint import pprint

# XXX: don't know why this works but
# from locationdatabase import LocationDatabase doesn't
# or from . import LocationDatabase
from __init__ import LocationDatabase  


load_dotenv()
logger = logging.getLogger(__name__)


def populate_service_database(dir_path: str, db: LocationDatabase) -> None:
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
        _import_services(filepath, db)


def _import_services(filepath: str, db: Optional[LocationDatabase]) -> None:
    """Insert the services within the .csv file into the given database.

    The csv file is structured with a header line followed by entries. Each 
    entry has four attributes in the following order:
        1. url: The MyAutism webpage for more information about the service;
        2. organisation: The name of the service;
        3. address: The physical address of the service; and
        4. phone: The phone number of the service.

    Args:
        filepath: The file path of the .csv file containing services.
        db: The service database which is populated.
    """
    with open(filepath) as csvfile:
        reader = csv.reader(csvfile)
        next(reader)  # skip header line
        with requests.Session() as session:
            for row in reader:
                address = row[2]
                try:
                    geocode = geocoder.google(address, session=session, components="country:CA")
                    if geocode.ok:
                        pprint(geocode.json)
                        region_id = _insert_regions(db,
                                                    geocode.city,
                                                    geocode.county,
                                                    geocode.state,
                                                    geocode.country)
                        res = _insert_service(db,
                                              row[1],
                                              geocode.address,
                                              geocode.lat,
                                              geocode.lng,
                                              region_id,
                                              row[3] if row[3] is not "" else None,
                                              row[0] if row[0] is not "" else None)
                        if not res:
                            logger.warning(f"_import_services: failed to insert address {geocode.address} from csv file {filepath}")
                except Exception as e:
                    logger.error(f"_import_services: {e}")


def _insert_regions(db: LocationDatabase,
                    city: str, 
                    county: str, 
                    province: str, 
                    country: str) -> int:
    """..."""
    raise NotImplementedError

    # TODO: complete the region insertion part
    if country is not "None":
        ...
    if province is not "None":
        ...
    if county is not "None":
        ...
    if city is not "None":
        ...


def _insert_service(db: LocationDatabase,
                    name: str, 
                    address: Optional[str],
                    lat: float,
                    long: float,
                    region_id: int,
                    phone: Optional[str],
                    website: Optional[str]) -> bool:
    """TODO: write this docstring"""

    # TODO: complete the service insertion part
    raise NotImplementedError


if __name__ == "__main__":
    _import_services("api/servicehandler/services/csv/Education.csv")