from enum import Enum


class FileAssociate(Enum):
    FORM_PF = "dataSources/WSR/OneTracker.xlsx"
    OCP_TECH = "dataSources/WSR/OneTracker.xlsx"
    ONETRACKER = "dataSources/WSR/OneTracker.xlsx"
    SICAV = "dataSources/WSR/OneTracker.xlsx"
    TREENA = "dataSources/WSR/OneTracker.xlsx"
    BEEQOM = "dataSources/WSR/OneTracker.xlsx"
    CORPORATE_ACTIONS = "dataSources/WSR/OneTracker.xlsx"
    HRIS = "dataSources/WSR/OneTracker.xlsx"
    ICS = "dataSources/WSR/OneTracker.xlsx"
    VEMS = "dataSources/WSR/OneTracker.xlsx"
    WORKDAY = "dataSources/WSR/OneTracker.xlsx"
    FX_CENTRAL = "dataSources/WSR/OneTracker.xlsx"
    MERCATUS = "dataSources/WSR/OneTracker.xlsx"
    QA_SMOKE_TEST = "dataSources/WSR/OneTracker.xlsx"
    
    @staticmethod
    def keys():
        return list(FileAssociate.__members__.keys())

    @staticmethod
    def values():
        return list(FileAssociate.__members__.values())
    
    @classmethod
    def get_value(cls, key):
        return cls[key].value if key in cls.__members__ else None