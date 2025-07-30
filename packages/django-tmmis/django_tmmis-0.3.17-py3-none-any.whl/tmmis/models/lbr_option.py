from .base_model import *


class LbrOption(BaseModel):
    """
    Справочник опций выбора биоматериала
    """

    id = models.AutoField(db_column="OptionID", primary_key=True)
    guid = models.CharField(db_column="GUID", unique=True, max_length=36)
    is_required = models.BooleanField(db_column="IsRequired")
    max = models.IntegerField(db_column="Max")
    min = models.IntegerField(db_column="Min")
    name = models.CharField(db_column="Name", max_length=255)
    unit = models.CharField(db_column="Unit", max_length=100)
    option_value_type = models.ForeignKey("LbrOptionValueType", db_column="rf_OptionValueTypeID", **FK_DEFAULT)

    class Meta:
        managed = False
        db_table = "lbr_Option"
