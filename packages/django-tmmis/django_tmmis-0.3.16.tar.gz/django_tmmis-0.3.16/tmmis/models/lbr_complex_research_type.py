from .base_model import *


class LbrComplexResearchType(BaseModel):
    """
    Комплексные исследования
    """

    id = models.AutoField(db_column="ComplexResearchTypeID", primary_key=True)
    guid = models.CharField(db_column="Guid", max_length=36, unique=True)
    research_type = models.ForeignKey(
        "LbrResearchType", db_column="rf_ResearchTypeGuid", to_field="uguid", **FK_DEFAULT
    )
    complex_research_type = models.ForeignKey(
        "LbrComplexResearchType", db_column="rf_ComplexResearchTypeGuid", to_field="guid", **FK_DEFAULT
    )
    flags = models.IntegerField(db_column="Flags")

    class Meta:
        managed = False
        db_table = "lbr_ComplexResearchType"
