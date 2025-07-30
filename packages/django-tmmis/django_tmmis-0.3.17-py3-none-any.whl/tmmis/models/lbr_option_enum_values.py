from .base_model import *


class LbrOptionEnumValues(BaseModel):
    """
    Вариант значений опций биоматериала
    """

    id = models.AutoField(db_column="OptionEnumValuesID", primary_key=True)
    guid = models.CharField(db_column="Guid", unique=True, max_length=36)
    value = models.CharField(db_column="Value", max_length=500)
    option = models.ForeignKey("LbrOption", db_column="rf_OptionID", **FK_DEFAULT)
    flags = models.IntegerField(db_column="Flags")

    class Meta:
        managed = False
        db_table = "lbr_OptionEnumValues"
