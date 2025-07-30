from .base_model import *


class OmsKlMedCareType(BaseModel):
    id = models.AutoField(db_column="kl_MedCareTypeID", primary_key=True)
    code = models.CharField(db_column="CODE", max_length=50)
    name = models.CharField(db_column="NAME", max_length=255)
    date_b = models.DateTimeField(db_column="Date_B")
    date_e = models.DateTimeField(db_column="Date_E")

    class Meta:
        managed = False
        db_table = "oms_kl_MedCareType"
