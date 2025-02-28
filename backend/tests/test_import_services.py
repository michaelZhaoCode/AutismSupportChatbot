# pylint: disable=missing-module-docstring, redefined-outer-name
import pytest

from api.locationdatabase.sqlitelocationdatabase import SQLiteLocationDatabase
from api.locationdatabase.import_services import populate_service_database


@pytest.fixture(scope="module")
def populated_small_database():
    dbpath = "test_locations.sqlite"
    db = SQLiteLocationDatabase(dbpath)
    db.initialize_database()

    populate_service_database(db, "tests/csv/small")
    yield db

    db.clear_database()

@pytest.fixture
def inserted_regions(populated_small_database):
    return {region["RegionName"] :
            {key : region[key] for key in region.keys() if key != "RegionName"}
            for region in populated_small_database.find_all_regions()}

@pytest.fixture
def region_ids(populated_small_database):
    return {region["RegionID"]
            for region in populated_small_database.find_all_regions()}

@pytest.fixture
def inserted_services(populated_small_database):
    return {(service["ServiceName"]) :
                {key : service[key] for key in service.keys()
                 if key != "ServiceName"}
            for service in populated_small_database.find_all_services()}


@pytest.mark.parametrize("service", [
    "ABC Dental",
    "Alderlea Dental Health Centre",
    "Applebay Family Dental",
    "ABC Solutions Inc.",
    "Aboriginal Family Centre",
    "Access Learning",
    "ACCESS Speech & Language Services",
    "Accomplished Learning Centre"
])
def test_all_services(inserted_services, service):
    assert service in inserted_services


def test_valid_regions(region_ids, populated_small_database):
    assert all(service["RegionID"] in region_ids
               for service in populated_small_database.find_all_services())


def test_service_types(populated_small_database):
    service_types = populated_small_database.get_all_service_types()
    assert all(service_type in {"Dentist", "Education"}
               for service_type in service_types)


@pytest.mark.parametrize("path", [
    ("CA", "NT", "North Slave Region", "Yellowknife"),
    ("CA", "YT", "Whitehorse"),
    ("CA", "BC", "Fraser Valley", "Mission"),
    ("CA", "BC", "Cowichan Valley", "Duncan"),
    ("CA", "ON", "Regional Municipality of Niagara", "Niagara Falls"),
    ("CA", "QC", "Montréal", "Dollard-des-Ormeaux"),
    ("CA", "NL", "Happy Valley-Goose Bay"),
    ("CA", "ON", "Simcoe County", "Barrie"),
    ("CA", "BC", "CRD", "Victoria"),
    ("CA", "BC", "Metro Vancouver", "Langley")
])
def test_all_paths(inserted_regions, path):
    assert all(region in inserted_regions for region in path)

    for i in range(len(path)):
        region = inserted_regions[path[i]]
        if i == 0:
            assert region["ParentRegionID"] is None
        else:
            parent_region = inserted_regions[path[i - 1]]
            assert region["ParentRegionID"] == parent_region["RegionID"]
