from .base_model import *


class LbrResearchJournal(BaseModel):
    """
    Журнал обследований
    """

    id = models.AutoField(db_column="ResearchJournalID", primary_key=True)
    action_date = models.DateTimeField(db_column="ActionDate")
    comment = models.TextField(db_column="Comment")
    hl7_message = models.TextField(db_column="HL7Message")
    research = models.ForeignKey(
        "LbrResearch", db_column="rf_ResearchGUID", to_field="guid", max_length=36, **FK_DEFAULT
    )
    research_state = models.ForeignKey("LbrResearchState", db_column="rf_ResearchStateID", **FK_DEFAULT)
    laboratory_research = models.ForeignKey("LbrLaboratoryResearch", db_column="rf_LaboratoryResearchID", **FK_DEFAULT)
    client_application_guid = models.CharField(db_column="rf_ClientApplicationGuid", max_length=36)

    class Meta:
        managed = False
        db_table = "lbr_ResearchJournal"
