from .base_model import *


class LbrResearchTypeParamInPack(BaseModel):
    """
    Параметр в составе пакета
    """

    id = models.AutoField(db_column="ResearchTypeParamInPackID", primary_key=True)
    uguid = models.CharField(db_column="UGUID", max_length=36, unique=True)
    research_type_in_pack = models.ForeignKey(
        "LbrResearchTypeInPack", db_column="rf_ResearchTypeInPackID", **FK_DEFAULT
    )
    research_type_param = models.ForeignKey("LbrResearchTypeParam", db_column="rf_ResearchTypeParamID", **FK_DEFAULT)
    required_param = models.BooleanField(db_column="RequiredParam")
    flags = models.IntegerField(db_column="Flags")

    class Meta:
        managed = False
        db_table = "lbr_ResearchTypeParamInPack"
