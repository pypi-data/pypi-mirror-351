from .base_model import *


class KlaAddress(BaseModel):
    id = models.AutoField(db_column="AddressID", primary_key=True)
    code = models.CharField(db_column="CODE", max_length=17)
    address_string = models.CharField(db_column="AddressString", max_length=500)
    appartment = models.CharField(db_column="Appartment", max_length=50)
    house = models.ForeignKey("KlaHouse", models.DO_NOTHING, db_column="rf_HouseID")
    area = models.CharField(db_column="Area", max_length=100)
    city = models.CharField(db_column="City", max_length=100)
    dop_data = models.CharField(db_column="DopData", max_length=500)
    region = models.CharField(db_column="Region", max_length=100)
    country = models.IntegerField(db_column="rf_CountryID")
    street = models.CharField(db_column="Street", max_length=100)
    locality = models.CharField(db_column="Locality", max_length=100)
    post_index = models.CharField(db_column="PostIndex", max_length=6)

    flags = models.IntegerField(db_column="Flags")

    class Meta:
        managed = False
        db_table = "kla_Address"
