# Overview
The Pytest framework was used to ensure the correctness of the backend logic.

## `test_choose.py`
The accuracy of the agent selection service was tested by providing a series of sample statements that the user could input to the chatbot. For the 4 chatbot agents provided (chatbot specialised for autism-related topics; a light discussion chatbot; a chatbot trained to deal with self-harm topics; and a chatbot that provides information about local services for the user) 5 statements were given, and the selection service was tested if it correctly classified the statements to the correct agent.

## `test_db.py`
Basic testing on the location/service database methods to ensure its correctness and data integrity. Each method was tested on an in-memory empty database initialised with the schema, and the method was run individually on  test data to test its functionality.

The data constraints of the regions relation was also tested, to ensure that regions correctly follow a tree-like structure: for example, a unit test ensures the insertion a region of type "Province" must have a parent region ID referring to a region of type "Country", so any region correctly follows a (Country, Province, County, City) path structure. This ensures that we can correctly search by any level of regions within the database for locating local services for the user.

## `test_import_services.py`
The module `import_services` handles the automation of inserting services via csv files, provided by the function `populate_service_database`. The correctness of the module was tested with a small dataset of the services and ensuring that the database follows all data constraints after the function call, such as whether if the inserted data matched the csv data, and if the inserted followed the path structure as described above. 

With the given dataset, 193 services and regions were processed, with 185 successes and 8 failures (failure rate of 4.1451%). The failures occurred due to a problem geocoding the address of the service or region:
 - 6 failed because the geocoder API could not find any locations matching the given address. This most likely occurred due to the address being incorrectly formatted within the csv file itself.
 - 2 failed because the request was refused by the geocoder API (no reason was given).
The total time taken to process all 193 entries was 66.12 seconds, giving an average of 2.92 seconds per entry. Since our complete services dataset has a total of 2935 services, this would take at least 8570.2 seconds to completely process the dataset. However, this is not a large concern as the database is persistent so this will only be run once, and the function is not a user-facing operation—thus the operation can be performed during maintenance or when an update to the existing database is needed.