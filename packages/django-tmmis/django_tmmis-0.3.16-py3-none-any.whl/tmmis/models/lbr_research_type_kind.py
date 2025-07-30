from .base_model import *


class LbrResearchTypeKind(BaseModel):
    """
    Вид исследования
    """

    id = models.AutoField(db_column="ResearchTypeKindID", primary_key=True)
    uguid = models.CharField(db_column="UGUID", max_length=36, unique=True)
    code = models.CharField(db_column="Code", max_length=20)
    description = models.CharField(db_column="Description", max_length=8000)
    name = models.CharField(db_column="Name", max_length=200)
    date_begin = models.DateTimeField(db_column="DateBegin")
    date_end = models.DateTimeField(db_column="DateEnd")
    flags = models.IntegerField(db_column="Flags")
    lab_direction_type = models.ForeignKey("LbrLabDirectionType", db_column="rf_LabDirectionTypeID", **FK_DEFAULT)

    class Meta:
        managed = False
        db_table = "lbr_ResearchTypeKind"
