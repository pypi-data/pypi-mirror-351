from .base_model import *


class OmsKlResearchProfile(BaseModel):
    id = models.AutoField(db_column="kl_ResearchProfileID", primary_key=True)
    guid = models.CharField(db_column="ResearchProfileGuid", unique=True, max_length=36)
    code = models.CharField(db_column="Code", max_length=20)
    name = models.CharField(db_column="Name", max_length=500)
    date_begin = models.DateTimeField(db_column="DateBegin")
    date_end = models.DateTimeField(db_column="DateEnd")
    description = models.CharField(db_column="Description", max_length=500)

    class Meta:
        managed = False
        db_table = "oms_kl_ResearchProfile"
