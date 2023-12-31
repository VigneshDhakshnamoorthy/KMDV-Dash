from enum import Enum


class FileAssociate(Enum):
    FORM_PF = "dataSources/WSR/FORM_PF.xlsx"
    OCP_TECH = None
    ONETRACKER = "dataSources/WSR/ONETRACKER.xlsx"
    SICAV = None
    TREENA = None
    BEEQOM = "dataSources/WSR/BEEQOM.xlsx"
    CORPORATE_ACTIONS = None
    HRIS = None
    ICS = "dataSources/WSR/ICS.xlsx"
    VEMS = "dataSources/WSR/VEMS.xlsx"
    WORKDAY = "dataSources/WSR/WORKDAY.xlsx"
    FX_CENTRAL = None
    MERCATUS = None
    QA_SMOKE_TEST = None
    PIW = None
    PUBLIC_WEBSITE = None
    SUMMIT = None
    QA_MANAGEMENT = None
    CLIENT_RELATIONS = None
    CORNERSTONE = None


    @staticmethod
    def keys():
        return list(FileAssociate.__members__.keys())

    @staticmethod
    def values():
        return list(FileAssociate.__members__.values())
    
    @classmethod
    def get_value(cls, key):
        return cls[key].value if key in cls.__members__ else None