from .base_model import *


class LbrResearchParamValueType(BaseModel):
    """
    Тип параметра
    """

    id = models.AutoField(db_column="ResearchParamValueTypeID", primary_key=True)
    code = models.IntegerField(db_column="Code")
    enum_name = models.CharField(db_column="EnumName", max_length=50)
    name = models.CharField(db_column="Name", max_length=8000)

    class Meta:
        managed = False
        db_table = "lbr_ResearchParamValueType"
