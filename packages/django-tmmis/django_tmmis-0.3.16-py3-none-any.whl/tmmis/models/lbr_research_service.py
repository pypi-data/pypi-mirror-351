from .base_model import *


class LbrResearchService(BaseModel):
    """
    Услуга исследования
    """

    id = models.AutoField(db_column="ResearchServiceID", primary_key=True)
    flag = models.IntegerField(db_column="Flag")
    guid = models.CharField(db_column="GUID", max_length=36)
    research = models.ForeignKey(
        "LbrResearch", db_column="rf_ResearchGUID", to_field="guid", max_length=36, **FK_DEFAULT
    )
    service_medical = models.ForeignKey("OmsServiceMedical", db_column="rf_ServiceMedicalID", **FK_DEFAULT)

    class Meta:
        managed = False
        db_table = "lbr_ResearchService"
