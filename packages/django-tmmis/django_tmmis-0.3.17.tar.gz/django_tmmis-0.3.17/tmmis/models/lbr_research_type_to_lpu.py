from .base_model import *


class LbrResearchTypeToLpu(BaseModel):
    """
    Справочник проводимых исследований в ЛПУ
    """

    id = models.AutoField(db_column="ResearchTypeToLpuID", primary_key=True)
    uguid = models.CharField(db_column="UGUID", unique=True, max_length=36)
    research_type = models.ForeignKey(
        "LbrResearchType", db_column="rf_ResearchTypeUGUID", to_field="uguid", **FK_DEFAULT
    )
    lpu = models.ForeignKey("OmsLpu", to_field="uuid", db_column="rf_LPUGuid", **FK_DEFAULT)

    class Meta:
        managed = False
        db_table = "lbr_ResearchTypeToLpu"
