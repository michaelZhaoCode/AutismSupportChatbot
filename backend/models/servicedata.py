# models/service_data.py

class ServiceData:
    """
    Abstraction over raw service dictionary entries.

    Attributes:
        address (str): Street address of the service provider.
        latitude (float): Latitude coordinate.
        longitude (float): Longitude coordinate.
        phone (str): Contact phone number.
        region_id (int): Region identifier.
        service_id (int): Unique service identifier.
        service_name (str): Name of the service.
        service_type (str): Category of the service.
        website (str): URL of the service.
        distance_km (float or None): Distance from a reference point, if provided.
    """

    def __init__(
        self,
        address,
        latitude,
        longitude,
        phone,
        region_id,
        service_id,
        service_name,
        service_type,
        website,
        distance_km=None
    ):
        self._address = address
        self._latitude = latitude
        self._longitude = longitude
        self._phone = phone
        self._region_id = region_id
        self._service_id = service_id
        self._service_name = service_name
        self._service_type = service_type
        self._website = website
        self._distance_km = distance_km

    @classmethod
    def from_dict(cls, data):
        """
        Create a ServiceData instance from a raw dictionary.
        """
        return cls(
            address=data.get("Address", ""),
            latitude=data.get("Latitude", 0.0),
            longitude=data.get("Longitude", 0.0),
            phone=data.get("Phone", ""),
            region_id=data.get("RegionID", -1),
            service_id=data.get("ServiceID", -1),
            service_name=data.get("ServiceName", ""),
            service_type=data.get("ServiceType", ""),
            website=data.get("Website", ""),
            distance_km=data.get("distance_km")
        )

    @property
    def address(self):
        return self._address

    @property
    def latitude(self):
        return self._latitude

    @property
    def longitude(self):
        return self._longitude

    @property
    def phone(self):
        return self._phone

    @property
    def region_id(self):
        return self._region_id

    @property
    def service_id(self):
        return self._service_id

    @property
    def service_name(self):
        return self._service_name

    @property
    def service_type(self):
        return self._service_type

    @property
    def website(self):
        return self._website

    @property
    def distance_km(self):
        return self._distance_km

    @distance_km.setter
    def distance_km(self, value):
        self._distance_km = value

    @property
    def city(self):
        """
        Extract a city name from the address if possible.
        """
        parts = self._address.split(",")
        return parts[-2].strip() if len(parts) >= 2 else None

    def to_dict(self):
        """
        Convert back to a raw dictionary, including distance_km if present.
        """
        data = {
            "Address": self._address,
            "Latitude": self._latitude,
            "Longitude": self._longitude,
            "Phone": self._phone,
            "RegionID": self._region_id,
            "ServiceID": self._service_id,
            "ServiceName": self._service_name,
            "ServiceType": self._service_type,
            "Website": self._website
        }
        if self._distance_km is not None:
            data["distance_km"] = self._distance_km
        return data

    def __repr__(self):
        return str(self.to_dict())
