from .base_model import *


class LbrResearchTypeInPack(BaseModel):
    """
    Исследование в составе пакета
    """

    id = models.AutoField(db_column="ResearchTypeInPackID", primary_key=True)
    uguid = models.CharField(db_column="UGUID", max_length=36, unique=True)
    research_type = models.ForeignKey(
        "LbrResearchType", db_column="rf_ResearchTypeGuid", to_field="uguid", **FK_DEFAULT
    )
    flags = models.IntegerField(db_column="Flags")
    laboratory_research_in_pack = models.ForeignKey(
        "LbrLaboratoryResearchInPack", db_column="rf_LaboratoryResearchInPackID", **FK_DEFAULT
    )

    class Meta:
        managed = False
        db_table = "lbr_ResearchTypeInPack"
