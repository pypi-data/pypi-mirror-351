from .base_model import *


class LbrResearchTypeParamToResearchType(BaseModel):
    """
    Связь между параметрами и типами исследований
    """

    id = models.AutoField(db_column="ResearchTypeParamToResearchTypeID", primary_key=True)
    uguid = models.CharField(db_column="UGUID", max_length=36, unique=True)
    research_type = models.ForeignKey("LbrResearchType", db_column="rf_ResearchTypeID", **FK_DEFAULT)
    research_type_param = models.ForeignKey("LbrResearchTypeParam", db_column="rf_ResearchTypeParamID", **FK_DEFAULT)
    date_end = models.DateTimeField(db_column="DateEnd")
    date_begin = models.DateTimeField(db_column="DateBegin")
    sort = models.IntegerField(db_column="Sort")

    class Meta:
        managed = False
        db_table = "lbr_ResearchTypeParamToResearchType"
