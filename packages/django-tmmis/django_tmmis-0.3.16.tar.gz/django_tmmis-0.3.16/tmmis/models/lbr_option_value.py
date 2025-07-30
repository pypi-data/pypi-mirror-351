from .base_model import *


class LbrOptionValue(BaseModel):
    """
    Таблица значений опции
    """

    id = models.AutoField(db_column="OptionValueID", primary_key=True)
    guid = models.CharField(db_column="Guid", unique=True, max_length=36)
    option = models.ForeignKey("LbrOption", db_column="rf_OptionID", **FK_DEFAULT)
    sample_id = models.IntegerField(db_column="rf_SampleID")
    value = models.TextField(db_column="Value")
    flags = models.IntegerField(db_column="Flags")

    class Meta:
        managed = False
        db_table = "lbr_OptionValue"
