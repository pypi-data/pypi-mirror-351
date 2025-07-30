from .base_model import *


class LbrOptionValueType(BaseModel):
    """
    Тип данных опции
    """

    id = models.AutoField(db_column="OptionValueTypeID", primary_key=True)
    guid = models.CharField(db_column="Guid", unique=True, max_length=36)
    code = models.CharField(db_column="Code", max_length=50)
    name = models.CharField(db_column="Name", max_length=200)
    enum_name = models.CharField(db_column="EnumName", max_length=50)
    flags = models.IntegerField(db_column="Flags")

    class Meta:
        managed = False
        db_table = "lbr_OptionValueType"
