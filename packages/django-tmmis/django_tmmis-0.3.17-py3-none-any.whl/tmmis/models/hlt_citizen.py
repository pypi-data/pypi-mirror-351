from .base_model import *


class HltCitizen(BaseModel):
    """
    Место жительства
    """

    id = models.AutoField(db_column="CitizenID", primary_key=True)
    uguid = models.CharField(db_column="UGUID", max_length=36)
    cod = models.SmallIntegerField(db_column="COD")
    name = models.CharField(db_column="NAME", max_length=50)
    date_in = models.DateTimeField(db_column="DATEIN")
    date_out = models.DateTimeField(db_column="DATEOUT")
    date_edit = models.DateTimeField(db_column="DateEDIT")

    class Meta:
        managed = False
        db_table = "hlt_Citizen"
