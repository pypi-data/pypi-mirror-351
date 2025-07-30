from .base_model import *


class LbrLaboratoryResearchPack(BaseModel):
    """
    Пакет направлений
    """

    id = models.AutoField(db_column="LaboratoryResearchPackID", primary_key=True)
    uguid = models.CharField(db_column="UGUID", max_length=36, unique=True)
    name = models.CharField(db_column="Name", max_length=300)
    prvs = models.ForeignKey("self", db_column="rf_PRVSID", **FK_DEFAULT)
    flags = models.IntegerField(db_column="Flags")
    user = models.ForeignKey("XUser", db_column="rf_UserID", **FK_DEFAULT)

    class Meta:
        managed = False
        db_table = "lbr_LaboratoryResearchPack"
