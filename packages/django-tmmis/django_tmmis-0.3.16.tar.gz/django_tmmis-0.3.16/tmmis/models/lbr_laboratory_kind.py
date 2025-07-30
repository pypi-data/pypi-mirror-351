from .base_model import *


class LbrLaboratoryKind(BaseModel):
    """
    Вид лаборатории
    """

    id = models.AutoField(db_column="LaboratoryKindID", primary_key=True)
    uguid = models.CharField(db_column="UGUID", max_length=36, unique=True)
    code = models.IntegerField(db_column="Code")
    date_begin = models.DateTimeField(db_column="DateBegin")
    date_end = models.DateTimeField(db_column="DateEnd")
    flags = models.IntegerField(db_column="Flags")
    name = models.CharField(db_column="Name", max_length=200)

    class Meta:
        managed = False
        db_table = "lbr_LaboratoryKind"
