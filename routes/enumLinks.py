from enum import Enum


class FileAssociate(Enum):
    FORM_PF = "dataSources/WSR/FORM_PF.xlsx"
    OCP_TECH = None
    ONETRACKER = "dataSources/WSR/ONETRACKER.xlsx"
    SICAV = None
    TREENA = None
    BEQOM = "dataSources/WSR/BEQOM.xlsx"
    CORPORATE_ACTIONS = "dataSources/WSR/CORPORATE_ACTIONS.xlsx"
    HRIS = "dataSources/WSR/HRIS.xlsx"
    ICS = "dataSources/WSR/ICS.xlsx"
    VEMS = "dataSources/WSR/VEMS.xlsx"
    WORKDAY = "dataSources/WSR/WORKDAY.xlsx"
    FX_CENTRAL = None
    MERCATUS = "dataSources/WSR/MERCATUS.xlsx"
    QA_SMOKE_TEST = None
    PIW = "dataSources/WSR/PIW.xlsx"
    PUBLIC_WEBSITE = None
    SUMMIT = None
    QA_MANAGEMENT = None
    CLIENT_RELATIONS = None
    CORNERSTONE = None
    ACCOUNT_MASTER = "dataSources/WSR/ACCOUNT_MASTER.xlsx"


    @staticmethod
    def keys():
        return list(FileAssociate.__members__.keys())

    @staticmethod
    def values():
        return list(FileAssociate.__members__.values())
    
    @classmethod
    def get_value(cls, key):
        return cls[key].value if key in cls.__members__ else None
    

class ChartData(Enum):
    max_width = "100%"
    min_width = "50%"
    height = "75vh"
    background_color = "transparent"
    borderColor="black"
    dataLabels_format_1f="{point.y:.1f}"
    dataLabels_format_0f="{point.y:.0f}"
    dataLabels_format_m0f="$ {point.y:,.0f}"
    lineColor_bar = "#e2725b"
    lineColor_column = "#00416a"
    lineColor_spline = "#e2725b"
    lineColor_spline2 = "#bd1354"
    gridLineWidth = 0
    

def getUserName(current_user):
    return f"{str(current_user.email.split('@')[0]).upper()}"