from .base_model import *


class KlaKladr(BaseModel):
    id = models.AutoField(db_column="KlAdrID", primary_key=True)
    name = models.CharField(db_column="Name", max_length=40)
    socr = models.CharField(db_column="SOCR", max_length=10)
    code = models.CharField(db_column="CODE", max_length=13)
    gninmb = models.CharField(db_column="GNINMB", max_length=4)
    uno = models.CharField(db_column="UNO", max_length=4)
    ocatd = models.CharField(db_column="OCATD", max_length=11)
    status = models.CharField(db_column="STATUS", max_length=1)
    source = models.CharField(db_column="Source", max_length=5)
    level = models.IntegerField(db_column="LEVEL")
    alt_code = models.CharField(db_column="AltCode", max_length=50)
    post_index = models.CharField(db_column="PostIndex", max_length=6)
    parent = models.ForeignKey("self", models.DO_NOTHING, db_column="rf_ParentID")
    address_string = models.CharField(db_column="AddressString", max_length=500)

    flags = models.IntegerField(db_column="FLAGS")

    class Meta:
        managed = False
        db_table = "kla_Kladr"
