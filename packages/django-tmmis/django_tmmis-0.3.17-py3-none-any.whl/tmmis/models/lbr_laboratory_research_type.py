from .base_model import *


class LbrLaboratoryResearchType(BaseModel):
    """
    Исследования, выполняемые лабораторией
    """

    id = models.AutoField(db_column="LaboratoryResearchTypeID", primary_key=True)
    guid = models.CharField(db_column="GUID", max_length=36, unique=True)
    laboratory = models.ForeignKey("LbrLaboratory", db_column="rf_LaboratoryID", **FK_DEFAULT)
    research_type = models.ForeignKey(
        "LbrResearchType", db_column="rf_ResearchTypeUGUID", to_field="uguid", **FK_DEFAULT
    )
    flags = models.IntegerField(db_column="Flags")

    class Meta:
        managed = False
        db_table = "lbr_LaboratoryResearchType"
