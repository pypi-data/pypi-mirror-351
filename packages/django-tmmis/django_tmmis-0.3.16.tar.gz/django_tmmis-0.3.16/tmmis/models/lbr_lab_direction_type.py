from .base_model import *


class LbrLabDirectionType(BaseModel):
    """
    Тип направления
    """

    id = models.AutoField(db_column="LabDirectionTypeID", primary_key=True)
    guid = models.CharField(db_column="Guid", unique=True, max_length=36)
    name = models.CharField(db_column="Name", max_length=200)
    code = models.CharField(db_column="Code", max_length=50)
    flags = models.IntegerField(db_column="Flags")

    class Meta:
        managed = False
        db_table = "lbr_LabDirectionType"
