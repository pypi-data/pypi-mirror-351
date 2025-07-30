from .base_model import *


class LbrLaboratoryType(BaseModel):
    """
    Тип лаборатории
    """

    id = models.AutoField(db_column="LaboratoryTypeID", primary_key=True)
    uguid = models.CharField(db_column="UGUID", max_length=36, unique=True)
    code = models.CharField(db_column="Code", max_length=20)
    description = models.CharField(db_column="Description", max_length=8000)
    name = models.CharField(db_column="Name", max_length=200)
    flags = models.IntegerField(db_column="Flags")
    date_end = models.DateTimeField(db_column="DateEnd")
    date_begin = models.DateTimeField(db_column="DateBegin")

    class Meta:
        managed = False
        db_table = "lbr_LaboratoryType"
