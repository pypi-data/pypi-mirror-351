from .base_model import *


class LbrLabResearchCause(BaseModel):
    """
    Причина направления
    """

    id = models.AutoField(db_column="LabResearchCauseID", primary_key=True)
    code = models.CharField(db_column="Code", max_length=50)
    name = models.CharField(db_column="Name", max_length=200)
    description = models.CharField(db_column="Description", max_length=250)
    date_begin = models.DateTimeField(db_column="DateBegin")
    date_end = models.DateTimeField(db_column="DateEnd")
    flags = models.IntegerField(db_column="Flags")

    class Meta:
        managed = False
        db_table = "lbr_LabResearchCause"
