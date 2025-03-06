# pylint: disable=missing-module-docstring, redefined-outer-name
import pytest
import sqlite3

from api.locationdatabase import RegionAlreadyExistsException
from api.locationdatabase.sqlitelocationdatabase import SQLiteLocationDatabase

@pytest.fixture()
def db():
    db = SQLiteLocationDatabase("test_locations.sqlite")
    db.initialize_database()

    yield db

    db.clear_database()

def test_insert_region(db):
    with sqlite3.connect(db.db_path) as conn:
        cur = conn.cursor()
        cur.execute("SELECT * FROM Regions "
                    "WHERE RegionName = 'CA' AND RegionType = 'Country';")
        assert cur.fetchone() is None

    assert db.insert_region("CA", "Country", None, 0.0, 0.0)

    with sqlite3.connect(db.db_path) as conn:
        cur = conn.cursor()
        cur.execute("SELECT * FROM Regions "
                    "WHERE RegionName = 'CA' AND RegionType = 'Country';")
        assert cur.fetchone() is not None

def test_insert_region_already_exists(db):
    db.insert_region("CA", "Country", None, 0.0, 0.0)
    with pytest.raises(RegionAlreadyExistsException):
        db.insert_region("CA", "Country", None, 0.0, 0.0)

def test_insert_province(db):
    with sqlite3.connect(db.db_path) as conn:
        cur = conn.cursor()
        cur.execute("SELECT * FROM Regions "
                    "WHERE RegionType = 'Province';")
        assert cur.fetchone() is None

    db.insert_region("CA", "Country", None, 0.0, 0.0)
    country_id = db.get_last_inserted_region_id()
    db.insert_province("ON", country_id, 0.0, 0.0)

    with sqlite3.connect(db.db_path) as conn:
        cur = conn.cursor()
        cur.execute("SELECT * FROM Regions "
                    "WHERE RegionType = 'Province';")
        assert cur.fetchone() is not None

def test_insert_province_invalid_parent(db):
    assert not db.insert_province("ON", -1, 0.0, 0.0)

def test_insert_city(db):
    with sqlite3.connect(db.db_path) as conn:
        cur = conn.cursor()
        cur.execute("SELECT * FROM Regions "
                    "WHERE RegionType = 'City';")
        assert cur.fetchone() is None

    db.insert_region("CA", "Country", None, 0.0, 0.0)
    country_id = db.get_last_inserted_region_id()
    db.insert_province("ON", country_id, 0.0, 0.0)
    province_id = db.get_last_inserted_region_id()
    db.insert_city("Toronto", province_id, 0.0, 0.0)

    with sqlite3.connect(db.db_path) as conn:
        cur = conn.cursor()
        cur.execute("SELECT * FROM Regions "
                    "WHERE RegionType = 'City';")
        assert cur.fetchone() is not None

def test_insert_city_invalid_parent(db):
    assert not db.insert_city("Toronto", -1, 0.0, 0.0)

def test_insert_service(db):
    with sqlite3.connect(db.db_path) as conn:
        cur = conn.cursor()
        cur.execute("SELECT * FROM Services;")
        assert cur.fetchone() is None

    db.insert_region("CA", "Country", None, 0.0, 0.0)
    country_id = db.get_last_inserted_region_id()
    db.insert_service("test", "service", country_id, 0.0, 0.0)

    with sqlite3.connect(db.db_path) as conn:
        cur = conn.cursor()
        cur.execute("SELECT * FROM Services;")
        assert cur.fetchone() is not None

def test_insert_service_invalid_region(db):
    assert not db.insert_service("test", "service", -1, 0.0, 0.0)

def test_find_services(db):
    db.insert_region("CA", "Country", None, 0.0, 0.0)
    country_id = db.get_last_inserted_region_id()
    db.insert_province("ON", country_id, 0.0, 0.0)
    ontario_id = db.get_last_inserted_region_id()
    db.insert_city("Toronto", ontario_id, 0.0, 0.0)
    toronto_id = db.get_last_inserted_region_id()
    db.insert_city("Oshawa", ontario_id, 0.0, 0.0)
    oshawa_id = db.get_last_inserted_region_id()

    db.insert_province("QC", country_id, 0.0, 0.0)
    quebec_id = db.get_last_inserted_region_id()
    db.insert_city("Montreal", quebec_id, 0.0, 0.0)
    montreal_id = db.get_last_inserted_region_id()

    db.insert_service("test", "service", toronto_id, 0.0, 0.0)
    db.insert_service("test2", "service", oshawa_id, 0.0, 0.0)
    db.insert_service("test3", "service", montreal_id, 0.0, 0.0)

    res = db.find_services_in(ontario_id, "service")
    assert len(res) == 2
    assert res[0]["ServiceName"] == "test" or res[0]["ServiceName"] == "test2"
    assert res[1]["ServiceName"] == "test" or res[1]["ServiceName"] == "test2"

def test_find_all_regions(db):
    db.insert_region("CA", "Country", None, 0.0, 0.0)
    country_id = db.get_last_inserted_region_id()
    db.insert_province("ON", country_id, 0.0, 0.0)
    ontario_id = db.get_last_inserted_region_id()
    db.insert_city("Toronto", ontario_id, 0.0, 0.0)
    db.get_last_inserted_region_id()
    db.insert_city("Oshawa", ontario_id, 0.0, 0.0)
    db.get_last_inserted_region_id()

    db.insert_province("QC", country_id, 0.0, 0.0)
    quebec_id = db.get_last_inserted_region_id()
    db.insert_city("Montreal", quebec_id, 0.0, 0.0)
    db.get_last_inserted_region_id()

    res = db.find_all_regions()
    assert len(res) == 6

def test_find_region_by_path(db):
    db.insert_region("CA", "Country", None, 0.0, 0.0)
    country_id = db.get_last_inserted_region_id()
    db.insert_province("ON", country_id, 0.0, 0.0)
    ontario_id = db.get_last_inserted_region_id()
    db.insert_city("Toronto", ontario_id, 0.0, 0.0)
    toronto_id = db.get_last_inserted_region_id()

    res = db.find_region_by_path("CA,ON,Toronto")
    assert res["RegionID"] == toronto_id

def test_find_invalid_region_by_path(db):
    assert db.find_region_by_path("CA,ON,Toronto") == {}

def test_find_region_by_id(db):
    db.insert_region("CA", "Country", None, 0.0, 0.0)
    country_id = db.get_last_inserted_region_id()
    db.insert_province("ON", country_id, 0.0, 0.0)
    ontario_id = db.get_last_inserted_region_id()
    db.insert_city("Toronto", ontario_id, 0.0, 0.0)
    toronto_id = db.get_last_inserted_region_id()

    res = db.find_region_by_id(toronto_id)
    assert res["RegionName"] == "Toronto"

def test_find_invalid_region_by_id(db):
    assert db.find_region_by_id(-1) == {}

def test_remove_region(db):
    db.insert_region("CA", "Country", None, 0.0, 0.0)
    country_id = db.get_last_inserted_region_id()

    db.remove_region(country_id)
    with sqlite3.connect(db.db_path) as conn:
        cur = conn.cursor()
        cur.execute("SELECT * FROM Regions "
                    "WHERE RegionName = 'CA' AND RegionType = 'Country';")
        assert cur.fetchone() is None
