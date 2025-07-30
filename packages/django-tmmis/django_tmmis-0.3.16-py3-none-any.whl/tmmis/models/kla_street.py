from .base_model import *


class KlaStreet(BaseModel):
    id = models.AutoField(db_column="StreetID", primary_key=True)
    socr = models.CharField(db_column="SOCR", max_length=10)
    code = models.CharField(db_column="CODE", max_length=17)
    uno = models.CharField(db_column="UNO", max_length=4)
    ocatd = models.CharField(db_column="OCATD", max_length=11)
    source = models.CharField(db_column="Source", max_length=5)
    alt_code = models.CharField(db_column="AltCode", max_length=50)
    name = models.CharField(db_column="Name", max_length=40)
    gninmb = models.CharField(db_column="GNINMB", max_length=4)
    post_index = models.CharField(db_column="PostIndex", max_length=6)
    kladr = models.ForeignKey("KlaKladr", models.DO_NOTHING, db_column="rf_KlAdrID")
    address_string = models.CharField(db_column="AddressString", max_length=500)

    flags = models.IntegerField(db_column="Flags")

    class Meta:
        managed = False
        db_table = "kla_Street"
