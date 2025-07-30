from .base_model import *


class LbrLaboratoryResearchInPack(BaseModel):
    """
    Направление в составе пакета
    """

    id = models.AutoField(db_column="LaboratoryResearchInPackID", primary_key=True)
    uguid = models.CharField(db_column="UGUID", max_length=36, unique=True)
    pack = models.ForeignKey("LbrLaboratoryResearchPack", db_column="rf_LaboratoryResearchPackID", **FK_DEFAULT)
    laboratory = models.ForeignKey("LbrLaboratory", db_column="rf_LaboratoryID", **FK_DEFAULT)
    lpu = models.ForeignKey("OmsLpu", db_column="rf_LPUID", **FK_DEFAULT)
    research_cause = models.ForeignKey("LbrLabResearchCause", db_column="rf_LabResearchCauseID", **FK_DEFAULT)
    lab_research_target = models.ForeignKey("LbrLabResearchTarget", db_column="rf_LabResearchTargetID", **FK_DEFAULT)
    lab_research_contingent_id = models.IntegerField(db_column="rf_LabResearchContingentID")
    priority = models.BooleanField(db_column="Priority")
    flags = models.IntegerField(db_column="Flags")

    class Meta:
        managed = False
        db_table = "lbr_LaboratoryResearchInPack"
