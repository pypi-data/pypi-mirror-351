from .base_model import *


class OmsKlNomServiceMkbMse(BaseModel):
    id = models.AutoField(db_column="kl_NomServiceMkbMseID", primary_key=True)
    code = models.CharField(db_column="Code", max_length=50)
    is_main = models.BooleanField(db_column="IsMain")
    name = models.CharField(db_column="Name", max_length=1000)
    nom_service_mkb_mse_guid = models.CharField(db_column="NomServiceMkbMseGuid", unique=True, max_length=36)
    nom_service = models.ForeignKey("OmsKlNomService", models.DO_NOTHING, db_column="rf_kl_NomServiceID")
    mkb = models.ForeignKey("OmsMkb", models.DO_NOTHING, db_column="rf_MKBID")
    is_child = models.BooleanField(db_column="IsChild")
    date_begin = models.DateTimeField(db_column="DateBegin")
    date_end = models.DateTimeField(db_column="DateEnd")

    class Meta:
        managed = False
        db_table = "oms_kl_NomServiceMkbMse"
