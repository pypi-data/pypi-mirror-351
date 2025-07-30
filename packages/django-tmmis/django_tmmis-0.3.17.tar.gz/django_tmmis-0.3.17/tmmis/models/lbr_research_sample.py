from .base_model import *


class LbrResearchSample(BaseModel):
    """
    Проба
    """

    id = models.AutoField(db_column="ResearchSampleID", primary_key=True)
    uguid = models.CharField(db_column="UGuid", unique=True, max_length=36)
    barcode = models.CharField(db_column="BarCode", max_length=50)
    count = models.DecimalField(db_column="Count", max_digits=10, decimal_places=3)
    date = models.DateTimeField(db_column="Date")
    bio_m_id = models.IntegerField(db_column="rf_BioMID")
    research = models.ForeignKey("LbrResearch", db_column="rf_ResearchID", **FK_DEFAULT)
    doc_prvd = models.ForeignKey("HltDocPrvd", db_column="rf_DocPRVDID", **FK_DEFAULT)
    laboratory_research = models.ForeignKey(
        "LbrLaboratoryResearch", db_column="rf_LaboratoryResearchGUID", to_field="guid", **FK_DEFAULT
    )
    print_labels_count = models.IntegerField(db_column="PrintLabelsCount")

    class Meta:
        managed = False
        db_table = "lbr_ResearchSample"
