from enum import Enum


class EpsgCode(str, Enum):
    EPSG_32632 = "epsg_32632"
    EPSG_32633 = "epsg_32633"
    EPSG_32634 = "epsg_32634"
    EPSG_32635 = "epsg_32635"
    EPSG_32636 = "epsg_32636"
    EPSG_4326 = "epsg_4326"
    EPSG_5972 = "epsg_5972"
    EPSG_5973 = "epsg_5973"
    EPSG_5974 = "epsg_5974"
    EPSG_5975 = "epsg_5975"
    EPSG_5976 = "epsg_5976"

    def __str__(self) -> str:
        return str(self.value)
