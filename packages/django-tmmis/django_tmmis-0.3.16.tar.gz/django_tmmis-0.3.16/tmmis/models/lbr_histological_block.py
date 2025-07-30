from .base_model import *


class LbrHistologicalBlock(BaseModel):
    """
    Гистологический блок
    """

    id = models.AutoField(db_column="HistologicalBlockID", primary_key=True)
    guid = models.CharField(db_column="Guid", unique=True, max_length=36)
    number = models.CharField(db_column="Number", max_length=50)
    sample = models.CharField(db_column="Sample", max_length=200)
    in_archive = models.BooleanField(db_column="InArchive")
    research = models.ForeignKey(
        "LbrResearch", db_column="rf_ResearchGUID", to_field="guid", max_length=36, **FK_DEFAULT
    )
    flags = models.IntegerField(db_column="Flags")

    class Meta:
        managed = False
        db_table = "lbr_HistologicalBlock"
