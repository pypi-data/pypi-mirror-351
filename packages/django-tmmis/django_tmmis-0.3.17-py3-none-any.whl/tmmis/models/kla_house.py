from .base_model import *


class KlaHouse(BaseModel):
    id = models.AutoField(db_column="HouseID", primary_key=True)
    code = models.CharField(db_column="CODE", max_length=17)
    number = models.CharField(db_column="Number", max_length=10)
    building = models.CharField(db_column="Building", max_length=10)
    construction = models.CharField(db_column="Construction", max_length=10)
    post_index = models.CharField(db_column="PostIndex", max_length=6)
    street = models.ForeignKey("KlaStreet", models.DO_NOTHING, db_column="rf_StreetID")

    flags = models.IntegerField(db_column="Flags")

    class Meta:
        managed = False
        db_table = "kla_House"
