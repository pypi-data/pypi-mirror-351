from .base_model import *


class LbrResearchParamValues(BaseModel):
    """
    Вариант значений параметра
    """

    id = models.AutoField(db_column="ResearchParamValuesID", primary_key=True)
    uguid = models.CharField(db_column="UGUID", max_length=36, unique=True)
    research_type_param = models.ForeignKey(
        "LbrResearchTypeParam", db_column="rf_ResearchTypeParamUGUID", to_field="uguid", **FK_DEFAULT
    )
    value = models.CharField(db_column="Value", max_length=8000)
    date_begin = models.DateTimeField(db_column="DateBegin")
    date_end = models.DateTimeField(db_column="DateEnd")
    code = models.CharField(db_column="Code", max_length=100)

    class Meta:
        managed = False
        db_table = "lbr_ResearchParamValues"
