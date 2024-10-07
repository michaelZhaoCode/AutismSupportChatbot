from api.locationdatabase import LocationDatabase
import sqlite3


class SQLiteLocationDatabase(LocationDatabase):
    """
    Concrete class for storing location-related operations using SQLite.

    This class implements the methods defined in SQLLocationDatabase for managing
    geographic data within an SQLite database.
    """

    def __init__(self, db_name="locations.db"):
        self.db_name = db_name

    def initialize_database(self) -> None:
        """Sets up the SQLite database with required tables and indexes."""
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()

            # Create Regions table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS Regions (
                    RegionID INTEGER PRIMARY KEY AUTOINCREMENT,
                    RegionName TEXT NOT NULL COLLATE NOCASE,
                    RegionType TEXT NOT NULL COLLATE NOCASE,
                    ParentRegionID INTEGER,
                    Latitude REAL NOT NULL,
                    Longitude REAL NOT NULL,
                    FOREIGN KEY (ParentRegionID) REFERENCES Regions (RegionID)
                )
            ''')

            # Create Services table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS Services (
                    ServiceID INTEGER PRIMARY KEY AUTOINCREMENT,
                    ServiceName TEXT NOT NULL,
                    ServiceType TEXT NOT NULL,
                    Latitude REAL NOT NULL,
                    Longitude REAL NOT NULL,
                    RegionID INTEGER NOT NULL,
                    Address TEXT,
                    Phone TEXT,
                    Website TEXT,
                    FOREIGN KEY (RegionID) REFERENCES Regions (RegionID)
                )
            ''')

            # Commit changes
            conn.commit()

            print("Database initialized with Regions and Services tables.")

    def insert_region(self, region: str, region_type: str, parent_id: int, latitude: float, longitude: float) -> None:
        """Inserts a region entry into the SQLite database."""
        try:
            with sqlite3.connect(self.db_name) as conn:
                cursor = conn.cursor()

                # Check if RegionName with the specified RegionType already exists
                cursor.execute("SELECT RegionID FROM Regions WHERE RegionName = ? AND RegionType = ?", (region, region_type))
                if cursor.fetchone():
                    print(f"Error: Region '{region}' with type '{region_type}' already exists.")
                    return

                # Check if ParentRegionID exists if provided
                if parent_id is not None:
                    cursor.execute("SELECT RegionID FROM Regions WHERE RegionID = ?", (parent_id,))
                    if cursor.fetchone() is None:
                        print(f"Error: Parent region with ID '{parent_id}' does not exist.")
                        return

                # Insert the new region
                cursor.execute('''
                    INSERT INTO Regions (RegionName, RegionType, ParentRegionID, Latitude, Longitude)
                    VALUES (?, ?, ?, ?, ?)
                ''', (region, region_type, parent_id, latitude, longitude))

                conn.commit()
                print(f"Region '{region}' of type '{region_type}' inserted successfully.")

        except sqlite3.Error as e:
            print(f"Database error: {e}")
        except Exception as e:
            print(f"An error occurred: {e}")

    def insert_province(self, province: str, country_id: int, latitude: float, longitude: float) -> None:
        """Inserts a province entry into the SQLite database."""
        self.insert_region(province, "Province", country_id, latitude, longitude)

    def insert_city(self, city: str, province_id: int, latitude: float, longitude: float) -> None:
        """Inserts a city entry into the SQLite database."""
        self.insert_region(city, "City", province_id, latitude, longitude)

    def insert_service(self, service: str, service_type: str, region_id: int, latitude: float, longitude: float,
                       address: str = None, phone: str = None, website: str = None) -> None:
        """Inserts a service entry associated with a region into the SQLite database with error checking."""
        try:
            with sqlite3.connect(self.db_name) as conn:
                cursor = conn.cursor()

                # Check if the specified region_id exists in the Regions table
                cursor.execute("SELECT RegionID FROM Regions WHERE RegionID = ?", (region_id,))
                if cursor.fetchone() is None:
                    print(f"Error: Region with ID '{region_id}' does not exist in the database.")
                    return

                # Insert the new service with its associated region and additional information
                cursor.execute('''
                    INSERT INTO Services (ServiceName, ServiceType, Latitude, Longitude, RegionID, Address, Phone, Website)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', (service, service_type, latitude, longitude, region_id, address, phone, website))

                conn.commit()
                print(
                    f"Service '{service}' of type '{service_type}' inserted successfully in region with ID '{region_id}'.")

        except sqlite3.Error as e:
            print(f"Database error: {e}")
        except Exception as e:
            print(f"An error occurred: {e}")

    def find_services_in(self, region_id: int, service_type: str) -> list[dict]:
        """Finds services of a specified type available within a region and its subregions in the SQLite database."""
        try:
            with sqlite3.connect(self.db_name) as conn:
                cursor = conn.cursor()

                # Check if the specified region_id exists in the Regions table
                cursor.execute("SELECT RegionID FROM Regions WHERE RegionID = ?", (region_id,))
                if cursor.fetchone() is None:
                    print(f"Error: Region with ID '{region_id}' does not exist.")
                    return []

                # Initialize list to store all relevant RegionIDs
                region_ids = []

                # Start the recursive search from the specified region
                self._get_all_descendant_regions(region_id, cursor)

                # Prepare query to find all services linked to any of the gathered RegionIDs, filtered by service_type
                query = f'''
                    SELECT *
                    FROM Services 
                    WHERE RegionID IN ({",".join("?" * len(region_ids))}) AND ServiceType = ?
                '''
                params = region_ids + [service_type]

                cursor.execute(query, params)

                # Fetch all services and convert each row to a dictionary
                columns = [column[0] for column in cursor.description]
                services = [dict(zip(columns, row)) for row in cursor.fetchall()]
                return services

        except sqlite3.Error as e:
            print(f"Database error: {e}")
            return []
        except Exception as e:
            print(f"An error occurred: {e}")
            return []

    # Private helper method for retrieving descendants
    def _get_all_descendant_regions(self, region_id: int, cursor) -> list[int]:
        """Retrieves all descendant RegionIDs for a specified region."""
        region_ids = [region_id]
        cursor.execute("SELECT RegionID FROM Regions WHERE ParentRegionID = ?", (region_id,))
        child_regions = cursor.fetchall()
        for child in child_regions:
            region_ids.extend(self._get_all_descendant_regions(child[0], cursor))
        return region_ids

    def find_all_regions(self) -> list[dict]:
        """
        Retrieves all regions stored in the database, replacing ParentRegionID with the actual parent region name and type.

        Returns:
            list[dict]: List of dictionaries, each containing details for a region.
                                  Each dictionary includes RegionID, RegionName, RegionType,
                                  ParentRegionName, ParentRegionType, Latitude, and Longitude.
        """
        regions = []
        try:
            with sqlite3.connect(self.db_name) as conn:
                cursor = conn.cursor()

                # Query to retrieve regions with their ParentRegionID (no join needed)
                cursor.execute('''
                            SELECT RegionID, RegionName, RegionType, ParentRegionID, Latitude, Longitude
                            FROM Regions
                        ''')

                # Fetch results and format them as a list of dictionaries
                rows = cursor.fetchall()
                for row in rows:
                    regions.append({
                        "RegionID": row[0],
                        "RegionName": row[1],
                        "RegionType": row[2],
                        "ParentRegionID": row[3],  # Keeps ParentRegionID as an ID reference
                        "Latitude": row[4],
                        "Longitude": row[5]
                    })

        except sqlite3.Error as e:
            print(f"Database error: {e}")
        except Exception as e:
            print(f"An error occurred: {e}")

        return regions

    def find_region_by_path(self, region_path: str) -> dict:
        """
        Finds and returns a region that matches a specified hierarchical path down to the lowest level.

        This function assumes there is only one matching region per level in the path.
        It interprets each comma-separated item in `region_path` as a level in the hierarchy,
        starting from the top level down through directly related child regions. Each region in the
        path is expected to be directly related to the next, such as "Country,Province,City".

        Args:
            region_path (str): A comma-separated string representing a path of regions (e.g., "Country,Province,City").
                               Each region in the path should be directly related to the next.

        Returns:
            dict: A dictionary with details of the final region if the full path matches.
                  Returns an empty dictionary if the path does not match exactly.
                  The dictionary includes RegionID, RegionName, RegionType, ParentRegionID, Latitude, and Longitude.
        """
        path_elements = region_path.split(",")
        try:
            with sqlite3.connect(self.db_name) as conn:
                cursor = conn.cursor()

                # Initial setup for the traversal through the hierarchy
                parent_id = None

                # Traverse the hierarchy
                for index, region_name in enumerate(path_elements):
                    region_name = region_name.strip()

                    # Perform query depending on whether we're at the top level or within the hierarchy
                    if parent_id is None:
                        cursor.execute('''
                            SELECT RegionID, RegionName, RegionType, ParentRegionID, Latitude, Longitude
                            FROM Regions
                            WHERE RegionName = ? AND ParentRegionID IS NULL
                        ''', (region_name,))
                    else:
                        cursor.execute('''
                            SELECT RegionID, RegionName, RegionType, ParentRegionID, Latitude, Longitude
                            FROM Regions
                            WHERE RegionName = ? AND ParentRegionID = ?
                        ''', (region_name, parent_id))

                    # Fetch the region details
                    region_record = cursor.fetchone()
                    if region_record is None:
                        print(f"No match found for '{region_name}' at level {index + 1}.")
                        return {}  # Return empty if any level is not matched

                    # Set parent_id to the current region's ID for the next level
                    parent_id = region_record[0]

                # Only return the final region if the entire path matched successfully
                return {
                    "RegionID": region_record[0],
                    "RegionName": region_record[1],
                    "RegionType": region_record[2],
                    "ParentRegionID": region_record[3],
                    "Latitude": region_record[4],
                    "Longitude": region_record[5]
                }

        except sqlite3.Error as e:
            print(f"Database error: {e}")
            return {}
        except Exception as e:
            print(f"An error occurred: {e}")
            return {}

    def find_all_services(self) -> list[dict]:
        """
        Retrieves all services stored in the database, including all details from each row in the Services table.

        Returns:
            list[dict]: List of dictionaries, each containing all details for a service,
                        including ServiceID, ServiceName, ServiceType, Latitude, Longitude,
                        RegionID, Address, Phone, and Website.
        """
        services = []
        try:
            with sqlite3.connect(self.db_name) as conn:
                cursor = conn.cursor()

                # Query to retrieve all information from each row in the Services table
                cursor.execute('''
                    SELECT *
                    FROM Services
                ''')

                # Fetch column names and results, then format them as a list of dictionaries
                columns = [column[0] for column in cursor.description]
                rows = cursor.fetchall()
                services = [dict(zip(columns, row)) for row in rows]

        except sqlite3.Error as e:
            print(f"Database error: {e}")
        except Exception as e:
            print(f"An error occurred: {e}")

        return services

    def remove_region(self, region_id: int) -> None:
        """Removes a specific region and its subregions from the SQLite database by region ID."""
        try:
            with sqlite3.connect(self.db_name) as conn:
                cursor = conn.cursor()

                # Check if the region exists
                cursor.execute("SELECT RegionID FROM Regions WHERE RegionID = ?", (region_id,))
                if cursor.fetchone() is None:
                    print(f"Error: Region with ID '{region_id}' does not exist.")
                    return

                # Start the recursive deletion
                self._delete_region_and_descendants(region_id, cursor)
                conn.commit()
                print(f"Region with ID '{region_id}' and all its subregions were removed successfully.")

        except sqlite3.Error as e:
            print(f"Database error: {e}")
        except Exception as e:
            print(f"An error occurred: {e}")

    # Private helper method for deleting a region and its descendants
    def _delete_region_and_descendants(self, region_id: int, cursor) -> None:
        """Deletes a region and all its descendant regions, along with associated services."""
        cursor.execute("DELETE FROM Services WHERE RegionID = ?", (region_id,))
        cursor.execute("SELECT RegionID FROM Regions WHERE ParentRegionID = ?", (region_id,))
        child_regions = cursor.fetchall()
        for child in child_regions:
            self._delete_region_and_descendants(child[0], cursor)
        cursor.execute("DELETE FROM Regions WHERE RegionID = ?", (region_id,))

    def remove_service(self, service_id: int) -> None:
        """Removes a specific service from the SQLite database by service ID."""
        try:
            with sqlite3.connect(self.db_name) as conn:
                cursor = conn.cursor()

                # Check if the service exists
                cursor.execute("SELECT ServiceID FROM Services WHERE ServiceID = ?", (service_id,))
                if cursor.fetchone() is None:
                    print(f"Error: Service with ID '{service_id}' does not exist.")
                    return

                # Delete the service
                cursor.execute("DELETE FROM Services WHERE ServiceID = ?", (service_id,))
                conn.commit()
                print(f"Service with ID '{service_id}' was removed successfully.")

        except sqlite3.Error as e:
            print(f"Database error: {e}")
        except Exception as e:
            print(f"An error occurred: {e}")

    def clear_database(self) -> None:
        """Clears all entries from the SQLite database."""
        try:
            with sqlite3.connect(self.db_name) as conn:
                cursor = conn.cursor()

                # Delete all records from Services and Regions tables
                cursor.execute("DELETE FROM Services")
                cursor.execute("DELETE FROM Regions")

                conn.commit()
                print("All entries in the database were cleared successfully.")

        except sqlite3.Error as e:
            print(f"Database error: {e}")
        except Exception as e:
            print(f"An error occurred: {e}")
