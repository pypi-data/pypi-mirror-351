from .base_model import *


class LbrResearchTypeToProfile(BaseModel):
    """
    Профиль по типу исследования
    """

    id = models.AutoField(db_column="ResearchTypeToProfileID", primary_key=True)
    uguid = models.CharField(db_column="UGUID", unique=True, max_length=36)
    research_profile_id = models.IntegerField(db_column="rf_kl_ResearchProfileID")
    research_type = models.ForeignKey("LbrResearchType", db_column="rf_ResearchTypeID", **FK_DEFAULT)

    class Meta:
        managed = False
        db_table = "lbr_ResearchTypeToProfile"
