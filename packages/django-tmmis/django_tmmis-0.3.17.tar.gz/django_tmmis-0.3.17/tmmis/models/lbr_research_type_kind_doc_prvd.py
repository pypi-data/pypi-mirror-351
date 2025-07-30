from .base_model import *


class LbrResearchTypeKindDocPRVD(BaseModel):
    """
    Вид исследования и ресурсы
    """

    id = models.AutoField(db_column="ResearchTypeKindDocPRVDID", primary_key=True)
    uguid = models.CharField(db_column="UGuid", unique=True, max_length=36)
    doc_prvd = models.ForeignKey("HltDocPrvd", db_column="rf_DocPRVDID", **FK_DEFAULT)
    research_type_kind = models.ForeignKey("LbrResearchTypeKind", db_column="rf_ResearchTypeKindID", **FK_DEFAULT)

    class Meta:
        managed = False
        db_table = "lbr_ResearchTypeKindDocPRVD"
